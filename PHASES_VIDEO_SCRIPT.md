# Presentation Script: Development & Security Phases Video Demo

**Target Duration**: 3-4 Minutes (approx. 200-240 seconds)
**Style**: Technical walkthrough, developer-centric, demonstrating the implementation of security and pipeline tooling.

---

## Video Outline & Timing Summary

| Segment | Duration | Topic | Screen Visual |
| :--- | :---: | :--- | :--- |
| **1. Intro & Phase 1** | 0:00 - 0:45 (45s) | Video introduction and Phase 1: ADK Workflow Scaffolding. | Diagram of Workflow Graph and **[agent.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/app/agent.py)** code |
| **2. Phase 2: Code Quality** | 0:45 - 1:20 (35s) | Phase 2: Dependency Management and local system Pre-Commit Hooks. | IDE view of **[pyproject.toml](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/pyproject.toml)** and **[.pre-commit-config.yaml](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/.pre-commit-config.yaml)** |
| **3. Phase 3: Security & AST** | 1:20 - 2:10 (50s) | Phase 3: Gemini input pre-screening and the Custom AST Security Scanner. | VS Code view of **[classifier.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/app/classifier.py)** and **[semgrep_wrapper.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/scripts/semgrep_wrapper.py)** |
| **4. Phase 4: STRIDE & Hooks** | 2:10 - 2:45 (35s) | Phase 4: STRIDE Threat Model Assessment and PreToolUse hooks. | Scroll of **[threat_model.md](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/threat_model.md)** and hook script **[validate_tool_call.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/agents/scripts/validate_tool_call.py)** |
| **5. Phase 5: Verification & Push** | 2:45 - 3:30 (45s) | Phase 5: Testing, running pre-commit checks, and git push. | Terminal output running `pytest`, `pre-commit`, and `git push` |

---

## Detailed Script & Storyboard

### Segment 1: Intro & Phase 1 - Workflow Scaffolding (0:00 - 0:45)
* **Visual**: IDE displaying `app/agent.py`. Highlight the `Workflow` initialization and nodes.
* **Audio (Voiceover)**:
  > *"Welcome! In this demo, we're tracing the complete development and security phases of the Florida IT Opportunities Agent.*
  >
  > *Phase 1 was all about scaffolding and establishing our graph architecture. We initialized our ADK project using Google's Agent CLI, creating a modular pipeline workflow. As you can see in **[agent.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/app/agent.py)**, the graph links a search discovery node, an enricher/classifier processor node, and a router node. This structures our flow into a highly manageable state machine."*

---

### Segment 2: Phase 2 - Dependency Gating & Pre-Commit (0:45 - 1:20)
* **Visual**: Show `pyproject.toml` dependencies, then switch to `.pre-commit-config.yaml`.
* **Audio (Voiceover)**:
  > *"Next, in Phase 2, we unified our dependency management under **[pyproject.toml](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/pyproject.toml)** and configured formatting and linting gates.*
  >
  > *To run automated pre-commit gating on Windows without path length or checkout errors, we set up **[.pre-commit-config.yaml](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/.pre-commit-config.yaml)** with local system hooks that invoke Python formatting modules directly in our virtual environment, guaranteeing code health checks before commits."*

---

### Segment 3: Phase 3 - Secure AI Agent & Custom AST Scanner (1:20 - 2:10)
* **Visual**: VS Code showing `app/classifier.py` security rules inside the Gemini prompt. Then switch to `scripts/semgrep_wrapper.py` and show AST visitor classes.
* **Audio (Voiceover)**:
  > *"Phase 3 is the security core of our agent. External web data is inherently untrusted. To mitigate prompt injections, our Gemini classifier prompt in **[classifier.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/app/classifier.py)** instructs the model to detect and isolate hijack attempts. Any threat triggers `security_risk_detected=True` to flag the lead database record.*
  >
  > *Additionally, we created **[semgrep_wrapper.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/scripts/semgrep_wrapper.py)**. Since installing full Semgrep binaries can be complex on Windows, this script parses python Abstract Syntax Trees locally to check for code execution (`eval`/`exec`), shell executions, and hardcoded Google API credentials."*

---

### Segment 4: Phase 4 - STRIDE Modeling & Pre-Tool Hooks (2:10 - 2:45)
* **Visual**: Scroll through the `threat_model.md` STRIDE table, then show `agents/scripts/validate_tool_call.py`.
* **Audio (Voiceover)**:
  > *"In Phase 4, we conducted a systematic security threat assessment. In **[threat_model.md](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/threat_model.md)**, we evaluated our boundaries against Spoofing, Tampering, Information Disclosure, and Denial of Service.*
  >
  > *To prevent the agent from executing dangerous shell commands during development, we configured a `PreToolUse` hook running **[validate_tool_call.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/agents/scripts/validate_tool_call.py)**, intercepting all CLI commands to assert command safety."*

---

### Segment 5: Phase 5 - Verification & Deploy to GitHub (2:45 - 3:30)
* **Visual**: Switch to the terminal. Run `uv run pytest`, then commit changes showing pre-commit hooks passing, and finally push to GitHub.
* **Audio (Voiceover)**:
  > *"Finally, in Phase 5, we validated and deployed our project. We run unit and integration tests in **[test_agent_security.py](file:///C:/Users/ocres/OneDrive/Desktop/TI/Projects/florida-it-opportunities/florida-it-agent/fl-it-opportunities-agent/tests/test_agent_security.py)** to verify database writes and safety boundaries. All tests pass.*
  >
  > *When we execute `git commit`, our local pre-commit hooks—including the trailing whitespace trimmer, EOF fixer, and Semgrep security scan—execute successfully. With our gates clean, we push to GitHub, completing a secure, automated development lifecycle. Thanks for watching!"*
