# Presentation Script: Florida IT Opportunities Pipeline Video Demo
**Target Duration**: 5 Minutes (300 seconds)
**Style**: Clear, concise, and high-impact messaging.

---

## Video Outline & Timing Summary

| Segment | Duration | Topic | Screen Visual |
| :--- | :---: | :--- | :--- |
| **1. Problem Statement** | 0:00 - 0:45 (45s) | Manual lead research pain points and why solving it is important. | Streamlit App Landing Page or Title Slide |
| **2. Why Agents? & Architecture** | 0:45 - 1:45 (60s) | Unique benefits of agents and visual walk-through of the ADK StateGraph. | GitHub-themed Mermaid Node Diagram / IDE Graph code |
| **3. The Build (Tools & Tech)** | 1:45 - 3:00 (75s) | Technology stack (ADK, Gemini 2.5 Flash, PostgreSQL, Streamlit) & security. | VS Code view of `classifier.py` and `database.py` |
| **4. Live Demo** | 3:00 - 4:30 (90s) | Walk-through of database initialization, live execution, and lead filtering. | Live Streamlit interface executing a query run |
| **5. Conclusion & BI Views** | 4:30 - 5:00 (30s) | Connecting to Power BI and repository final wrap-up. | Power BI view view SQL / GitHub Repository |

---

## Detailed Script & Storyboard

### Segment 1: Problem Statement (0:00 - 0:45)
* **Visual**: Streamlit dashboard header: "🌴 Florida IT Opportunities Pipeline". Mouse hovers over search config.
* **Audio (Voiceover)**:
  > *"Hi everyone! Identifying qualified business leads for B2B IT service agencies is historically a tedious, manual chore. Sales teams waste hours searching Google, scanning websites, diagnosing security issues like missing HTTPS, and estimating staff sizes just to determine if a lead has IT budget.*
  >
  > *This is an important and interesting problem because local business websites are highly unstructured. Some are modern, some are legacy sites built over a decade ago, and others are completely broken. Automating this discovery and profiling lifecycle transforms unstructured regional web data into high-value structured sales targets, saving hours of manual prospecting."*

---

### Segment 2: Why Agents? & Architecture (0:45 - 1:45)
* **Visual**: Show the Mermaid architecture diagram styled with dark-theme colors. Zoom in on nodes.
* **Audio (Voiceover)**:
  > *"So, why use AI agents? Traditional APIs or simple scripts are fragile. They break when a site layout changes, fail to adapt to varying industries, and struggle to coordinate multi-step flows.*
  >
  > *Agents are uniquely suited here because they reason. They handle open-ended search queries, dynamically parse scraped web content, inspect security states, and route decisions conditionally. *
  >
  > *Here is our agentic architecture built on Google's ADK Workflow engine. The **Lead Discovery Node** queries the Google Places API. The **Business Processor Node** acts as a scraper and AI evaluator, feeding each candidate to Gemini to perform multi-dimensional classification. Lastly, the **Router Node** dynamically controls the workflow loop, determining whether to continue processing or exit. All qualified data is stored in our relational PostgreSQL database."*

---

### Segment 3: The Build: Tools & Technology (1:45 - 3:00)
* **Visual**: Switch to VS Code. Show `app/classifier.py` Pydantic model (`ITOpportunityClassification`) and `app/agent.py` security rules.
* **Audio (Voiceover)**:
  > *"Let's talk about the build. We built this pipeline using **Google's Agent Development Kit (ADK)** for agent state orchestration, and the **Google GenAI SDK** to interface with **Gemini 2.5 Flash**.*
  >
  > *We enforce strict data contracts by passing Pydantic models directly to Gemini. This guarantees the model outputs structured JSON containing business size, website status, IT pain points, recommended services, and an opportunity score from 1 to 10.*
  >
  > *For storage, we used **PostgreSQL** linked via `psycopg2`. For safety, the build features built-in security pre-screening on search inputs and scraped web pages to block prompt injection payloads. Finally, we engineered a robust Offline Fallback Mode, enabling full local testing with mocked scraping and rule-based classification."*

---

### Segment 4: Live Demo (3:00 - 4:30)
* **Visual**: Back to the browser. Click **Test Conn** (shows success), then click **Init DB** (shows success). Type a query in the text area and click **Proceed & Run**. Show the progress logs scrolling in real time.
* **Audio (Voiceover)**:
  > *"Now for the live demo. On the Streamlit sidebar, I can check my database connection and initialize the tables and Power BI views with one click. Let's run a live pipeline query for dentists in Miami and lawyers in Tampa.*
  >
  > *A launch confirmation screen verifies our active search parameters and API configurations. Once we proceed, the agent begins execution. The logs show the active Google Places query, real-time website crawling, and Gemini classification. *
  >
  > *Within seconds, our Lead Explorer populates. We can filter leads dynamically by Lead Tier, size, or query, instantly updating our KPI cards. A built-in download button lets us export this target list directly to CSV."*

---

### Segment 5: Conclusion & BI Views (4:30 - 5:00)
* **Visual**: Show `v_lead_scoring` database view. Transition to the GitHub repository page.
* **Audio (Voiceover)**:
  > *"To make this data highly actionable for business intelligence, we expose a custom view called `v_lead_scoring`. You can connect Microsoft Power BI directly to this PostgreSQL view for deep analytical reporting.*
  >
  > *The code is fully open-sourced on GitHub. You can follow the setup instructions in the README to deploy it in minutes. Thanks for watching, and feel free to check out the repository!"*

---

## 💡 Quick Tips for Recording
1. **Pacing**: Speak clearly and naturally. Maintain a steady pace to keep the video concise and easily finish within the 5-minute limit.
2. **Readability**: Zoom in on your IDE and Streamlit browser window to make the code and text clearly readable on standard video players.
3. **Smooth Transitions**: Transition smoothly from slides/architecture diagrams to code, and then to the live browser dashboard.
