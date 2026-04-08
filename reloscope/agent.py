"""ReloScope — Multi-Agent AI Relocation & Urban Intelligence Advisor for India.

This is the main agent definition file for the Google ADK framework.
It defines the root_agent and all sub-agents in the multi-agent hierarchy.

Architecture:
    root_agent (orchestrator)
    ├── greeter_agent — Welcome, showcase capabilities
    ├── research_workflow (SequentialAgent)
    │   ├── environment_agent — Weather, AQI, Solar, Elevation
    │   ├── livability_agent — Places, Amenities, Commute
    │   ├── investment_agent — Trends, Opportunities
    │   ├── comparison_agent — Scoring, Reports, Sheets/Docs
    │   └── summary_agent — Work-done summary
    └── (all agents share state via output_key / session state)
"""

import os
import logging
from dotenv import load_dotenv

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.tool_context import ToolContext

# --- Tools ---
from reloscope.tools.environment_tools import (
    get_weather_forecast,
    get_air_quality,
    get_solar_potential,
    get_elevation,
    geocode_address,
)
from reloscope.tools.livability_tools import (
    search_nearby_places,
    count_amenities_by_type,
)
from reloscope.tools.routing_tools import compute_commute
from reloscope.tools.output_tools import (
    create_shared_spreadsheet,
    create_shared_document,
    generate_calendar_link,
)
from reloscope.tools.translation_tools import translate_text

# --- Prompts ---
from reloscope.prompts.greeter import GREETER_INSTRUCTION
from reloscope.prompts.environment import ENVIRONMENT_INSTRUCTION
from reloscope.prompts.livability import LIVABILITY_INSTRUCTION
from reloscope.prompts.investment import INVESTMENT_INSTRUCTION
from reloscope.prompts.comparison import COMPARISON_INSTRUCTION
from reloscope.prompts.summary import SUMMARY_INSTRUCTION

# --- Config ---
load_dotenv()
MODEL = os.getenv("MODEL", "gemini-2.5-flash")

# ============================================================
# State Management Tools
# ============================================================

def save_user_query(tool_context: ToolContext, query: str) -> dict:
    """Save the user's research query to session state.

    Args:
        query: The user's research question or request.

    Returns:
        Confirmation that the query was saved.
    """
    tool_context.state["user_query"] = query
    logging.info(f"[State] User query saved: {query}")
    return {"status": "success", "query_saved": query}


# ============================================================
# Sub-Agents
# ============================================================

# --- 1. Greeter Agent ---
greeter_agent = Agent(
    name="greeter_agent",
    model=MODEL,
    description="Welcomes the user, showcases ReloScope capabilities, and asks for their research query.",
    instruction=GREETER_INSTRUCTION,
    tools=[save_user_query],
)


# --- 2. Environment Agent ---
environment_agent = Agent(
    name="environment_agent",
    model=MODEL,
    description="Analyzes weather, air quality, solar potential, and elevation for cities and neighborhoods in India.",
    instruction=ENVIRONMENT_INSTRUCTION,
    tools=[
        get_weather_forecast,
        get_air_quality,
        get_solar_potential,
        get_elevation,
        geocode_address,
    ],
    output_key="environment_data",
)


# --- 3. Livability Agent ---
livability_agent = Agent(
    name="livability_agent",
    model=MODEL,
    description="Assesses livability by analyzing nearby amenities (schools, hospitals, parks), computing density scores, and calculating commute times.",
    instruction=LIVABILITY_INSTRUCTION,
    tools=[
        search_nearby_places,
        count_amenities_by_type,
        compute_commute,
        geocode_address,
    ],
    output_key="livability_data",
)


# --- 4. Investment Agent ---
investment_agent = Agent(
    name="investment_agent",
    model=MODEL,
    description="Analyzes investment potential, market trends, news sentiment, and identifies business opportunities in the researched areas.",
    instruction=INVESTMENT_INSTRUCTION,
    tools=[],  # Uses model knowledge + data from previous agents in state
    output_key="investment_data",
)


