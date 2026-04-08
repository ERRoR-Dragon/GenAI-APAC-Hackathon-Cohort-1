# 🏡 ReloScope — AI-Powered Relocation & Urban Intelligence Advisor

## What is ReloScope?
ReloScope is a highly sophisticated, multi-agent artificial intelligence system designed to revolutionize urban relocation and property research in India. By simultaneously acting as a data scientist, real estate analyst, and itinerary planner, ReloScope takes a user's target cities or neighborhoods and automatically researches them across dozens of vectors—including environmental safety, livability density, investment sentiment, and commute viability. It replaces endless hours of manual research with conversational, actionable intelligence, complete with autonomously generated documentation.

## 🤖 The Multi-Agent Architecture & Sub-Agents Deep Dive
ReloScope orchestrates a complex symphony of autonomous actors. It is built on the **Google Agent Development Kit (ADK)** using a state-of-the-art hierarchical multi-agent workflow. Every individual sub-agent has a highly specific persona, strict computational boundaries, and access to a uniquely tailored set of tools. 

Here is what happens behind the scenes when a user submits a query:

- **`root_agent` (The ReloScope Master Orchestrator)**: The core brain of the operation. It interprets the semantic intent of user queries, manages conversation state, routes task flows intelligently, and handles error recovery. It holds the "keys" to the sub-agents and dynamically decides whether a query requires a simple factual answer or a massive multi-city programmatic analysis.
- **`greeter_agent`**: Your friendly host. It introduces the system's capabilities, guides new users on how to query the platform properly, and acts as the front-door concierge.
- **`tour_agent` (The Logistics Specialist)**: A dedicated logistics planner. When a user asks to visit locations, this agent mathematically computes exact driving commutes between custom origins and destinations factoring in time-of-day traffic. It then structures a realistic multi-stop itinerary and leverages API tools to autonomously generate click-to-add `.ics` Google Calendar events for your daily planner.
- **`research_workflow` (Sequential Automation Engine)**: For deep research, ReloScope triggers this sophisticated `SequentialAgent`. It is a strict pipeline that executes our massive data-gathering loop in a locked order. The output state of one agent is magically fed into the context of the next:
  1. **`environment_agent`**: The ecological scientist. It scans target coordinates to analyze 10-day weather forecasts, interprets high-resolution Air Quality (AQI) down to the exact pollutant level (e.g., PM2.5 dominance), computes rooftop solar energy potential, and checks geographic elevation to flag low-lying flood-risk zones.
  2. **`livability_agent`**: The neighborhood scout. It explores the area's amenity density using rigorous radial batch-counting. It specifically catalogs and names top-rated schools, multi-specialty hospitals, grocery stores, and parks, providing a true feel of the neighborhood's daily convenience.
  3. **`investment_agent`**: The financial analyst. It contextualizes the raw data accrued by the previous two agents against broader property market trends, infrastructure news (like upcoming metro lines or IT corridors), and local business gap opportunities (e.g., "This area has 12 coworking spaces but only 3 cafes—high ROI opportunity for Food & Beverage").
  4. **`comparison_agent` (The Output Engine)**: The presentation layer. It synthesizes the enormous volume of gathered metrics into weighted, easy-to-read comparisons. It then seamlessly reaches into Google Workspace APIs to autonomously draft and format vast Google Docs and granular Google Sheets matrices for the user to take away.
  5. **`summary_agent`**: The closer. It provides a clean, conversational wrap-up of the complex deep-dive session, delivering the final verdict directly in the chat UI.

## ✨ Tangible Outputs: Docs, Sheets & Calendars
ReloScope goes far beyond standard text-based chat interfaces. When analyzing neighborhoods or executing comparisons, the system securely authenticates and seamlessly writes directly to your Google Workspace:
* **Rich Google Docs**: Autonomously writes cleanly formatted, highly structured 2-page research reports. These docs highlight executive summaries, methodology logic, detailed multi-city comparisons, and actionable next steps.
* **Extensive Google Sheets**: Generates massive comparison matrices filled with granular data. It contrasts everything from hyper-local AQI values and flood risks to precise commute distance minutes and the true count of nearby pharmacies.
* **Smart Calendar Scheduling**: When asked to plan a tour, the system bypasses standard chat and computes the exact driving commutes between requested locations, generating click-to-add `.ics` Google Calendar event links to instantly organize your entire itinerary.

