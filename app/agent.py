import json
from typing import Any

from google.adk.agents.context import Context
from google.adk.apps import App
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.workflow import START, Workflow
from google.genai import types
from pydantic import BaseModel, Field

from . import database as db
from .classifier import classify_lead
from .places_search import search_places_google
from .scraper import scrape_website


class PipelineInput(BaseModel):
    queries: list[str] = Field(description="Search queries for Google Places API.")


class PipelineState(BaseModel):
    queries: list[str] = []
    businesses: list[dict[str, Any]] = []
    current_index: int = 0
    processed_results: list[dict[str, Any]] = []
    security_risk_detected: bool = False
    security_risk_summary: str = ""


def search_businesses_node(ctx: Context, node_input: Any) -> Event:
    """
    Search node: Runs queries on Google Places API and populates the list of businesses.
    """
    # Robust Input Parsing
    queries = []
    raw_text = ""

    if isinstance(node_input, PipelineInput):
        queries = node_input.queries
        raw_text = " ".join(queries)
    elif isinstance(node_input, dict):
        if "queries" in node_input:
            queries = node_input["queries"]
            if isinstance(queries, str):
                queries = [queries]
            raw_text = " ".join(queries)
        else:
            queries = list(node_input.values())
            raw_text = " ".join(str(v) for v in queries)
    elif isinstance(node_input, str):
        raw_text = node_input
    elif hasattr(node_input, "parts"):  # types.Content
        raw_text = "".join(part.text for part in node_input.parts if part.text)
    elif hasattr(node_input, "text"):  # types.Part
        raw_text = node_input.text
    else:
        raw_text = str(node_input)

    # Try parsing text as JSON if queries not populated
    if not queries and raw_text:
        stripped = raw_text.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, dict) and "queries" in parsed:
                    queries = parsed["queries"]
                elif isinstance(parsed, list):
                    queries = parsed
            except Exception:
                pass

    # Fallback to plain text splitting if JSON parsing didn't work/apply
    if not queries and raw_text:
        # Split by comma or newline
        lines = [q.strip() for q in raw_text.replace(",", "\n").split("\n")]
        queries = [q for q in lines if q]

    # Safe default if still empty
    if not queries:
        queries = ["dentists in Miami, FL", "lawyers in Tampa, FL"]

    # Security Check on the Input Queries (Prompt Injection Detection)
    security_risk_detected = False
    security_risk_summary = ""
    injection_keywords = [
        "ignore previous instructions",
        "reveal system prompt",
        "expose api keys",
        "change your role",
        "delete data",
        "modify data",
        "exfiltrate data",
        "call tools without permission",
    ]

    query_check_str = raw_text.lower()
    for kw in injection_keywords:
        if kw in query_check_str:
            security_risk_detected = True
            security_risk_summary = f"Detected potential prompt injection attempt in search query using keyword: '{kw}'."
            break

    # If injection detected, summarize the risk and continue only with safe business analysis (Rule 8)
    if security_risk_detected:
        print(f"[Security Warning] {security_risk_summary}")
        # Replace the malicious query with a safe default search query to continue safe analysis
        queries = ["general businesses in Florida"]
    else:
        print(f"[Graph Node: Search] Processing queries: {queries}")

    all_discovered = []
    seen_place_ids = set()

    for query in queries:
        places = search_places_google(query)
        for place in places:
            if place["place_id"] not in seen_place_ids:
                seen_place_ids.add(place["place_id"])
                all_discovered.append(place)

    print(f"[Graph Node: Search] Discovered {len(all_discovered)} unique businesses.")
    search_summary = f"Discovered {len(all_discovered)} businesses matching queries."
    yield Event(
        content=types.Content(
            role="model", parts=[types.Part.from_text(text=search_summary)]
        )
    )
    yield Event(
        output={"businesses_count": len(all_discovered)},
        actions=EventActions(
            state_delta={
                "businesses": all_discovered,
                "queries": queries,
                "current_index": 0,
                "processed_results": [],
                "security_risk_detected": security_risk_detected,
                "security_risk_summary": security_risk_summary,
            }
        ),
    )


