import asyncio
import json
import os
import sys

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Ensure the app folder is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.runners import InMemoryRunner
from google.genai import types

from app import database as db
from app.agent import app as adk_app

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Florida IT Opportunities Dashboard",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Premium Aesthetics
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
    }
    .metric-title {
        font-size: 14px;
        color: #6c757d;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #212529;
    }
    .lead-high {
        color: #dc3545;
        font-weight: bold;
    }
    .lead-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .lead-low {
        color: #28a745;
        font-weight: bold;
    }
    .st-key-stop_pipeline button {
        background-color: #dc3545 !important;
        color: white !important;
        border-color: #dc3545 !important;
    }
    .st-key-stop_pipeline button:hover {
        background-color: #bd2130 !important;
        color: white !important;
        border-color: #b21f2d !important;
    }
    .st-key-stop_pipeline button:active {
        background-color: #b21f2d !important;
        color: white !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "run_completed" not in st.session_state:
    st.session_state.run_completed = False
if "tier_filter" not in st.session_state:
    st.session_state.tier_filter = "All"
if "size_filter" not in st.session_state:
    st.session_state.size_filter = "All"
if "query_filter" not in st.session_state:
    st.session_state.query_filter = "All"
if "current_queries" not in st.session_state:
    st.session_state.current_queries = []
if "active_task" not in st.session_state:
    st.session_state.active_task = None
if "test_conn_result" not in st.session_state:
    st.session_state.test_conn_result = None
if "init_db_result" not in st.session_state:
    st.session_state.init_db_result = None
if "selected_biz_name" not in st.session_state:
    st.session_state.selected_biz_name = None
if "in_memory_leads" not in st.session_state:
    st.session_state.in_memory_leads = []
if "db_connection_failed" not in st.session_state:
    st.session_state.db_connection_failed = False

is_running = st.session_state.active_task is not None

# Execute connection test task
if st.session_state.get("active_task") == "test_conn":
    try:
        conn = db.get_db_connection()
        conn.close()
        st.session_state.test_conn_result = ("success", "Connection OK!")
    except Exception as e:
        st.session_state.test_conn_result = ("error", f"Failed: {e}")
    st.session_state.active_task = None
    st.rerun()

# Execute DB initialization task
if st.session_state.get("active_task") == "init_db":
    if db.init_db():
        st.session_state.init_db_result = (
            "success",
            "✅ DB Initialized Successfully! Tables and Views are ready.",
        )
    else:
        st.session_state.init_db_result = (
            "error",
            "❌ Database Initialization Failed. Check logs or connection parameters.",
        )
    st.session_state.active_task = None
    st.rerun()

# App Title
st.title("🌴 Florida IT Opportunities Pipeline")
st.markdown(
    "Automate lead discovery via Google Places, website scraping/analysis, and Gemini opportunity scoring."
)

# Run Button
run_pipeline = st.button(
    "🚀 Run ADK 2.0 Graph Pipeline",
    use_container_width=True,
    disabled=is_running,
    key="run_pipeline",
)

# Placeholder container for logs
log_placeholder = st.container()

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
st.sidebar.subheader("🚀 Pipeline Settings")
default_queries = "dentists in Miami, FL\nlawyers in Tampa, FL"
queries_input = st.sidebar.text_area(
    "Search Queries (one per line)", value=default_queries, height=100
)

st.sidebar.markdown("---")

# Read API keys from env
gemini_key = os.getenv("GEMINI_API_KEY", "")
places_key = os.getenv("GOOGLE_PLACES_API_KEY", "")

# PostgreSQL DB settings
st.sidebar.subheader("🗄️ PostgreSQL Database")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "florida_it_opportunities")

col_db1, col_db2 = st.sidebar.columns(2)
with col_db1:
    if st.sidebar.button("Test Conn", disabled=is_running):
        st.session_state.test_conn_result = None
        st.session_state.init_db_result = None
        st.session_state.active_task = "test_conn"
        st.rerun()
with col_db2:
    if st.sidebar.button("Init DB", disabled=is_running):
        st.session_state.test_conn_result = None
        st.session_state.init_db_result = None
        st.session_state.confirm_init_db = True
        st.rerun()

test_conn_result = st.session_state.get("test_conn_result")
if isinstance(test_conn_result, tuple):
    status, msg = test_conn_result
    if status == "success":
        st.sidebar.success(msg)
    else:
        st.sidebar.error(msg)

