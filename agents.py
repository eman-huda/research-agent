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
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import operator


# ── State Schema ─────────────────────────────────────────────────────────────
class ResearchState(TypedDict):
    messages: Annotated[List, operator.add]
    query: str
    clarity_status: str
    clarification_question: str
    research_findings: str
    confidence_score: int
    research_attempts: int
    validation_result: str
    final_response: str
    awaiting_clarification: bool


# ── LLM & Tool Setup ─────────────────────────────────────────────────────────
def get_llm():
    return ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.3,
    )

def get_search_tool():
    return TavilySearchResults(
        max_results=5,
        tavily_api_key=os.environ.get("TAVILY_API_KEY"),
    )


# ── Agent 1: Clarity Agent ───────────────────────────────────────────────────
def clarity_agent(state: ResearchState) -> ResearchState:
    llm = get_llm()

    history_text = ""
    if state.get("messages"):
        recent = state["messages"][-6:]
        history_text = "\n".join([
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in recent
        ])

    prompt = f"""You are a Clarity Agent. Evaluate if the user query is specific enough to research a company.

Conversation History:
{history_text if history_text else "No prior conversation."}

Current Query: "{state['query']}"

Rules:
- Specific company name + clear intent (news, financials, CEO, products) → CLEAR
- Vague query with no company name → NEEDS_CLARIFICATION
- Follow-up referencing prior conversation → CLEAR
- Common nicknames are fine (Apple, Google, Tesla)

Respond in EXACTLY this format, nothing else:
STATUS: clear
or
STATUS: needs_clarification
QUESTION: [specific clarification question]"""

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
    llm = get_llm()
    search = get_search_tool()

    query = state["query"]

    try:
        search_results = search.invoke({"query": f"{query} company information 2024 2025"})
        raw_data = "\n\n".join([
            f"Source: {r.get('url', 'Unknown')}\n{r.get('content', '')}"
            for r in search_results
        ]) if search_results else "No search results found."
    except Exception as e:
        raw_data = f"Search error: {str(e)}"

    prompt = f"""You are a Research Agent. Process raw search data and produce structured findings.

User Query: "{query}"

Raw Search Data:
{raw_data[:4000]}

Tasks:
1. Extract key information relevant to the query
2. Organize findings clearly with sections
3. Assign a confidence score (0-10):
   - 8-10: Rich, recent, highly relevant data
   - 6-7: Good data with minor gaps
   - 4-5: Partial data
   - 0-3: Very limited data

Respond in EXACTLY this format:
FINDINGS:
[structured findings here]

CONFIDENCE: [single number 0-10]"""

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    findings = content
    confidence = 5

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
    llm = get_llm()

    prompt = f"""You are a Validator Agent. Assess if research findings are sufficient to answer the query.

User Query: "{state['query']}"
Confidence Score: {state['confidence_score']}/10
Research Attempts so far: {state['research_attempts']}

Research Findings:
{state['research_findings'][:2000]}

Evaluation:
- Does data directly address what the user asked?
- Is there enough substance for a meaningful response?
- Are there critical gaps that would mislead the user?

Respond in EXACTLY this format:
RESULT: sufficient
or
RESULT: insufficient
REASON: [brief reason]"""

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
    llm = get_llm()

    history_text = ""
    if state.get("messages"):
        recent = state["messages"][-8:]
        history_text = "\n".join([
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in recent
        ])

    prompt = f"""You are a Synthesis Agent. Generate a comprehensive, well-structured response.

Conversation History:
{history_text if history_text else "First query."}

Current Query: "{state['query']}"

Research Findings:
{state['research_findings']}

Data Confidence: {state['confidence_score']}/10

Instructions:
- Structure with clear ## sections
- Use conversation history for follow-up context
- If confidence < 6, acknowledge data limitations
- Be informative and professional
- End with 2-3 suggested follow-up questions

Use markdown ## headers for sections."""

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
        return "research"
    return "synthesis"


# ── Build Graph ───────────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("clarity", clarity_agent)
    graph.add_node("research", research_agent)
    graph.add_node("validator", validator_agent)
    graph.add_node("synthesis", synthesis_agent)

    graph.set_entry_point("clarity")

    graph.add_conditional_edges(
        "clarity",
        route_after_clarity,
        {"interrupt": END, "research": "research"}
    )
    graph.add_conditional_edges(
        "research",
        route_after_research,
        {"synthesis": "synthesis", "validator": "validator"}
    )
    graph.add_conditional_edges(
        "validator",
        route_after_validator,
        {"research": "research", "synthesis": "synthesis"}
    )
    graph.add_edge("synthesis", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# ── Public Interface ──────────────────────────────────────────────────────────
def run_research(query: str, conversation_history: list, thread_id: str = "default"):
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
