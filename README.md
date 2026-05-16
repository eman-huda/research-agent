# Multi-Agent Business Research Assistant

A production-grade multi-agent research system built with **LangGraph**, **Gemini 1.5 Flash**, and **Tavily Search**. Four specialized agents collaborate to deliver structured, confidence-scored business intelligence with full conversation memory.
![alt text](<Screenshot 2026-05-16 152817.png>)
---

## Architecture

```
User Query
    ↓
┌─────────────────┐
│  Clarity Agent  │ — Checks if query is specific enough
│                 │   OUTPUT: clear / needs_clarification
└────────┬────────┘
         │ clear              │ needs_clarification
         ↓                   ↓
┌─────────────────┐        INTERRUPT → Ask user
│ Research Agent  │ — Fetches real data via Tavily
│                 │   OUTPUT: findings + confidence (0-10)
└────────┬────────┘
         │ confidence ≥ 6     │ confidence < 6
         ↓                   ↓
┌─────────────────┐   ┌─────────────────┐
│ Synthesis Agent │   │ Validator Agent │ — Checks data quality
│                 │   │                 │   OUTPUT: sufficient / insufficient
└────────┬────────┘   └────────┬────────┘
         │                     │ insufficient (& attempts < 3)
         ↓                     ↓
        END          → Research Agent (loop back)
```

---

## Tech Stack

| Component | Tool |
|---|---|
| Agent Orchestration | LangGraph (StateGraph + MemorySaver) |
| LLM | Google Gemini 1.5 Flash |
| Web Search | Tavily Search API |
| UI | Streamlit |
| Memory | LangGraph MemorySaver (in-memory) |

---

## Setup & Run

### 1. Get Free API Keys

**Google Gemini (free):**
- Go to https://aistudio.google.com
- Sign in → Get API Key → Copy

**Tavily (free tier — 1000 searches/month):**
- Go to https://tavily.com
- Sign up → Dashboard → Copy API Key

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run app.py
```

### 4. Enter API Keys
Paste both keys in the sidebar and start asking questions.

---

## Features

- **4 Specialized Agents** — each with a distinct role and clear routing logic
- **Human-in-the-Loop** — Clarity Agent interrupts when queries are ambiguous
- **Confidence Scoring** — Research Agent scores data quality 0-10
- **Validation Loop** — Validator can trigger up to 3 research attempts
- **Multi-turn Memory** — conversation history maintained across all turns
- **Follow-up Questions** — understands "What about their CEO?" in context
- **Premium Dark UI** — production-grade Streamlit interface

---

## Example Queries

- "What's the latest news about OpenAI?"
- "Tell me about Tesla's financials in 2024"
- "Who is the CEO of Microsoft and what have they done recently?"
- [follow-up] "What about their competitors?"
- [ambiguous — triggers clarification] "Tell me about that company"

---

## Author

**Eman Ul Huda**
github.com/eman-huda | linkedin.com/in/eman-ul-huda-2a8011250