init_db_result = st.session_state.get("init_db_result")
if isinstance(init_db_result, tuple):
    status, msg = init_db_result
    if status == "success":
        st.sidebar.success(msg)
    else:
        st.sidebar.error(msg)

# Load data if completed
try:
    if st.session_state.get("run_completed", False):
        try:
            db_leads = db.fetch_all_leads()
            if not db_leads and st.session_state.get("in_memory_leads"):
                df_leads = pd.DataFrame(st.session_state.in_memory_leads)
                st.session_state.db_connection_failed = True
            else:
                df_leads = pd.DataFrame(db_leads)
                st.session_state.db_connection_failed = False
        except Exception as db_err:
            print(f"[Database Error] Failed to fetch leads: {db_err}")
            st.session_state.db_connection_failed = True
            df_leads = pd.DataFrame(st.session_state.get("in_memory_leads", []))

        if (
            not df_leads.empty
            and "search_query" in df_leads.columns
            and st.session_state.get("current_queries")
        ):
            df_leads = df_leads[
                df_leads["search_query"].isin(st.session_state.current_queries)
            ]

        if not df_leads.empty:
            string_cols = [
                "category",
                "online_presence",
                "scraped_title",
                "meta_description",
                "scraped_text",
                "sales_reasoning",
                "business_size_reasoning",
                "phone",
                "address",
                "website_url",
            ]
            for col in string_cols:
                if col in df_leads.columns:
                    df_leads[col] = df_leads[col].fillna("N/A")
    else:
        df_leads = pd.DataFrame()
except Exception:
    df_leads = pd.DataFrame()

# DB init confirmation panel
if st.session_state.get("confirm_init_db", False):
    st.warning("⚠️ **Confirm PostgreSQL Schema Initialization**")
    st.markdown(f"""
    You are about to initialize the PostgreSQL database schema for **`{db_name}`** at `{db_host}:{db_port}`.
    *Note: Tables are created using `IF NOT EXISTS`, so existing lead records will not be overwritten.*
    """)
    col_d1, col_d2 = st.columns([2, 5])
    with col_d1:
        if st.button("🚀 Proceed & Init DB", type="primary"):
            st.session_state.confirm_init_db = False
            st.session_state.active_task = "init_db"
            st.rerun()
    with col_d2:
        if st.button("❌ Cancel DB Init"):
            st.session_state.confirm_init_db = False
            st.rerun()

# Run confirmation panel
if run_pipeline:
    st.session_state.test_conn_result = None
    st.session_state.init_db_result = None
    st.session_state.confirm_run = True
    st.session_state.execute_pipeline = False
    st.session_state.selected_biz_name = None

if st.session_state.get("confirm_run", False):
    queries = [q.strip() for q in queries_input.split("\n") if q.strip()]
    if not queries:
        st.error("Please provide at least one search query.")
        st.session_state.confirm_run = False
    else:
        st.warning("⚠️ **Confirm ADK 2.0 Pipeline Launch**")
        st.markdown(f"""
        You are about to start the Florida IT Opportunities workflow.
        *   **Search Google Places** for: {", ".join([f"`{q}`" for q in queries])}
        *   **Scrape & Enrich** homepages
        *   **Analyze & Score** with Gemini
        *   **Save Results** to PostgreSQL database `{db_name}`

        API Status:
        - **Gemini API:** {"🟢 Live" if gemini_key else "🟡 Offline Fallback"}
        - **Places API:** {"🟢 Live" if places_key else "🟡 Offline Fallback"}
        """)
        col_c1, col_c2 = st.columns([1, 6])
        with col_c1:
            if st.button("🚀 Proceed & Run", type="primary"):
                st.session_state.confirm_run = False
                st.session_state.current_queries = queries
                st.session_state.active_task = "pipeline"
                st.session_state.run_completed = False
                st.session_state.in_memory_leads = []
                st.session_state.db_connection_failed = False
                st.session_state.tier_filter = "All"
                st.session_state.size_filter = "All"
                st.session_state.query_filter = "All"
                st.session_state.selected_biz_name = None
                st.rerun()
        with col_c2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_run = False
                st.rerun()