## 🗄️ Database Architecture: Why AlloyDB? 
ReloScope integrates deeply with **Google Cloud AlloyDB**, leveraging the powerful `pgvector` extension. A robust database layer is critical to elevating this project from a simple "chatbot" to a highly scalable "Urban Intelligence System":
- **Semantic Similarity Search**: Using `pgvector`, the system translates neighborhood characteristics into high-dimensional embeddings. This allows the agents to perform native vector similarity searches (e.g., "Find me an area in Pune that has the exact same demographic vibe and amenity density as Koramangala, Bangalore").
- **Historical Analysis & Caching**: Intensive geospatial API calls are expensive. AlloyDB acts as a high-speed caching layer, saving historical comparison reports, tracking user preference baselines, and massively reducing API latency for frequently researched districts.
- **Autonomous Monitoring State**: AlloyDB gives the multi-agent system persistent memory, allowing our backend to act as a stateful monitoring engine that tracks metric changes over time (like tracking rising real estate trends or deteriorating seasonal AQI over months).

## 🛠️ The Tech Arsenal: 12+ APIs and MCP Toolbox
ReloScope boasts an enormous toolkit wrapped as local Python functions and formalized as **MCPs (Model Context Protocol)**. This protocol standardizes how the Large Language Model safely interfaces with external tools, granting our agents extraordinary, hallucination-free reach into live, real-world data:

**Core Google Workspace & Google Maps APIs:**
- **Places API (New)**: Powers the massive amenity discovery loop. It executes radial searches to find exact GPS coordinates, reviews, and operational statuses of local schools, hospitals, cafes, and critical infrastructure.
- **Geocoding API**: Seamlessly converts conversational user inputs ("Bopal, Ahmedabad") into strictly formatted lat/long latitude matrices for backend math.
- **Routes API**: Rather than guessing distances, the agents use this to calculate precise A-to-B commute logistics factoring in real-world traffic scenarios, highway routes, and transit modes.
- **Air Quality API**: Harvests live, hyper-local environmental data, providing both UAQI and local CPCB standards, alongside AI-driven health recommendations.
- **Solar API & Elevation API**: Extracts structural rooftop data for renewable energy potential and identifies topographical flood-risk indicators based on sea-level meters.
- **Google Sheets & Google Docs APIs**: Responsible for direct, programmatic file creation. The agents map the raw JSON metrics they gather into heavily formatted spreadsheet matrices and natural language proxy reports.
- **Google Cloud Translation API**: Real-time linguistic inclusivity. It can effortlessly translate entire analytical reports into Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, or Urdu!

**Enterprise Database Architecture Tooling:**
- **AlloyDB MCP Toolbox**: We utilized the Model Context Protocol to build **12 custom MCP database access tools**. These tools grant the LLM agents the secured ability to read and write directly to our PostgreSQL vector database. This allows agents to seamlessly execute complex SELECT/INSERT chains natively within their thought loops to retrieve historical context without exposing raw DB credentials.


---

## 🚀 Running the Project Locally
We've deliberately made running ReloScope on your own machine incredibly simple.

### 1. Clone the Repository
```bash
git clone <your-repo-link>
cd "project-name"
```

### 2. Set Up Your Python Environment
Ensure you have Python 3.11+ installed.
```bash
python -m venv .venv

# On Windows:
.\.venv\Scripts\Activate.ps1

# On Linux/macOS:
source .venv/bin/activate

# Install the required dependencies (Including Google ADK)
pip install -r requirements.txt
```

### 3. Google Cloud CLI & Authentication
Since ReloScope relies heavily on Google's APIs, you need the Google Cloud CLI (`gcloud`) installed.
1. Download and install [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
2. Authenticate your terminal with your Google account:
```bash
gcloud auth application-default login
```
3. Set the active project:
```bash
gcloud config set project project-cohort-one
```

### 4. Setting up Virtual Environment Keys (`.env`)
For security, API keys are never pushed to GitHub. You will need to create a file named exactly `.env` in the root folder of the project.
Add the following template to your new `.env` file:
```env
# Google Cloud configuration
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=<your project name>
GOOGLE_CLOUD_LOCATION=<your location>
MODEL=<your model>

# Maps & Tooling API Key
GOOGLE_MAPS_API_KEY=<your_copied_api_key_here>
```
*(To get your Maps API key, visit the Google Cloud Console > APIs & Services > Credentials, click "Create Credentials -> API Key," and explicitly restrict it to the Maps, Routes, Places, Solar, Air Quality, Elevation, and Weather APIs).*

### 5. Launch the ADK Dev Server
Start the local Google ADK Web Interface to interact with the ReloScope agents!
```bash
adk web
```
Open **`http://127.0.0.1:8000`** in your browser, select the `reloscope` agent on the left sidebar, and start researching your next home!
