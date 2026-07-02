import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def clean_string_for_postgres(val):
    """Recursively removes NUL (0x00) characters from string inputs to prevent Postgres errors."""
    if isinstance(val, str):
        return val.replace("\x00", "").replace("\u0000", "")
    elif isinstance(val, list):
        return [clean_string_for_postgres(item) for item in val]
    elif isinstance(val, dict):
        return {k: clean_string_for_postgres(v) for k, v in val.items()}
    return val


def get_db_connection():
    """Establishes a connection to the PostgreSQL database using environment variables."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "florida_it_opportunities"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def init_db():
    """Initializes the database schema by executing schema.sql."""
    # Find the schema.sql file path
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema.sql")
    if not os.path.exists(schema_path):
        print(f"Warning: schema.sql not found at {schema_path}")
        return False

    with open(schema_path, encoding="utf-8") as f:
        schema_sql = f.read()

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
        print("Database schema initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def upsert_business(conn, business_data):
    """
    Upserts a business entry in the database.
    Returns the internal business ID.
    """
    business_data = clean_string_for_postgres(business_data)
    query = """
    INSERT INTO businesses (place_id, name, phone, address, website_url, rating, user_ratings_total, search_query)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (place_id) DO UPDATE SET
        name = EXCLUDED.name,
        phone = EXCLUDED.phone,
        address = EXCLUDED.address,
        website_url = EXCLUDED.website_url,
        rating = EXCLUDED.rating,
        user_ratings_total = EXCLUDED.user_ratings_total,
        search_query = EXCLUDED.search_query
    RETURNING id;
    """
    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                business_data["place_id"],
                business_data["name"],
                business_data.get("phone"),
                business_data.get("address"),
                business_data.get("website_url"),
                business_data.get("rating"),
                business_data.get("user_ratings_total"),
                business_data.get("search_query"),
            ),
        )
        result = cur.fetchone()
        return result[0] if result else None


def upsert_website_enrichment(conn, business_id, scrape_data):
    """Upserts website enrichment details for a business."""
    scrape_data = clean_string_for_postgres(scrape_data)
    query = """
    INSERT INTO website_enrichment (business_id, scraped_title, meta_description, scraped_text, http_status)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (business_id) DO UPDATE SET
        scraped_title = EXCLUDED.scraped_title,
        meta_description = EXCLUDED.meta_description,
        scraped_text = EXCLUDED.scraped_text,
        http_status = EXCLUDED.http_status,
        scraped_at = CURRENT_TIMESTAMP;
    """
    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                business_id,
                scrape_data.get("scraped_title"),
                scrape_data.get("meta_description"),
                scrape_data.get("scraped_text"),
                scrape_data.get("http_status"),
            ),
        )


def upsert_it_opportunities(conn, business_id, classification_data):
    """Upserts Gemini classification and IT opportunity details for a business."""
    classification_data = clean_string_for_postgres(classification_data)
    query = """
    INSERT INTO it_opportunities (
        business_id, business_size, business_size_reasoning, website_status,
        it_pain_points, pitchable_services, opportunity_score, lead_tier, sales_reasoning,
        category, online_presence, security_risk_detected, security_risk_summary
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (business_id) DO UPDATE SET
        business_size = EXCLUDED.business_size,
        business_size_reasoning = EXCLUDED.business_size_reasoning,
        website_status = EXCLUDED.website_status,
        it_pain_points = EXCLUDED.it_pain_points,
        pitchable_services = EXCLUDED.pitchable_services,
        opportunity_score = EXCLUDED.opportunity_score,
        lead_tier = EXCLUDED.lead_tier,
        sales_reasoning = EXCLUDED.sales_reasoning,
        category = EXCLUDED.category,
        online_presence = EXCLUDED.online_presence,
        security_risk_detected = EXCLUDED.security_risk_detected,
        security_risk_summary = EXCLUDED.security_risk_summary,
        analyzed_at = CURRENT_TIMESTAMP;
    """
    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                business_id,
                classification_data.get("business_size"),
                classification_data.get("business_size_reasoning"),
                classification_data.get("website_status"),
                classification_data.get("it_pain_points"),
                classification_data.get("pitchable_services"),
                classification_data.get("opportunity_score"),
                classification_data.get("lead_tier"),
                classification_data.get("sales_reasoning"),
                classification_data.get("category"),
                classification_data.get("online_presence"),
                classification_data.get("security_risk_detected", False),
                classification_data.get("security_risk_summary", ""),
            ),
        )


def fetch_all_leads():
    """Fetches all leads from the unified lead scoring view."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM v_lead_scoring ORDER BY opportunity_score DESC, google_reviews_count DESC;"
            )
            colnames = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(colnames, row, strict=False)) for row in rows]
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return []
    finally:
        conn.close()
