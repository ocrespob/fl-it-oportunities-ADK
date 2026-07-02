# fl-it-oportunities-ADK

## What is this project?

🌴 **Florida IT Opportunities Pipeline**  
An agentic lead qualification pipeline built with Google's Agent Development Kit (ADK) that discovers, scrapes, and classifies IT opportunities for Florida businesses.

The pipeline discovery workflow integrates with a local PostgreSQL database and is optimized to connect directly with Microsoft Power BI for deep business intelligence analysis.

```
fl-it-opportunities-agent/
├── app/                      # Core agent logic, classifier, scraper, and DB helpers
│   ├── agent.py              # Main agent workflow graph and nodes
│   ├── classifier.py         # Gemini IT opportunity classification
│   ├── database.py           # PostgreSQL CRUD operations
│   ├── fast_api_app.py       # FastAPI backend server
│   ├── places_search.py      # Google Places API integration
│   └── scraper.py            # Website crawler and content extractor
├── tests/                    # Unit and integration test suites
├── schema.sql                # PostgreSQL database schema & Power BI reporting view
├── pyproject.toml            # Project dependencies and configs
└── AGENTS.md                 # Agent-assisted coding guidelines
```

---

## Why was it created?

Identifying and qualifying high-potential IT service leads is historically a tedious, manual chore. Sales teams spend hours searching Google, scanning websites, estimating company sizes, diagnosing outdated sites, and determining technical needs. 

This project was created to automate the entire process:
1. **Automated Search**: Programmatically queries Google Places API to find regional businesses.
2. **Context Enrichment**: Scrapes each target's website to gather title, meta description, and page body.
3. **AI-Driven Assessment**: Uses the **Gemini LLM** to estimate business scale, categorize business types, pinpoint IT pain points, recommend pitchable services, and assign a structured `Opportunity Score` (1-10) and `Lead Tier`.
4. **Interactive Dashboarding**: Stores all insights in a structured PostgreSQL database exposed via a clean SQL view (`v_lead_scoring`) designed to directly power Microsoft Power BI reports.

---

## How do I install it?

### Prerequisites
Make sure you have the following installed on your system:
* **Python 3.11+**
* **uv**: Modern, fast Python package manager. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
* **PostgreSQL**: Local or remote database server instance running.

### 1. Scaffold & Setup Agent CLI
Install the agent tool globally using `uv`:
```bash
uv tool install google-agents-cli
```

### 2. Clone and Install Dependencies
Navigate to the project directory and run the install command to configure the virtual environment and fetch packages:
```bash
agents-cli install
```

### 3. Database Setup
Create a PostgreSQL database named `florida_it_opportunities`. Execute the database schema script to initialize tables and the unified reporting view:
```bash
psql -U postgres -d florida_it_opportunities -f schema.sql
```

### 4. Configuration
Create a `.env` file at the root of the project (copying from `.env.example`) and fill in your API credentials and database connection details:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

DB_HOST=localhost
DB_PORT=5432
DB_NAME=florida_it_opportunities
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
```

---

## How do I use it?

### 1. Launch local development playground
Run the interactive playground to test query inputs and review agent outputs directly from a browser interface:
```bash
agents-cli playground
```

### 2. Run unit and integration tests
To verify project integrity, execute:
```bash
uv run pytest tests/unit tests/integration
```

### 3. Run the Streamlit Web Application
To run the Streamlit frontend web app in your browser:
```bash
uv run streamlit run app.py
```

### 4. Run FastAPI Backend
To launch the FastAPI server hosting the agent REST endpoints:
```bash
uv run uvicorn app.fast_api_app:app --reload
```

### 5. Run Evaluation Loops
To run agent evaluations against test datasets:
```bash
agents-cli eval generate
agents-cli eval grade
```

---

## Who created it?

* **Oscar Crespo**
  * **Email**: [ocrespob@gmail.com](mailto:ocrespob@gmail.com)
  * **GitHub**: [@ocrespob](https://github.com/ocrespob)

---

## How can others contribute?

Contributions are welcome and highly appreciated! To contribute:

1. **Fork the Repository** on GitHub.
2. **Create a Feature Branch** (`git checkout -b feature/amazing-feature`).
3. **Commit Your Changes** following the [Conventional Commits](https://www.conventionalcommits.org/) specification:
   * Example: `feat(scraper): add support for parsing javascript-heavy sites`
   * Use type options such as `feat`, `fix`, `docs`, `refactor`, `chore`, or `test`.
4. **Run Code Quality Checks**:
   ```bash
   agents-cli lint
   ```
5. **Open a Pull Request** explaining your enhancements or bug fixes.
