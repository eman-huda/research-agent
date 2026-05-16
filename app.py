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
    page_title="Research Assistant",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    color-scheme: dark;
}
* { box-sizing: border-box; }
.stApp {
    background: radial-gradient(circle at top left, rgba(62, 110, 255, 0.16), transparent 25%),
                radial-gradient(circle at top right, rgba(107, 94, 255, 0.18), transparent 18%),
                #050814;
    font-family: 'DM Sans', sans-serif;
}

section[data-testid="stSidebar"] {
    background: rgba(6, 10, 24, 0.96) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
section[data-testid="stSidebar"] * {
    color: #c7d5f5 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 1.8rem 2rem 2.4rem !important;
    max-width: 1480px;
}

a { color: #7db3ff; }

.hero-shell {
    display: grid;
    gap: 1.2rem;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    background: rgba(10, 18, 36, 0.82);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 30px;
    backdrop-filter: blur(20px);
    box-shadow: 0 40px 120px rgba(2, 12, 40, 0.45);
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 1.8px;
    color: #7c93d2;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.4rem, 4vw, 4.2rem);
    line-height: 1.02;
    letter-spacing: -0.03em;
    margin: 0;
    background: linear-gradient(90deg, #7db3ff, #b57cff, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-copy {
    font-size: 1rem;
    max-width: 820px;
    line-height: 1.8;
    color: #c7d5f5;
}
.hero-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.9rem;
    margin-top: 1.4rem;
}
.hero-pill {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 999px;
    padding: 0.85rem 1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    color: #d5e1ff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}
.hero-pill span { color: #7db3ff; }

.glass-card {
    background: rgba(8, 14, 28, 0.86);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 28px;
    padding: 1.4rem;
    backdrop-filter: blur(18px);
    box-shadow: 0 32px 90px rgba(0, 0, 0, 0.22);
}
.glass-card.smaller { padding: 1rem; }
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    margin: 0 0 1rem;
    color: #f5f7ff;
}
.card-subtitle {
    color: #9badcf;
    font-size: 0.85rem;
    line-height: 1.7;
    margin: 0;
}

.workflow-board {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    flex-wrap: wrap;
    padding: 0.8rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
}
.workflow-step {
    min-width: 120px;
    padding: 0.9rem 1rem;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    color: #99a8d5;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    transition: transform 0.25s ease, border-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
}
.workflow-step.active {
    color: #e7f7ff;
    border-color: rgba(109, 154, 255, 0.75);
    box-shadow: 0 0 30px rgba(77, 170, 255, 0.22);
    transform: translateY(-2px);
    background: rgba(28, 52, 97, 0.55);
}
.workflow-step .step-label {
    font-weight: 700;
    font-size: 0.95rem;
}
.workflow-step .step-desc {
    color: #9badcf;
    font-size: 0.76rem;
    line-height: 1.5;
}
.workflow-arrow {
    font-size: 1.4rem;
    color: rgba(255,255,255,0.3);
}

.assistant-panel {
    display: grid;
    gap: 1rem;
}
.assistant-avatar {
    width: 72px;
    height: 72px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(76, 153, 255, 0.2), rgba(120, 73, 255, 0.18));
    border: 1px solid rgba(255,255,255,0.15);
    display: grid;
    place-items: center;
    color: white;
    font-size: 2rem;
    box-shadow: 0 18px 60px rgba(24, 93, 255, 0.18);
}
.assistant-status {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 1rem 1.1rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 22px;
}
.assistant-status strong {
    color: #e7f7ff;
    font-family: 'Syne', sans-serif;
}
.assistant-state {
    color: #98b7e3;
    font-size: 0.9rem;
    line-height: 1.6;
}
.metric-grid {
    display: grid;
    gap: 0.9rem;
}
.metric-card {
    padding: 1rem;
    border-radius: 22px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}
.metric-value {
    display: block;
    font-size: 1.9rem;
    font-family: 'Syne', sans-serif;
    margin-top: 0.35rem;
    color: #eef4ff;
}
.metric-label {
    color: #94a9d0;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.progress-pill {
    height: 10px;
    width: 100%;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
    margin-top: 0.9rem;
}
.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #5ac4ff, #9f7fff);
    transition: width 0.8s ease;
}

.activity-feed {
    display: grid;
    gap: 0.8rem;
}
.activity-event {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    padding: 1rem;
    border-radius: 20px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}
.event-dot {
    min-width: 10px;
    min-height: 10px;
    border-radius: 50%;
    margin-top: 0.4rem;
}
.event-title {
    color: #e6ecff;
    font-size: 0.92rem;
    line-height: 1.6;
}
.event-time {
    color: #8fa7d8;
    font-size: 0.76rem;
    margin-top: 0.35rem;
}
.event-info .event-dot { background: #5ab7ff; }
.event-success .event-dot { background: #55d289; }
.event-warning .event-dot { background: #ffad52; }
.event-error .event-dot { background: #ff5b87; }

.insight-grid {
    display: grid;
    gap: 1rem;
}
.insight-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 24px;
    padding: 1.1rem;
    min-height: 136px;
}
.insight-card h4 {
    margin: 0 0 0.75rem;
    font-family: 'Syne', sans-serif;
    color: #eef4ff;
    font-size: 1rem;
}
.insight-card p {
    margin: 0;
    color: #b0c3e6;
    font-size: 0.88rem;
    line-height: 1.7;
}

.chat-window {
    display: grid;
    gap: 1rem;
}
.chat-window .glass-card {
    padding: 1.4rem;
}
.chat-piece {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;
}
.chat-user { justify-content: flex-end; }
.chat-user .bubble {
    background: linear-gradient(135deg, rgba(0,82,204,0.95), rgba(0,102,255,0.95));
    color: white;
    border-radius: 22px 22px 4px 22px;
}
.chat-assistant .bubble {
    background: rgba(18, 28, 50, 0.95);
    color: #d0d9f3;
    border-radius: 4px 22px 22px 22px;
    border: 1px solid rgba(255,255,255,0.08);
}
.bubble {
    padding: 16px 20px;
    max-width: 82%;
    line-height: 1.75;
    font-size: 0.95rem;
    white-space: pre-wrap;
}
.bubble h2, .bubble h3 { color: #8dbcff; margin: 1rem 0 0.6rem; }

.input-panel {
    display: grid;
    gap: 1.1rem;
    padding: 1.4rem;
    margin-top: 1.5rem;
    background: rgba(13, 20, 39, 0.9);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 28px;
}
.input-actions {
    display: flex;
    gap: 0.9rem;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
}
.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.55rem 0.9rem;
    border-radius: 999px;
    font-family: 'DM Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.7rem;
    color: #d8e7ff;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}
.hero-shell { animation: float 8s ease-in-out infinite; }

@media (max-width: 1024px) {
    .hero-stats { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
    .workflow-board { flex-direction: column; }
}
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ──────────────────────────────────────────────────────────
import re
from datetime import datetime


def init_session_state():
    defaults = {
        'messages': [],
        'lc_history': [],
        'awaiting_clarification': False,
        'clarification_question': '',
        'active_agent': 'clarity',
        'thread_id': 'session_001',
        'activity_feed': [],
        'last_result': {},
        'query_input': '',
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def format_timestamp():
    return datetime.now().strftime('%I:%M %p')


def push_activity(message: str, level: str = 'info'):
    st.session_state.activity_feed.insert(0, {
        'text': message,
        'status': level,
        'time': format_timestamp(),
    })
    st.session_state.activity_feed = st.session_state.activity_feed[:12]


def agent_label(key: str) -> str:
    return {
        'clarity': 'Clarity',
        'research': 'Research',
        'validator': 'Validator',
        'synthesis': 'Synthesis',
    }.get(key, 'Samantha')


def build_insights(response_text: str):
    if not response_text:
        return []
    sections = re.split(r'\n##+\s*', response_text)
    titles = re.findall(r'\n##+\s*(.+)', response_text)
    cards = []
    for idx, title in enumerate(titles[:5]):
        body = sections[idx + 1].strip() if idx + 1 < len(sections) else ''
        clean = body.replace('\n', ' ').strip()
        if len(clean) > 150:
            clean = clean[:150].rstrip() + '…'
        cards.append({'title': title, 'body': clean or 'Insight coming from Samantha…'})
    if not cards:
        snippet = response_text.replace('\n', ' ').strip()
        if len(snippet) > 180:
            snippet = snippet[:180].rstrip() + '…'
        return [{'title': 'Research summary', 'body': snippet}]
    return cards


def node_html(label: str, key: str, active_key: str, desc: str):
    active = 'active' if active_key == key else ''
    return f'<div class="workflow-step {active}"><span class="step-label">{label}</span><span class="step-desc">{desc}</span></div>'


def render_sidebar():
    with st.sidebar:
        st.markdown('''
            <div style="padding: 0 0.4rem;">
                <h3 style="margin-bottom:0.45rem; font-family: 'Syne', sans-serif; font-size:1.25rem; color:#eef4ff;">
                    Samantha Control
                </h3>
                <p style="color:#9db1d8; font-size:0.95rem; margin:0 0 1rem; line-height:1.7;">
                    Manage API keys, workflow examples, and conversation state for a polished demo experience.
                </p>
            </div>
        ''', unsafe_allow_html=True)

        groq_key = st.text_input(
            'Groq API Key',
            type='password',
            placeholder='gsk_...',
            value=os.environ.get('GROQ_API_KEY', ''),
            help='Google GeminI / Groq key used by the assistant.',
        )
        tavily_key = st.text_input(
            'Tavily API Key',
            type='password',
            placeholder='tvly-...',
            value=os.environ.get('TAVILY_API_KEY', ''),
            help='Search API key for live company intelligence.',
        )

        if groq_key:
            os.environ['GROQ_API_KEY'] = groq_key
        if tavily_key:
            os.environ['TAVILY_API_KEY'] = tavily_key

        st.markdown('---')
        st.markdown('''
            <div style="padding: 0 0.4rem;">
                <p style="font-family:'DM Mono',monospace;font-size:0.75rem;color:#7db3ff;text-transform:uppercase;letter-spacing:1.6px;margin:0 0 0.8rem;">
                    Quick launch
                </p>
            </div>
        ''', unsafe_allow_html=True)

        examples = [
            "What's the latest news about OpenAI?",
            "Tell me about Tesla's financials in 2024",
            "Who is the CEO of Microsoft and what have they done recently?",
            "What are Apple's latest product launches?",
        ]
        for idx, ex in enumerate(examples):
            if st.button(ex, key=f'ex_{idx}', use_container_width=True):
                st.session_state.query_input = ex
                st.session_state.pending_query = ex

        st.markdown('---')
        if st.button('Clear conversation', use_container_width=True):
            st.session_state.messages = []
            st.session_state.lc_history = []
            st.session_state.awaiting_clarification = False
            st.session_state.clarification_question = ''
            st.session_state.active_agent = 'clarity'
            st.session_state.last_result = {}
            st.session_state.activity_feed = []
            st.session_state.query_input = ''
            push_activity('Samantha is ready for a fresh research session.', 'info')
            st.experimental_rerun()


def render_hero():
    active_agent = agent_label(st.session_state.active_agent)
    status_text = 'Awaiting your next signal.'
    if st.session_state.awaiting_clarification:
        status_text = 'Samantha needs a quick clarification before she proceeds.'
    elif st.session_state.last_result:
        status_text = f'Samantha delivered the latest findings through the {active_agent} Agent.'

    st.markdown(f"""
    <div class="hero-shell">
        <div>
            <div class="hero-eyebrow">Meet Samantha</div>
            <h1 class="hero-title">AI research orchestration with intelligence and confidence.</h1>
            <p class="hero-copy">Samantha manages a four-agent workflow that moves from clarification to research, validation, and synthesis — all while keeping your conversation context intact.</p>
            <div class="hero-stats">
                <div class="hero-pill">Live multi-turn research</div>
                <div class="hero-pill">Human-in-the-loop clarity</div>
                <div class="hero-pill">Confidence-backed intelligence</div>
            </div>
        </div>
        <div style="display:grid; gap:0.95rem; align-content:start;">
            <div class="glass-card smaller">
                <div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:0.9rem;">
                    <div class="assistant-avatar">S</div>
                    <div>
                        <div style="font-size:0.95rem; color:#eef4ff; font-weight:700;">Samantha</div>
                        <div style="font-size:0.82rem; color:#9ab1d7;">Your AI research analyst</div>
                    </div>
                </div>
                <div style="display:grid; gap:0.65rem;">
                    <div class="status-chip">{status_text}</div>
                    <div class="status-chip">Active node: {active_agent}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_workflow():
    active = st.session_state.active_agent or 'clarity'
    st.markdown('''
        <div class="glass-card">
            <div class="card-title">Workflow live view</div>
            <div class="card-subtitle">Samantha routes your question through the multi-agent process with transparency and energy.</div>
            <div class="workflow-board" style="margin-top:1.4rem;">
    ''' +
        node_html('Clarity', 'clarity', active, 'Validates query intent') +
        '<div class="workflow-arrow">→</div>' +
        node_html('Research', 'research', active, 'Fetches real data') +
        '<div class="workflow-arrow">→</div>' +
        node_html('Validator', 'validator', active, 'Checks quality') +
        '<div class="workflow-arrow">→</div>' +
        node_html('Synthesis', 'synthesis', active, 'Crafts the final report') +
        '</div></div>',
        unsafe_allow_html=True)


def render_samantha_panel():
    last = st.session_state.last_result or {}
    confidence = last.get('confidence_score', 0)
    attempts = last.get('research_attempts', 0)
    validation = last.get('validation_result', 'pending')
    validation_label = validation.capitalize() if validation else 'Pending'
    st.markdown(f'''
        <div class="glass-card assistant-panel">
            <div class="card-title">Samantha overview</div>
            <div class="assistant-status">
                <div style="display:grid; gap:0.24rem;">
                    <strong>{agent_label(st.session_state.active_agent)} Agent</strong>
                    <span class="assistant-state">{ 'Clarifying request' if st.session_state.awaiting_clarification else 'Processing research and confidence signals' }</span>
                </div>
            </div>
            <div class="metric-grid">
                <div class="metric-card"><span class="metric-label">Confidence</span><span class="metric-value">{confidence}/10</span>
                    <div class="progress-pill"><span class="progress-fill" style="width:{confidence * 10}%;"></span></div>
                </div>
                <div class="metric-card"><span class="metric-label">Validator status</span><span class="metric-value">{validation_label}</span></div>
                <div class="metric-card"><span class="metric-label">Research attempts</span><span class="metric-value">{attempts}</span></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)


def render_insight_cards():
    cards = build_insights(st.session_state.last_result.get('final_response', ''))
    if not cards:
        st.markdown('''
            <div class="glass-card">
                <div class="card-title">Research insights</div>
                <div class="card-subtitle">Submit a query to generate a polished summary of company news, leadership, competitors, and financial context.</div>
            </div>
        ''', unsafe_allow_html=True)
        return
    html = '<div class="glass-card"><div class="card-title">Research insights</div><div class="insight-grid">'
    for card in cards[:4]:
        html += f'<div class="insight-card"><h4>{card["title"]}</h4><p>{card["body"]}</p></div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_activity_feed():
    if not st.session_state.activity_feed:
        st.markdown('''
            <div class="glass-card">
                <div class="card-title">Activity feed</div>
                <div class="card-subtitle">Samantha logs every workflow event so your demo feels alive and intentional.</div>
                <div class="activity-feed" style="margin-top:1rem;">
                    <div class="activity-event event-info"><div class="event-dot"></div><div>
                        <div class="event-title">Ready for your first research prompt.</div>
                        <div class="event-time">Awaiting input</div>
                    </div></div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        html = '''
            <div class="glass-card">
                <div class="card-title">Activity feed</div>
                <div class="card-subtitle">Samantha logs every workflow event so your demo feels alive and intentional.</div>
                <div class="activity-feed" style="margin-top:1rem;">
        '''
        for event in st.session_state.activity_feed[:6]:
            html += f'<div class="activity-event event-{event["status"]}"><div class="event-dot"></div><div><div class="event-title">{event["text"]}</div><div class="event-time">{event["time"]}</div></div></div>'
        html += '</div></div>'
        st.markdown(html, unsafe_allow_html=True)


def render_chat_messages():
    st.markdown('<div class="glass-card chat-window"><div class="card-title">Conversation</div>', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown('''
            <div style="color:#9fb4dd; padding:1rem 0;">Ask Samantha a business question to begin the research workflow.</div>
        ''', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            content = msg['content'].replace('\n', '<br>')
            st.markdown(f'''
                <div class="chat-piece chat-user"><div class="bubble">{content}</div></div>
            ''', unsafe_allow_html=True)
        elif msg['role'] == 'assistant':
            content_html = msg['content'].replace('## ', '<h2>').replace('### ', '<h3>').replace('\n', '<br>')
            st.markdown(f'''
                <div class="chat-piece chat-assistant">
                    <div class="bubble">{content_html}</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(f'''
                <div style="display:flex; gap:0.7rem; flex-wrap:wrap; margin-top:-0.4rem; margin-bottom:0.8rem;">
                    <span class="badge badge-blue">Confidence: {msg.get('confidence','—')}/10</span>
                    <span class="badge badge-purple">Attempts: {msg.get('attempts','—')}</span>
                </div>
            ''', unsafe_allow_html=True)
        elif msg['role'] == 'clarification':
            st.markdown(f'''
                <div class="chat-piece chat-assistant">
                    <div class="bubble clarification-box"><strong>Clarification needed:</strong><br>{msg['content']}</div>
                </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_input_panel():
    placeholder = 'Clarify the request...' if st.session_state.awaiting_clarification else 'Ask Samantha about a company, CEO, product, or market trend...'
    if 'pending_query' in st.session_state:
        st.session_state.query_input = st.session_state.pending_query
        st.session_state.pop('pending_query', None)

    user_input = st.text_input('Your research prompt', key='query_input', placeholder=placeholder, label_visibility='collapsed')
    send = st.button('Send to Samantha →', use_container_width=True)

    if send and user_input.strip():
        return user_input.strip()
    return None


def render_api_warning():
    st.markdown('''
        <div class="glass-card" style="border-left:4px solid #4d9fff; margin-bottom:1.5rem;">
            <div class="card-title">Setup required</div>
            <div class="card-subtitle">Enter your Groq and Tavily API keys in the sidebar to unlock Samantha's full research capabilities.</div>
        </div>
    ''', unsafe_allow_html=True)


# ── Initialize ───────────────────────────────────────────────────────────────
init_session_state()
if not st.session_state.activity_feed:
    push_activity('Samantha is ready for a fresh research session.', 'info')

render_sidebar()
render_hero()

if not os.environ.get('GROQ_API_KEY') or not os.environ.get('TAVILY_API_KEY'):
    render_api_warning()

left, right = st.columns([3, 1], gap='large')
with left:
    render_workflow()
    render_insight_cards()
    render_chat_messages()
with right:
    render_samantha_panel()
    render_activity_feed()

query_to_process = render_input_panel()

if query_to_process and os.environ.get('GROQ_API_KEY') and os.environ.get('TAVILY_API_KEY'):
    st.session_state.messages.append({
        'role': 'user',
        'content': query_to_process,
    })
    st.session_state.lc_history.append(HumanMessage(content=query_to_process))
    if st.session_state.awaiting_clarification:
        st.session_state.active_agent = 'clarity'
        push_activity('Samantha is validating the clarification before continuing.', 'info')
    else:
        st.session_state.active_agent = 'research'
        push_activity('Samantha received your query and began research.', 'info')

    with st.spinner('Samantha is analyzing the workflow...'):
        st.markdown('''
            <div class="thinking"><div class="thinking-dot"></div><div class="thinking-dot"></div><div class="thinking-dot"></div></div>
        ''', unsafe_allow_html=True)
        try:
            result = run_research(
                query=query_to_process,
                conversation_history=st.session_state.lc_history[:-1],
                thread_id=st.session_state.thread_id,
            )
            st.session_state.last_result = result
            if result['awaiting_clarification']:
                st.session_state.awaiting_clarification = True
                st.session_state.clarification_question = result['clarification_question']
                st.session_state.messages.append({
                    'role': 'clarification',
                    'content': result['clarification_question'],
                })
                st.session_state.active_agent = 'clarity'
                push_activity('Samantha detected ambiguity and requested clarification.', 'warning')
                st.session_state.lc_history.pop()
            else:
                st.session_state.awaiting_clarification = False
                st.session_state.active_agent = 'synthesis'
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': result['final_response'],
                    'confidence': result.get('confidence_score', 0),
                    'attempts': result.get('research_attempts', 0),
                })
                st.session_state.lc_history.append(AIMessage(content=result['final_response']))
                push_activity('Samantha synthesized the final intelligence report.', 'success')
                validation_status = result.get('validation_result', 'pending')
                if validation_status == 'insufficient':
                    push_activity('Validator suggested deeper research before finalizing.', 'warning')
                else:
                    push_activity('Research confidence is strong and validation passed.', 'success')
        except Exception as e:
            st.session_state.messages.append({
                'role': 'assistant',
                'content': f'An error occurred: {str(e)}\n\nPlease check your API keys and try again.',
                'confidence': 0,
                'attempts': 0,
            })
            push_activity('Samantha encountered an error while processing.', 'error')