# Dashboard UI
if not df_leads.empty:
    metrics_placeholder = st.container()
    tier_col = "lead_tier"
    size_col = "business_size"
    score_col = "opportunity_score"

    if st.session_state.get("db_connection_failed", False):
        st.warning(
            "⚠️ **Database Connection Failed**: Displaying in-memory results from the pipeline run."
        )

    st.subheader("🔎 Lead Explorer")
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        tiers_list = ["All", *list(df_leads[tier_col].unique())]
        default_index = 0
        if st.session_state.tier_filter in tiers_list:
            default_index = tiers_list.index(st.session_state.tier_filter)
        selected_tier = st.selectbox(
            "Filter by Lead Tier", tiers_list, index=default_index
        )
        st.session_state.tier_filter = selected_tier

    with filter_col2:
        sizes_list = ["All", *list(df_leads[size_col].unique())]
        default_index = 0
        if st.session_state.size_filter in sizes_list:
            default_index = sizes_list.index(st.session_state.size_filter)
        selected_size = st.selectbox(
            "Filter by Business Size", sizes_list, index=default_index
        )
        st.session_state.size_filter = selected_size

    with filter_col3:
        queries_list = ["All", *list(df_leads["search_query"].unique())]
        default_index = 0
        if st.session_state.query_filter in queries_list:
            default_index = queries_list.index(st.session_state.query_filter)
        selected_query = st.selectbox(
            "Filter by Search Query", queries_list, index=default_index
        )
        st.session_state.query_filter = selected_query

    filtered_df = df_leads.copy()
    if selected_tier != "All":
        filtered_df = filtered_df[filtered_df[tier_col] == selected_tier]
    if selected_size != "All":
        filtered_df = filtered_df[filtered_df[size_col] == selected_size]
    if selected_query != "All":
        filtered_df = filtered_df[filtered_df["search_query"] == selected_query]

    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1

    with metrics_placeholder:
        if st.session_state.get("current_queries"):
            queries_str = ", ".join(st.session_state.current_queries)
            st.markdown(f"#### 🔎 Search Queries: {queries_str}")
        st.subheader("📊 Key Lead Performance Indicators")
        col1, col2, col3, col4, col5 = st.columns(5)

        total_leads = len(filtered_df)
        high_leads = len(filtered_df[filtered_df[tier_col] == "High"])
        large_biz = len(filtered_df[filtered_df[size_col] == "Large"])
        med_biz = len(filtered_df[filtered_df[size_col] == "Medium"])
        small_biz = len(filtered_df[filtered_df[size_col] == "Small"])

        with col1:
            st.markdown(
                f"""<div class="metric-card"><div class="metric-title">Total Leads</div><div class="metric-value">{total_leads}</div></div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""<div class="metric-card" style="border-left-color: #dc3545;"><div class="metric-title">🔥 High Priority</div><div class="metric-value">{high_leads}</div></div>""",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""<div class="metric-card" style="border-left-color: #0d6efd;"><div class="metric-title">🏢 Large Sized</div><div class="metric-value">{large_biz}</div></div>""",
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"""<div class="metric-card" style="border-left-color: #6c757d;"><div class="metric-title">🏢 Medium Sized</div><div class="metric-value">{med_biz}</div></div>""",
                unsafe_allow_html=True,
            )
        with col5:
            st.markdown(
                f"""<div class="metric-card" style="border-left-color: #28a745;"><div class="metric-title">🏪 Small Sized</div><div class="metric-value">{small_biz}</div></div>""",
                unsafe_allow_html=True,
            )

        st.markdown("---")
        sum_col1, sum_col2 = st.columns(2)

        all_pain_points = []
        if "it_pain_points" in filtered_df.columns:
            for pts in filtered_df["it_pain_points"].dropna():
                if isinstance(pts, list):
                    all_pain_points.extend([p.strip() for p in pts if p.strip()])

        all_services = []
        if "pitchable_services" in filtered_df.columns:
            for svcs in filtered_df["pitchable_services"].dropna():
                if isinstance(svcs, list):
                    all_services.extend([s.strip() for s in svcs if s.strip()])

        from collections import Counter

        with sum_col1:
            st.markdown("### 🚨 Top 10 IT Pain Points Identified")
            if all_pain_points:
                pain_counts = Counter(all_pain_points).most_common(10)
                for i, (pain, count) in enumerate(pain_counts, 1):
                    st.markdown(
                        f"**{i}. {pain}** ({count} lead{'s' if count > 1 else ''})"
                    )
            else:
                st.info("No pain points identified.")

        with sum_col2:
            st.markdown("### 🛠️ Top 10 Recommended Services to Pitch")
            if all_services:
                service_counts = Counter(all_services).most_common(10)
                for i, (svc, count) in enumerate(service_counts, 1):
                    st.markdown(
                        f"**{i}. {svc}** ({count} lead{'s' if count > 1 else ''})"
                    )
            else:
                st.info("No recommended services.")
        st.markdown("---")

    display_cols = [
        "name",
        "category",
        size_col,
        "website_url",
        score_col,
        tier_col,
        "sales_reasoning",
        "phone",
        "address",
    ]
    display_cols = [c for c in display_cols if c in filtered_df.columns]

    selection = st.dataframe(
        filtered_df[display_cols].style.map(
            lambda val: (
                "background-color: #f8d7da; color: #721c24;"
                if val == "High"
                else (
                    "background-color: #fff3cd; color: #856404;"
                    if val == "Medium"
                    else (
                        "background-color: #d4edda; color: #155724;"
                        if val == "Low"
                        else ""
                    )
                )
            ),
            subset=[tier_col] if tier_col in display_cols else [],
        ),
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    try:
        selected_rows = selection.selection.rows
        if selected_rows:
            row_idx = selected_rows[0]
            st.session_state.selected_biz_name = filtered_df.iloc[row_idx]["name"]
    except Exception:
        pass

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Lead Table as CSV (for Power BI)",
        data=csv_data,
        file_name="florida_it_opportunities_leads.csv",
        mime="text/csv",
    )

    st.subheader("🕵️ Business Deep Dive & Website Scrapes")
    unique_biz = list(filtered_df["name"].unique())
    default_idx = 0
    if st.session_state.get("selected_biz_name") in unique_biz:
        default_idx = unique_biz.index(st.session_state.selected_biz_name)

    selected_business_name = st.selectbox(
        "Select a business to view detailed analysis", unique_biz, index=default_idx
    )
    st.session_state.selected_biz_name = selected_business_name

    if selected_business_name:
        biz_detail = filtered_df[filtered_df["name"] == selected_business_name].iloc[0]

        detail_col1, detail_col2 = st.columns(2)
        with detail_col1:
            st.markdown(f"### 🏢 {biz_detail['name']}")
            if biz_detail.get("security_risk_detected"):
                st.error(
                    f"🚨 **Security Warning:** {biz_detail.get('security_risk_summary', 'Suspicious content or prompt injection detected and neutralized.')}"
                )

            st.write(f"🏷️ **Category:** {biz_detail.get('category', 'N/A')}")
            st.write(f"📞 **Phone:** {biz_detail.get('phone', 'N/A')}")
            st.write(f"📍 **Address:** {biz_detail.get('address', 'N/A')}")
            st.write(f"🌐 **Website:** {biz_detail.get('website_url', 'N/A')}")
            st.write(
                f"📶 **Online Presence:** {biz_detail.get('online_presence', 'N/A')}"
            )
            st.write(
                f"📈 **Google Rating:** {biz_detail.get('google_rating', biz_detail.get('rating', 'N/A'))} ({int(biz_detail.get('google_reviews_count', biz_detail.get('user_ratings_total', 0)))} reviews)"
            )
            st.write(
                f"🏢 **Estimated Size:** {biz_detail[size_col]} ({biz_detail.get('business_size_reasoning', 'N/A')})"
            )

            st.markdown("---")
            st.markdown("#### 🎯 AI Opportunity Assessment")
            st.markdown(
                f"**Lead Tier:** `{biz_detail[tier_col]}` (Score: `{biz_detail[score_col]}/10`)"
            )
            st.markdown(
                f"**Sales Pitch Reasoning:** *{biz_detail.get('sales_reasoning', 'N/A')}*"
            )

            pain_points = biz_detail.get("it_pain_points", [])
            services = biz_detail.get("pitchable_services", [])

            st.markdown("##### 🚨 IT Pain Points Identified")
            if pain_points:
                for pt in pain_points:
                    st.write(f"⚠️ {pt}")
            else:
                st.write("None identified.")

            st.markdown("##### 🛠️ Recommended Services to Pitch")
            if services:
                for svc in services:
                    st.write(f"✅ {svc}")
            else:
                st.write("None.")

        with detail_col2:
            st.markdown("#### 📄 Web Scrape Details")
            st.write(f"**Scraped Title:** `{biz_detail.get('scraped_title', 'N/A')}`")
            st.write(
                f"**HTTP Status:** `{biz_detail.get('scrape_http_status', biz_detail.get('http_status', 'N/A'))}`"
            )
            st.write(
                f"**Meta Description:** *{biz_detail.get('meta_description', 'N/A')}*"
            )
            st.text_area(
                "Cleaned Page Text Content (first 1000 chars)",
                value=biz_detail.get("scraped_text", "N/A")[:1000],
                height=300,
            )
else:
    st.info(
        "💡 Run the pipeline from the button at the top to populate lead data, or verify PostgreSQL connection in the sidebar."
    )

# Run pipeline execution task
if st.session_state.get("active_task") == "pipeline":
    queries = st.session_state.get("current_queries", [])

    with log_placeholder:
        st.subheader("⚙️ ADK 2.0 Graph Workflow Live Logs")
        if st.button(
            "🛑 Stop / Interrupt Pipeline",
            use_container_width=True,
            key="stop_pipeline",
        ):
            st.warning("Pipeline execution stopped by user.")
            st.session_state.active_task = None
            st.rerun()

        log_container = st.empty()
        progress_bar = st.progress(0)

    logs = ["🚀 Instantiating ADK 2.0 InMemoryRunner..."]
    log_container.text("\n".join(logs))

    async def run_adk_workflow():
        runner = InMemoryRunner(app=adk_app)
        session = await runner.session_service.create_session(
            app_name="app", user_id="streamlit_user"
        )

        # Pass queries to workflow input schema
        input_data = {"queries": queries}

        discovered_count = 0

        async for event in runner.run_async(
            user_id="streamlit_user",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part.from_text(text=json.dumps(input_data))]
            ),
        ):
            if (
                event.node_name == "search_businesses_node"
                and event.actions.state_delta
            ):
                businesses = event.actions.state_delta.get("businesses", [])
                discovered_count = len(businesses)
                logs.append(
                    f"🔍 [Search Node] Discovered {discovered_count} businesses from Google Places."
                )
                log_container.text("\n".join(logs))
                progress_bar.progress(0.1)

            elif (
                event.node_name == "process_business_node" and event.actions.state_delta
            ):
                idx = event.actions.state_delta.get("current_index", 0)
                processed_list = event.actions.state_delta.get("processed_results", [])
                st.session_state.in_memory_leads = processed_list

                if processed_list:
                    latest = processed_list[-1]
                    logs.append(
                        f"⚙️ [Process Node] ({idx}/{discovered_count}) {latest['name']} "
                        f"| Size: {latest['business_size']} "
                        f"| Website: {latest['website_status']} "
                        f"| Score: {latest['opportunity_score']}/10 ({latest['lead_tier']} Lead)"
                    )
                    log_container.text("\n".join(logs))

                    pct = 0.1 + (idx / max(1, discovered_count)) * 0.9
                    progress_bar.progress(min(pct, 1.0))

        logs.append("✅ ADK 2.0 Graph Workflow completed successfully!")
        log_container.text("\n".join(logs))
        progress_bar.progress(1.0)
        st.session_state.run_completed = True
        st.session_state.active_task = None

    try:
        asyncio.run(run_adk_workflow())
        st.rerun()
    except Exception as pipeline_err:
        with log_placeholder:
            st.error(f"Error executing ADK pipeline: {pipeline_err}")
        st.session_state.active_task = None

# Power BI guide
st.markdown("---")
with st.expander("📊 How to Connect PostgreSQL to Power BI"):
    st.markdown("""
    ### Option 1: Direct Database Connection (Recommended)
    1. Open **Power BI Desktop**.
    2. Click **Get Data** -> **PostgreSQL database**.
    3. Enter the server details:
       - **Server:** `localhost` (or database host IP)
       - **Database:** `florida_it_opportunities`
    4. Choose **DirectQuery** or **Import**.
    5. Enter database credentials:
       - **Username:** `postgres`
       - **Password:** `postgres`
    6. Select the view `v_lead_scoring` to build reports.

    ### Option 2: Fallback CSV Import
    1. Click the **📥 Download Lead Table as CSV** button above to save `florida_it_opportunities_leads.csv`.
    2. Open **Power BI Desktop**.
    3. Click **Get Data** -> **Text/CSV** and select the downloaded file.
    """)
