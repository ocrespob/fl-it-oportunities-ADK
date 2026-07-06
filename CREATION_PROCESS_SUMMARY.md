# Florida IT Opportunities Agent: Creation & Implementation Summary

This document provides a comprehensive summary of the process followed to build, secure, validate, and deploy the **Florida IT Opportunities Agent (`fl-it-opportunities-agent`)** using Google’s Agent Development Kit (ADK 2.0).

---

## 📌 1. Project Scaffolding & Architecture Setup

The project was initialized using the `agents-cli` tool to scaffold the standard ADK structure:
```bash
agents-cli scaffold create fl-it-opportunities-agent
```

### Core Architecture Components:
* **[agent.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/app/agent.py)**: Configures the ADK `Workflow` state machine. It comprises three nodes connected sequentially in an execution loop:
  1. `search_businesses_node`: Discovers regional business leads in Florida using the **Google Places API** (falls back to mock data if offline).
  2. `process_business_node`: Crawls homepages using `httpx` + `BeautifulSoup`, feeds text content to **Gemini 2.5 Flash** for lead qualification/scoring, and saves outcomes to PostgreSQL.
  3. `route_next_business`: Directs the graph to process the next lead index or exit the workflow.
* **[app.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/app.py)**: A Streamlit Dashboard interface that exposes:
  * Database connection tests and database initialization controls.
  * Real-time workflow logging output.
  * Lead filtering parameters (Tier, Size, Score) and a CSV exporter.

---

## 🛠️ 2. Dependency Management & Automated Linting

* **Dependency Migration**: Runtime and development packages were migrated from `requirements.txt` to a modern, unified dependency management system in **[pyproject.toml](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/pyproject.toml)** and locked via `uv.lock`.
* **Pre-commit Quality Hooks**:
  * Configured local git hooks in **[.pre-commit-config.yaml](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/.pre-commit-config.yaml)**.
  * *Windows Workaround*: To bypass Windows `MAX_PATH` path length limitations (which caused errors during remote repository checkouts of standard pre-commit hook packages), hooks were configured as local `system` hooks executing Python modules directly (e.g., `python -m pre_commit_hooks.end_of_file_fixer`).

---

## 🛡️ 3. Security-First AI Agent Guardrails

To harden the LLM against malicious external payloads (such as prompt injections on scanned business websites), the following layers of defense were added:

1. **Untrusted Payload Guardrails**:
   * Scraped website body content is treated as untrusted data.
   * In **[classifier.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/app/classifier.py)**, the Gemini 2.5 system prompt contains strict rules commanding the model to ignore system-altering requests (e.g., *"ignore previous instructions"*, *"reveal system prompt"*).
   * If a threat is detected, Gemini sets `security_risk_detected=True`, populates the `security_risk_summary`, and completes the business analysis safely without executing the injection payload.
2. **AST-Based Windows-Compatible Security Scanner**:
   * A custom python Abstract Syntax Tree (AST) checker was created at **[semgrep_wrapper.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/scripts/semgrep_wrapper.py)** with matching constraints defined in **[rules.yaml](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/semgrep/rules.yaml)**.
   * This parses project Python files to detect:
     * Code execution functions (`eval()` and `exec()`).
     * Vulnerable shell calls (`subprocess` with `shell=True`).
     * Hardcoded secrets/credentials and Google API key prefixes starting with `AIzaSy`.
   * On non-Windows platforms, the wrapper automatically delegates to the real `semgrep` binary.

---

## 📐 4. Threat Modeling & Defensive Hooks

* **STRIDE Threat Model Assessment**: Compiled a systematic threat modeling document at **[threat_model.md](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/threat_model.md)** to analyze system boundaries, trace vulnerabilities, and plan mitigations across the STRIDE pillars.
* **Pre-Tool Hook**: Created a pre-tool execution hook validator in **[validate_tool_call.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/agents/scripts/validate_tool_call.py)** and integrated it via `.agents/hooks.json` to intercept command executions and verify tool parameters.

---

## 🧪 5. Testing, Verification, & GitHub Deployment

1. **Safety Testing**: Unit and integration tests in **[test_agent_security.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/tests/test_agent_security.py)** were established to verify code health, test database transactions, and confirm that prompt injections are successfully caught and isolated.
2. **Commit & Push**:
   * Pre-commit hooks were run and verified locally:
     ```bash
     uv run git commit -m "chore: migrate to pyproject.toml, configure pre-commit hooks, and implement agent security tools"
     ```
   * Successfully pushed changes to the remote branch:
     ```bash
     git push origin main
     ```
     * **Repository**: `ocrespob/fl-it-oportunities-ADK`
     * **Branch**: `main`
     * **Commit SHA**: `9f7be07db1de6767c65d6275b483d0129ffd441e`
     * **Kaggle Write-Up**: Completed and saved in **[KAGGLE_WRITEUP.md](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/KAGGLE_WRITEUP.md)**.
