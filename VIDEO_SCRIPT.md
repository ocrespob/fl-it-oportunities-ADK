# Presentation Script: Florida IT Opportunities Pipeline Video Demo
**Target Duration**: 5 Minutes (300 seconds)
**Style**: Engaging developer walkthrough, clear and professional tone.

---

## Video Outline & Timing Summary

| Segment | Duration | Topic | Screen Visual |
| :--- | :---: | :--- | :--- |
| **1. Hook & Intro** | 0:00 - 0:45 (45s) | The B2B lead discovery problem & introduction of the solution. | Streamlit App Landing Page / Title Slide |
| **2. Architecture** | 0:45 - 1:45 (60s) | ADK graph orchestration flow & nodes. | Mermaid Diagram / Code layout in IDE |
| **3. Core Features** | 1:45 - 3:00 (75s) | Gemini structured output, security rules, and offline modes. | `classifier.py` Pydantic models & prompt injection checks |
| **4. Live App Demo** | 3:00 - 4:30 (90s) | Live dashboard run, DB initialization, filtering, and export. | Live Streamlit browser interface in action |
| **5. BI & Wrap Up** | 4:30 - 5:00 (30s) | Power BI integration, GitHub links, and conclusion. | Power BI view schema / GitHub Repository |

---

## Detailed Script & Storyboard

### Segment 1: Hook & Introduction (0:00 - 0:45)
* **Visual**: Streamlit dashboard header: "🌴 Florida IT Opportunities Pipeline". The mouse hovers over the sidebar configuration.
* **Audio (Voiceover)**:
  > *"Hi everyone! If you’ve ever worked in B2B sales or managed IT services, you know that finding qualified local business leads is a massive bottleneck. Sales teams spend hours manually searching Google, clicking through outdated websites, estimating company sizes, checking for security certificates, and trying to draft the perfect cold pitch.*
  >
  > *Today, I’m excited to show you the **Florida IT Opportunities Pipeline**—an agentic lead qualification system built on Google’s Agent Development Kit (ADK) and powered by Gemini 2.5 Flash that automates this entire discovery and profiling process in seconds."*

---

### Segment 2: System Architecture & Workflow (0:45 - 1:45)
* **Visual**: Show the Mermaid architecture diagram (ideally the one styled with GitHub dark theme colors). Zoom in slightly on the nodes as they are mentioned.
* **Audio (Voiceover)**:
  > *"Let's take a look at how it works under the hood. The pipeline is modeled as an agentic state-machine workflow executing a graph-based loop using the Google ADK engine.*
  >
  > *First, we enter our search queries. The **Lead Discovery Node** connects to the Google Places API to find regional businesses matching terms like 'dentists in Miami' or 'lawyers in Tampa'.*
  >
  > *Second, for each discovered lead, the **Business Processor Node** steps in to crawl the business website homepage, scrape its title and text, and feed it into Gemini to classify and score the IT opportunity.*
  >
  > *Finally, the **Router Node** decides whether to continue processing the next business in line or exit cleanly when the queue is empty. All qualified data is stored in our PostgreSQL database."*

---

### Segment 3: Core AI & Security Features (1:45 - 3:00)
* **Visual**: Open VS Code or your IDE. Show the Pydantic schema `ITOpportunityClassification` in `app/classifier.py` and scroll down to the prompt-injection keywords check.
* **Audio (Voiceover)**:
  > *"Three core engineering features make this pipeline incredibly resilient:*
  >
  > *First, we leverage **Gemini's Structured Outputs**. By passing a Pydantic schema to Gemini 2.5 Flash, the model is guaranteed to return perfectly formatted JSON containing the business size, website status, identified IT pain points, recommended services, and an opportunity score from 1 to 10.*
  >
  > *Second, we implement **Security Guardrails**. Web scrapers are vulnerable to prompt injections hidden in external website text. We pre-screen search terms and instruct the Gemini model to ignore commands found on crawled pages, capturing any suspicious attempts in a dedicated security flag.*
  >
  > *Third, we built a robust **Offline Fallback Mode**. If API keys are missing or rate limits are reached, the system automatically uses mock scrapers and rule-based classifiers, letting developers prototype locally without consuming active credits."*

---

### Segment 4: Live Dashboard Demo (3:00 - 4:30)
* **Visual**: Back to the browser. Click **Test Conn** (shows success), then click **Init DB** (shows success). Type a query in the text area and click **Proceed & Run**. Show the logs scrolling in real time as nodes process.
* **Audio (Voiceover)**:
  > *"Let's see it in action. On the Streamlit control panel, I'll first test my database connection. With a single click, I can initialize the PostgreSQL schema. Let's run a pipeline search for regional Florida businesses.*
  >
  > *We get a launch prompt confirming our settings and API statuses. Once we proceed, you can watch the agent run in real time. The logs show the active web scraping, followed by Gemini’s classification outputs.*
  >
  > *As the runs complete, the Lead Explorer loads the results. We can use dynamic filters to isolate leads by Lead Tier, size, or industry category, instantly updating our KPI metrics. We can also export this qualified list to a CSV with a single click."*

---

### Segment 5: Power BI Integration & Wrap Up (4:30 - 5:00)
* **Visual**: Show the custom database view `v_lead_scoring` in code, or a quick screen of a Power BI import window. Then transition to the GitHub repository page.
* **Audio (Voiceover)**:
  > *"To make this data actionable, the database exposes a pre-joined PostgreSQL view called `v_lead_scoring`. You can connect Power BI directly to this view to build interactive executive dashboards.*
  >
  > *The code is fully open-source and available on GitHub. You can follow the setup instructions in the README to run it locally using Python `uv` or standard virtual environments.*
  >
  > *Thanks for watching! Feel free to review the Kaggle Writeup for a deeper dive into the system's performance and security threat models."*

---

## 💡 Quick Tips for Recording
1. **Show, Don't Just Tell**: Whenever you talk about a feature, make sure the screen displays the corresponding file or UI element.
2. **Clear Font Size**: Zoom in on your IDE and browser (to about 125%–150%) so viewers can easily read the code and UI texts.
3. **Pace Yourself**: Keep a steady, confident pace. Use pauses between transitions to keep it under the 5-minute mark.
