"""
app.py — SynapseAI Multi-Agent Research Assistant
Streamlit frontend with a dark, premium aesthetic
"""

import streamlit as st
import os
import time
from langchain_core.messages import HumanMessage, AIMessage
from agents import run_research

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SynapseAI — Research Assistant",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
* { box-sizing: border-box; }

.stApp {
    background: #080b12;
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0c1018 !important;
    border-right: 1px solid #1a2035;
}
section[data-testid="stSidebar"] * {
    color: #8896b0 !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; max-width: 900px; }

/* ── Logo / Header ── */
.synapse-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #1a2035;
}
.synapse-logo {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #00d4ff, #0066ff);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 0 20px #0066ff44;
}
.synapse-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    margin: 0;
}
.synapse-sub {
    font-size: 0.75rem;
    color: #3a4a6b;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0;
}

/* ── Agent Pipeline Visual ── */
.pipeline {
    display: flex;
    align-items: center;
    gap: 4px;
    margin: 1.2rem 0;
    flex-wrap: wrap;
}
.agent-node {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 10px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    border: 1px solid;
    transition: all 0.3s ease;
}
.agent-clarity   { background: #0d1829; border-color: #1e4d7b; color: #4d9fff; }
.agent-research  { background: #0d1a14; border-color: #1e4d2e; color: #4dff8f; }
.agent-validator { background: #1a1208; border-color: #4d3800; color: #ffb84d; }
.agent-synthesis { background: #1a0d1a; border-color: #4d1a7b; color: #b84dff; }
.agent-active    { box-shadow: 0 0 12px currentColor; transform: scale(1.05); }
.arrow { color: #2a3a5a; font-size: 0.9rem; }

/* ── Chat Messages ── */
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 1rem 0 0.5rem;
}
.msg-user-bubble {
    background: linear-gradient(135deg, #0052cc, #0066ff);
    color: #fff;
    padding: 10px 16px;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    font-size: 0.9rem;
    line-height: 1.5;
    box-shadow: 0 4px 15px #0052cc44;
}
.msg-assistant {
    display: flex;
    justify-content: flex-start;
    margin: 0.5rem 0 1rem;
    gap: 10px;
    align-items: flex-start;
}
.msg-avatar {
    width: 30px; height: 30px;
    background: linear-gradient(135deg, #00d4ff22, #6366f122);
    border: 1px solid #6366f144;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
    margin-top: 4px;
}
.msg-assistant-bubble {
    background: #0e1520;
    border: 1px solid #1a2540;
    color: #c8d8f0;
    padding: 14px 18px;
    border-radius: 4px 18px 18px 18px;
    max-width: 80%;
    font-size: 0.88rem;
    line-height: 1.7;
}
.msg-assistant-bubble h2, .msg-assistant-bubble h3 {
    color: #7db3ff;
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    margin: 1rem 0 0.4rem;
    border-bottom: 1px solid #1a2540;
    padding-bottom: 4px;
}
.msg-assistant-bubble strong { color: #a0c4ff; }
.msg-assistant-bubble ul { padding-left: 1.2rem; }
.msg-assistant-bubble li { margin: 0.3rem 0; }

/* ── Clarification box ── */
.clarification-box {
    background: #0d1520;
    border: 1px solid #1e3a5f;
    border-left: 3px solid #00d4ff;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 0.5rem 0 1rem;
    color: #7db3ff;
    font-size: 0.88rem;
    line-height: 1.6;
}
.clarification-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #00d4ff;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    margin-left: 8px;
}
.badge-green  { background: #0d2a1a; color: #4dff8f; border: 1px solid #1e5a2e; }
.badge-blue   { background: #0d1a2a; color: #4d9fff; border: 1px solid #1e3a5f; }
.badge-orange { background: #2a1a08; color: #ffb84d; border: 1px solid #5a3a1e; }
.badge-purple { background: #1a0d2a; color: #b84dff; border: 1px solid #3a1a5a; }

/* ── Confidence meter ── */
.confidence-bar-wrap {
    margin: 6px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.confidence-bar-bg {
    flex: 1;
    height: 4px;
    background: #1a2035;
    border-radius: 2px;
    overflow: hidden;
}
.confidence-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #0052cc, #00d4ff);
    transition: width 0.8s ease;
}
.confidence-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: #3a4a6b;
    min-width: 60px;
}

/* ── Input area ── */
.stTextInput > div > div > input {
    background: #0e1520 !important;
    border: 1px solid #1a2540 !important;
    border-radius: 10px !important;
    color: #c8d8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #0066ff !important;
    box-shadow: 0 0 0 2px #0066ff22 !important;
}
.stTextInput > div > div > input::placeholder { color: #2a3a5a !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0052cc, #0066ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px #0066ff44 !important;
}

/* ── Divider ── */
hr { border-color: #1a2035 !important; }

/* ── Sidebar widgets ── */
.stTextInput label, .stSelectbox label {
    color: #3a4a6b !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #080b12; }
::-webkit-scrollbar-thumb { background: #1a2540; border-radius: 2px; }

/* ── Thinking animation ── */
.thinking {
    display: flex;
    gap: 4px;
    align-items: center;
    padding: 4px 0;
}
.thinking-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #0066ff;
    animation: pulse 1.2s infinite;
}
.thinking-dot:nth-child(2) { animation-delay: 0.2s; background: #00a3ff; }
.thinking-dot:nth-child(3) { animation-delay: 0.4s; background: #00d4ff; }
@keyframes pulse {
    0%, 100% { opacity: 0.3; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1.2); }
}

.meta-row {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    flex-wrap: wrap;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # Chat display history
if "lc_history" not in st.session_state:
    st.session_state.lc_history = []        # LangChain message objects
if "awaiting_clarification" not in st.session_state:
    st.session_state.awaiting_clarification = False
if "clarification_question" not in st.session_state:
    st.session_state.clarification_question = ""
if "active_agent" not in st.session_state:
    st.session_state.active_agent = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "session_001"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⬡ Configuration")
    st.markdown("---")

    google_key = st.text_input(
        "GOOGLE API KEY",
        type="password",
        placeholder="AIza...",
        value=os.environ.get("GOOGLE_API_KEY", ""),
    )
    tavily_key = st.text_input(
        "TAVILY API KEY",
        type="password",
        placeholder="tvly-...",
        value=os.environ.get("TAVILY_API_KEY", ""),
    )

    if google_key:
        os.environ["GOOGLE_API_KEY"] = google_key
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key

    st.markdown("---")
    st.markdown("### ⬡ Agent Pipeline")

    agents_info = [
        ("clarity",   "⬡", "Clarity",   "Validates query specificity"),
        ("research",  "⬡", "Research",  "Fetches company data via Tavily"),
        ("validator", "⬡", "Validator", "Checks research quality"),
        ("synthesis", "⬡", "Synthesis", "Generates final response"),
    ]

    for key, icon, name, desc in agents_info:
        is_active = st.session_state.active_agent == key
        cls = f"agent-{key}" + (" agent-active" if is_active else "")
        st.markdown(
            f'<div class="agent-node {cls}">{icon} {name}</div>'
            f'<div style="font-size:0.7rem;color:#2a3a5a;margin:2px 0 8px 12px">{desc}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### ⬡ Try These")
    examples = [
        "What's the latest news about OpenAI?",
        "Tell me about Tesla's financials in 2024",
        "Who is the CEO of Microsoft and what have they done recently?",
        "What are Apple's latest product launches?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:20]}", use_container_width=True):
            st.session_state.pending_query = ex

    st.markdown("---")
    if st.button("🗑 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.lc_history = []
        st.session_state.awaiting_clarification = False
        st.session_state.clarification_question = ""
        st.session_state.active_agent = None
        st.rerun()


# ── Main Area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="synapse-header">
    <div class="synapse-logo">⬡</div>
    <div>
        <div class="synapse-title">SynapseAI Research</div>
        <div class="synapse-sub">Multi-Agent Business Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Pipeline visual
st.markdown("""
<div class="pipeline">
    <div class="agent-node agent-clarity">⬡ Clarity</div>
    <span class="arrow">→</span>
    <div class="agent-node agent-research">⬡ Research</div>
    <span class="arrow">→</span>
    <div class="agent-node agent-validator">⬡ Validator</div>
    <span class="arrow">→</span>
    <div class="agent-node agent-synthesis">⬡ Synthesis</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Check API Keys ────────────────────────────────────────────────────────────
if not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("TAVILY_API_KEY"):
    st.markdown("""
    <div style="background:#0d1520;border:1px solid #1e3a5f;border-left:3px solid #00d4ff;
                border-radius:8px;padding:20px;margin:1rem 0;">
        <div style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#00d4ff;
                    letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px">
            Setup Required
        </div>
        <div style="color:#8896b0;font-size:0.88rem;line-height:1.6">
            Enter your <strong style="color:#c8d8f0">Google API Key</strong> and 
            <strong style="color:#c8d8f0">Tavily API Key</strong> in the sidebar to begin.<br><br>
            • Google API Key: <a href="https://aistudio.google.com" style="color:#4d9fff">aistudio.google.com</a> (free)<br>
            • Tavily API Key: <a href="https://tavily.com" style="color:#4d9fff">tavily.com</a> (free tier available)
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Display Chat History ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="msg-user-bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

    elif msg["role"] == "assistant":
        content_html = msg["content"].replace("## ", "<h2>").replace("### ", "<h3>")
        st.markdown(f"""
        <div class="msg-assistant">
            <div class="msg-avatar">⬡</div>
            <div>
                <div class="msg-assistant-bubble">{content_html}</div>
                <div class="meta-row">
                    <span class="badge badge-green">✓ Research Complete</span>
                    <span class="badge badge-blue">Confidence: {msg.get('confidence', '—')}/10</span>
                    <span class="badge badge-purple">Attempts: {msg.get('attempts', '—')}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif msg["role"] == "clarification":
        st.markdown(f"""
        <div class="msg-assistant" style="margin-bottom:0.5rem">
            <div class="msg-avatar">⬡</div>
            <div class="clarification-box">
                <div class="clarification-label">⬡ Clarification Needed</div>
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Input Area ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# Handle example button clicks
pending = st.session_state.pop("pending_query", None)

col1, col2 = st.columns([5, 1])

with col1:
    placeholder = (
        "Your clarification here..." if st.session_state.awaiting_clarification
        else "Ask about any company — news, financials, leadership, products..."
    )
    user_input = st.text_input(
        "query",
        placeholder=placeholder,
        label_visibility="collapsed",
        value=pending or "",
        key="query_input",
    )

with col2:
    send = st.button("Send →", use_container_width=True)


# ── Process Query ─────────────────────────────────────────────────────────────
query_to_process = None
if send and user_input.strip():
    query_to_process = user_input.strip()
elif pending:
    query_to_process = pending

if query_to_process and os.environ.get("GOOGLE_API_KEY") and os.environ.get("TAVILY_API_KEY"):

    # Add user message to display
    st.session_state.messages.append({
        "role": "user",
        "content": query_to_process,
    })

    # Add to LangChain history
    st.session_state.lc_history.append(HumanMessage(content=query_to_process))

    # Show thinking state
    with st.spinner(""):
        st.markdown("""
        <div class="msg-assistant">
            <div class="msg-avatar">⬡</div>
            <div style="padding:10px 0">
                <div class="thinking">
                    <div class="thinking-dot"></div>
                    <div class="thinking-dot"></div>
                    <div class="thinking-dot"></div>
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#2a3a5a;margin-top:4px">
                    agents processing...
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        try:
            result = run_research(
                query=query_to_process,
                conversation_history=st.session_state.lc_history[:-1],
                thread_id=st.session_state.thread_id,
            )

            if result["awaiting_clarification"]:
                # Need more info from user
                st.session_state.awaiting_clarification = True
                st.session_state.clarification_question = result["clarification_question"]
                st.session_state.messages.append({
                    "role": "clarification",
                    "content": result["clarification_question"],
                })
                # Remove the user message from LangChain history temporarily
                st.session_state.lc_history.pop()

            else:
                # Got a response
                st.session_state.awaiting_clarification = False
                response_text = result["final_response"]

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "confidence": result.get("confidence_score", 0),
                    "attempts": result.get("research_attempts", 1),
                })

                # Add AI response to history
                st.session_state.lc_history.append(AIMessage(content=response_text))

        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"An error occurred: {str(e)}\n\nPlease check your API keys and try again.",
                "confidence": 0,
                "attempts": 0,
            })

    st.rerun()
