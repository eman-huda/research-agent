"""
agents.py — Multi-Agent Research Assistant
4 specialized agents built with LangGraph:
  1. Clarity Agent     — checks if query is specific enough
  2. Research Agent    — fetches real company data via Tavily
  3. Validator Agent   — checks research quality
  4. Synthesis Agent   — generates final structured response
"""

import os
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import operator


# ── State Schema ─────────────────────────────────────────────────────────────
class ResearchState(TypedDict):
    # Conversation history (persisted across turns)
    messages: Annotated[List, operator.add]
    # Current user query
    query: str
    # Clarity agent output
    clarity_status: str          # "clear" or "needs_clarification"
    clarification_question: str  # What to ask the user
    # Research agent output
    research_findings: str
    confidence_score: int        # 0-10
    research_attempts: int
    # Validator output
    validation_result: str       # "sufficient" or "insufficient"
    # Final output
    final_response: str
    # Interrupt flag
    awaiting_clarification: bool


# ── LLM & Tool Setup ─────────────────────────────────────────────────────────
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
        temperature=0.3,
    )

def get_search_tool():
    return TavilySearchResults(
        max_results=5,
        tavily_api_key=os.environ.get("TAVILY_API_KEY"),
    )


# ── Agent 1: Clarity Agent ───────────────────────────────────────────────────
def clarity_agent(state: ResearchState) -> ResearchState:
    """
    Evaluates whether the query is specific enough to research.
    Checks for: company name, clear intent, not too vague.
    """
    llm = get_llm()

    # Build context from conversation history
    history_text = ""
    if state.get("messages"):
        recent = state["messages"][-6:]  # Last 3 turns
        history_text = "\n".join([
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in recent
        ])

    prompt = f"""You are a Clarity Agent. Your job is to evaluate if a user's query is specific enough to research a company.

Conversation History:
{history_text if history_text else "No prior conversation."}

Current Query: "{state['query']}"

Rules:
- If the query mentions a specific company name AND has a clear intent (news, financials, CEO, products, etc.) → CLEAR
- If query is vague (e.g., "tell me about a tech company", "what about them?") → NEEDS_CLARIFICATION
- If query is a follow-up referencing prior conversation context → CLEAR (use history to understand)
- Common company nicknames are fine (e.g., "Apple", "Google", "Tesla")

Respond in EXACTLY this format (no extra text):
STATUS: clear
or
STATUS: needs_clarification
QUESTION: [Your specific clarification question here]"""

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    if "STATUS: clear" in content:
        return {
            **state,
            "clarity_status": "clear",
            "awaiting_clarification": False,
            "clarification_question": "",
        }
    else:
        # Extract clarification question
        question = "Could you please specify which company you're asking about and what information you need?"
        if "QUESTION:" in content:
            question = content.split("QUESTION:")[-1].strip()

        return {
            **state,
            "clarity_status": "needs_clarification",
            "awaiting_clarification": True,
            "clarification_question": question,
        }


# ── Agent 2: Research Agent ──────────────────────────────────────────────────
def research_agent(state: ResearchState) -> ResearchState:
    """
    Searches for real company data using Tavily.
    Assigns a confidence score 0-10 based on data quality.
    """
    llm = get_llm()
    search = get_search_tool()

    query = state["query"]

    # Run Tavily search
    try:
        search_results = search.invoke({"query": f"{query} company information 2024 2025"})
        raw_data = "\n\n".join([
            f"Source: {r.get('url', 'Unknown')}\n{r.get('content', '')}"
            for r in search_results
        ]) if search_results else "No search results found."
    except Exception as e:
        raw_data = f"Search error: {str(e)}"

    # Let LLM process and score the results
    prompt = f"""You are a Research Agent. You have retrieved raw search data about a company. 
Analyze this data and produce structured research findings.

User Query: "{query}"

Raw Search Data:
{raw_data[:4000]}

Your task:
1. Extract key information relevant to the query
2. Organize findings clearly
3. Assign a confidence score (0-10) based on data quality and relevance:
   - 8-10: Rich, recent, highly relevant data
   - 6-7: Good data with some gaps
   - 4-5: Partial data, some relevant info
   - 0-3: Very limited or irrelevant data

Respond in this EXACT format:
FINDINGS:
[Your structured research findings here - be detailed and informative]

CONFIDENCE: [single number 0-10]"""

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    # Parse findings and confidence
    findings = content
    confidence = 5  # default

    if "FINDINGS:" in content and "CONFIDENCE:" in content:
        parts = content.split("CONFIDENCE:")
        findings = parts[0].replace("FINDINGS:", "").strip()
        try:
            confidence = int(parts[1].strip().split()[0])
            confidence = max(0, min(10, confidence))
        except:
            confidence = 5

    attempts = state.get("research_attempts", 0) + 1

    return {
        **state,
        "research_findings": findings,
        "confidence_score": confidence,
        "research_attempts": attempts,
    }