def process_business_node(ctx: Context, node_input: Any) -> Event:
    """
    Business processor node: Scrapes the website, runs Gemini classification, and saves to PostgreSQL.
    """
    businesses = ctx.state.get("businesses", [])
    idx = ctx.state.get("current_index", 0)
    processed = ctx.state.get("processed_results", [])

    if idx >= len(businesses):
        return Event(output={}, actions=EventActions(route="exit"))

    business = businesses[idx]
    business_name = business["name"]
    website_url = business.get("website_url")
    review_count = business.get("user_ratings_total") or 0

    print(
        f"\n--- [Graph Node: Process] ({idx + 1}/{len(businesses)}) {business_name} ---"
    )

    # 1. Scrape Website
    scrape_data = scrape_website(website_url)

    # 2. Run Gemini (or Mock) IT Classification & Business Size Estimation
    scraped_text = scrape_data.get("scraped_text", "")
    http_status = scrape_data.get("http_status", 200)
    classification = classify_lead(
        business_name, website_url, review_count, scraped_text, http_status
    )

    # Create unified result dictionary
    full_result = {
        **business,
        "scraped_title": scrape_data.get("scraped_title"),
        "meta_description": scrape_data.get("meta_description"),
        "scraped_text": scraped_text,
        "http_status": scrape_data.get("http_status"),
        **classification,
    }

    # 3. Save to PostgreSQL
    try:
        conn = db.get_db_connection()
        try:
            # Insert business first to get internal serial ID
            business_id = db.upsert_business(conn, business)

            # Insert website enrichment
            db.upsert_website_enrichment(conn, business_id, scrape_data)

            # Insert IT opportunities and sizing
            db.upsert_it_opportunities(conn, business_id, classification)

            conn.commit()
            print(
                f"[Database] Successfully saved '{business_name}' to PostgreSQL (ID: {business_id})."
            )
        except Exception as db_err:
            conn.rollback()
            print(f"[Database Warning] Error saving business transaction: {db_err}")
        finally:
            conn.close()
    except Exception as conn_err:
        print(
            f"[Database Warning] Could not connect to PostgreSQL: {conn_err}. Skipping database save."
        )

    # Append to state accumulator
    new_processed = list(processed)
    new_processed.append(full_result)

    summary_text = (
        f"Processed business: {business_name}\n"
        f"Estimated Size: {full_result['business_size']}\n"
        f"Website Status: {full_result['website_status']}\n"
        f"Category: {full_result['category']}\n"
        f"Lead Tier: {full_result['lead_tier']} (Score: {full_result['opportunity_score']}/10)"
    )
    if full_result.get("security_risk_detected"):
        summary_text += (
            f"\n⚠️ Security Risk Warning: {full_result['security_risk_summary']}"
        )

    yield Event(
        content=types.Content(
            role="model", parts=[types.Part.from_text(text=summary_text)]
        )
    )
    yield Event(
        output=full_result,
        actions=EventActions(
            state_delta={"processed_results": new_processed, "current_index": idx + 1}
        ),
    )


def route_next_business(ctx: Context, node_input: Any) -> Event:
    """
    Router function: Determines if there are more businesses to process.
    """
    businesses = ctx.state.get("businesses", [])
    idx = ctx.state.get("current_index", 0)

    if idx < len(businesses):
        print(f"[Graph Router] Continuing to next business index: {idx}")
        return Event(output=node_input, actions=EventActions(route="continue"))
    else:
        print("[Graph Router] All businesses processed. Ending workflow.")
        return Event(output=node_input, actions=EventActions(route="exit"))


root_agent = Workflow(
    name="pipeline_workflow",
    state_schema=PipelineState,
    edges=[
        (START, search_businesses_node),
        (search_businesses_node, process_business_node),
        (process_business_node, route_next_business),
        (route_next_business, {"continue": process_business_node}),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