# --- 5. Comparison & Output Agent ---
comparison_agent = Agent(
    name="comparison_agent",
    model=MODEL,
    description="Synthesizes all analysis data, computes weighted scores, generates recommendations, and creates Google Sheets, Docs, and Calendar links.",
    instruction=COMPARISON_INSTRUCTION,
    tools=[
        create_shared_spreadsheet,
        create_shared_document,
        generate_calendar_link,
        compute_commute,
        translate_text,
    ],
    output_key="comparison_output",
)


# --- 6. Summary Agent ---
summary_agent = Agent(
    name="summary_agent",
    model=MODEL,
    description="Provides a comprehensive summary of all work done in the session including APIs called, data gathered, documents created, and next steps.",
    instruction=SUMMARY_INSTRUCTION,
    tools=[],
)


# --- 7. Tour Planner Agent ---
tour_agent = Agent(
    name="tour_agent",
    model=MODEL,
    description="Handles tour scheduling, calculates travel times, and creates Google Calendar links.",
    instruction="""You are the Smart Tour Planner.
1. Use compute_commute for accurate travel times between the user's origin and destination.
2. Suggest an itinerary timeframe.
2b. Do keep in mind user may take some time at a location before moving on to the next location in the intinerary. Take average time spent over there (for example visit to a fort can take upto 3 hours.)
3. Use generate_calendar_link to provide the Google Calendar URLs.
- When you complete your analysis, simply return your final response text. The system will automatically move to the next stage.
## Guardrails & Scope:
- **STRICT SCOPE:** You are exclusively a Relocation & Urban Intelligence Advisor for India.
- If the user asks for ANY content clearly outside this scope, firmly state: "I am sorry, but that is outside my stated job as the ReloScope advisor." Do NOT answer it.
""",
    tools=[compute_commute, generate_calendar_link],
)


# ============================================================
# Sequential Research Workflow
# ============================================================

research_workflow = SequentialAgent(
    name="research_workflow",
    description="Executes the full research pipeline: environment analysis → livability analysis → investment analysis → comparison & scoring → output generation → summary.",
    sub_agents=[
        environment_agent,
        livability_agent,
        investment_agent,
        comparison_agent,
        summary_agent,
    ],
)


# ============================================================
# Root Agent (Entry Point)
# ============================================================

root_agent = Agent(
    name="reloscope",
    model=MODEL,
    description="ReloScope — AI-powered relocation and urban intelligence advisor for India. Helps users compare cities, analyze neighborhoods, assess livability, find business opportunities, and make data-driven relocation decisions.",
    instruction="""You are **ReloScope**, the root orchestrator agent for an AI-powered relocation and urban intelligence advisor for India.

## Your Role:
You coordinate between the greeter agent and the research workflow based on the user's needs.

## Workflow:

### First interaction:
1. Transfer to `greeter_agent` to welcome the user if they don't provide a query.

### Subsequent interactions:
1. Understand the user's query
2. If it requires multi-location research (comparing cities, analyzing neighborhoods, finding opportunities):
   → Use the `save_user_query` tool to save their query to state
   → Transfer to `research_workflow` to execute the full pipeline
3. If it's a simple question you can answer directly:
   → Answer directly without invoking the workflow
4. If the user asks to plan a tour / schedule visits:
   → Transfer to `tour_agent` directly
5. If the user wants to translate something:
   → Use the translate tool directly

## Critical Rules:
- The research_workflow is a SequentialAgent — it runs environment → livability → investment → comparison → summary in order
- Respect the user's intent — don't force document creation for simple questions
- The `tour_agent` exclusively handles Google Calendar tour scheduling. Transfer to it for these tasks.
- Be conversational and helpful between research sessions
- After research completes, be ready for follow-up questions without re-running the full pipeline

## Guardrails & Scope:
- **STRICT SCOPE:** You are exclusively a Relocation & Urban Intelligence Advisor for India.
- If the user asks for ANY content clearly outside this scope (e.g., coding, writing stories, unrelated general queries), firmly state: "I am sorry, but that is outside my stated job as the ReloScope advisor." Do NOT answer out-of-scope queries.

## State Keys You Can Access:
- `user_query` — the current research query
- `environment_data` — environmental analysis results
- `livability_data` — livability analysis results
- `investment_data` — investment analysis results
- `comparison_output` — final comparison and document links
""",
    tools=[save_user_query],
    sub_agents=[greeter_agent, research_workflow, tour_agent],
)