# ── Agent 3: Validator Agent ─────────────────────────────────────────────────
def validator_agent(state: ResearchState) -> ResearchState:
    """
    Validates research quality and completeness.
    Decides if data is sufficient to generate a good response.
    """
    llm = get_llm()

    prompt = f"""You are a Validator Agent. Assess whether the research findings are sufficient to answer the user's query.

User Query: "{state['query']}"
Confidence Score: {state['confidence_score']}/10
Research Attempts: {state['research_attempts']}

Research Findings:
{state['research_findings'][:2000]}

Evaluation criteria:
- Does the data directly address what the user asked?
- Is there enough substance to generate a meaningful response?
- Are there critical gaps that would make the answer misleading?

Respond in EXACTLY this format:
RESULT: sufficient
or
RESULT: insufficient
REASON: [Brief reason]"""

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    result = "sufficient"
    if "RESULT: insufficient" in content:
        result = "insufficient"

    return {
        **state,
        "validation_result": result,
    }


# ── Agent 4: Synthesis Agent ─────────────────────────────────────────────────
def synthesis_agent(state: ResearchState) -> ResearchState:
    """
    Generates a polished, structured final response.
    Maintains conversation context for follow-up questions.
    """
    llm = get_llm()

    # Build conversation context
    history_text = ""
    if state.get("messages"):
        recent = state["messages"][-8:]
        history_text = "\n".join([
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in recent
        ])

    prompt = f"""You are a Synthesis Agent. Generate a comprehensive, well-structured response for the user.

Conversation History:
{history_text if history_text else "This is the first query."}

Current Query: "{state['query']}"

Research Findings:
{state['research_findings']}

Data Confidence: {state['confidence_score']}/10

Instructions:
- Structure your response clearly with sections
- Use the conversation history to personalize follow-up responses
- If confidence is low (<6), acknowledge data limitations honestly
- Be informative, concise, and professional
- For financial/news queries, include timestamps where available
- End with 2-3 suggested follow-up questions the user might find useful

Format your response with clear sections using markdown-style headers (##)."""

    response = llm.invoke([HumanMessage(content=prompt)])

    return {
        **state,
        "final_response": response.content,
        "awaiting_clarification": False,
    }


# ── Routing Logic ─────────────────────────────────────────────────────────────
def route_after_clarity(state: ResearchState) -> str:
    if state["clarity_status"] == "needs_clarification":
        return "interrupt"
    return "research"

def route_after_research(state: ResearchState) -> str:
    if state["confidence_score"] >= 6:
        return "synthesis"
    return "validator"

def route_after_validator(state: ResearchState) -> str:
    attempts = state.get("research_attempts", 0)
    if state["validation_result"] == "insufficient" and attempts < 3:
        return "research"  # Loop back
    return "synthesis"    # Max attempts reached or sufficient


# ── Build the Graph ───────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("clarity", clarity_agent)
    graph.add_node("research", research_agent)
    graph.add_node("validator", validator_agent)
    graph.add_node("synthesis", synthesis_agent)

    # Entry point
    graph.set_entry_point("clarity")

    # Conditional routing
    graph.add_conditional_edges(
        "clarity",
        route_after_clarity,
        {
            "interrupt": END,       # Stop and ask user
            "research": "research",
        }
    )

    graph.add_conditional_edges(
        "research",
        route_after_research,
        {
            "synthesis": "synthesis",
            "validator": "validator",
        }
    )

    graph.add_conditional_edges(
        "validator",
        route_after_validator,
        {
            "research": "research",   # Loop
            "synthesis": "synthesis",
        }
    )

    graph.add_edge("synthesis", END)

    # Compile with memory
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# ── Public Interface ──────────────────────────────────────────────────────────
def run_research(query: str, conversation_history: list, thread_id: str = "default"):
    """
    Main entry point. Returns dict with response info.
    """
    graph = build_graph()

    initial_state = {
        "messages": conversation_history,
        "query": query,
        "clarity_status": "",
        "clarification_question": "",
        "research_findings": "",
        "confidence_score": 0,
        "research_attempts": 0,
        "validation_result": "",
        "final_response": "",
        "awaiting_clarification": False,
    }

    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(initial_state, config=config)

    return {
        "clarity_status": result.get("clarity_status"),
        "awaiting_clarification": result.get("awaiting_clarification", False),
        "clarification_question": result.get("clarification_question", ""),
        "final_response": result.get("final_response", ""),
        "confidence_score": result.get("confidence_score", 0),
        "research_attempts": result.get("research_attempts", 0),
        "validation_result": result.get("validation_result", ""),
    }
