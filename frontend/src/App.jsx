import { useEffect, useMemo, useState } from 'react';

const STEPS = [
  { id: 'boot', label: 'Boot Agent', description: 'Agent is spinning up its core and loading the research engine.' },
  { id: 'connect', label: 'Activate sources', description: 'Agent is connecting to Groq and Tavily behind the scenes for live intelligence.' },
  { id: 'prompt', label: 'Ask your question', description: 'Everything is ready — now type your business prompt and launch the workflow.' },
];

const DEFAULT_ACTIVITY = [
  { text: 'Agent is powering on and preparing your research session.', status: 'info' },
];

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function App() {
  const [prompt, setPrompt] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [activityFeed, setActivityFeed] = useState(DEFAULT_ACTIVITY);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastResponse, setLastResponse] = useState(null);
  const [step, setStep] = useState('boot');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (step === 'boot') {
      const timeout = setTimeout(() => setStep('connect'), 1200);
      return () => clearTimeout(timeout);
    }
    if (step === 'connect' && prompt.trim()) {
      setStep('prompt');
    }
    if (step === 'prompt' && !prompt.trim()) {
      setStep('connect');
    }
  }, [prompt, step]);

  const currentStep = useMemo(() => STEPS.find((item) => item.id === step), [step]);

  const assistantQuote = useMemo(() => {
    if (isProcessing) {
      return 'Research engines are warming up — I am synthesizing clever business intelligence now!';
    }
    if (step === 'boot') {
      return 'I am powering on and aligning the research matrix.';
    }
    if (step === 'connect') {
      return 'I am connecting my hidden Groq and Tavily sources behind the scenes.';
    }
    return 'Perfect! Write a clear prompt and I’ll turn it into a polished report.';
  }, [step, isProcessing]);

  const assistantTip = useMemo(() => {
    if (step === 'boot') {
      return 'The agent is loading its core — hang tight for the next quick step.';
    }
    if (step === 'connect') {
      return 'The live intelligence pipeline is active. Your question is the last piece.';
    }
    return 'Tip: keep your prompt specific for the crispest research output.';
  }, [step]);

  const progressValue = useMemo(() => {
    if (isProcessing) return 96;
    if (step === 'boot') return 20;
    if (step === 'connect') return 60;
    return 100;
  }, [step, isProcessing]);

  const addActivity = (text, status = 'info') => {
    setActivityFeed((prev) => [{ text, status, id: Date.now() }, ...prev].slice(0, 10));
  };

  const escapeHtml = (text) =>
    String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

  const formatMessageText = (text) => {
    const escaped = escapeHtml(text);
    const withBold = escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    const withItalic = withBold.replace(/\*(.+?)\*/g, '<em>$1</em>');
    const paragraphs = withItalic
      .split(/\n{2,}/)
      .map((line) => `<p>${line.replace(/\n/g, '<br/>')}</p>`)
      .join('');
    return paragraphs;
  };

  const handleSend = async () => {
    if (!prompt.trim()) {
      setErrorMessage('Please type your question before sending your prompt.');
      return;
    }
    setErrorMessage('');
    setIsProcessing(true);
    addActivity('Agent is activating the multi-agent workflow...', 'info');
    const updatedChat = [...chatHistory, { role: 'user', text: prompt }];
    setChatHistory(updatedChat);

    try {
      const response = await fetch(`${API_BASE}/api/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: prompt,
          thread_id: 'session_001',
          history: updatedChat,
        }),
      });
      if (!response.ok) {
        throw new Error('Network error. Confirm backend is running and CORS is enabled.');
      }
      const payload = await response.json();
      setLastResponse(payload);
      setChatHistory((prev) => [
        ...prev,
        { role: 'assistant', text: payload.final_response || 'Agent returned an empty result.' },
      ]);
      addActivity('Agent synthesized your research and returned a premium report.', 'success');
      setPrompt('');
    } catch (error) {
      console.error(error);
      setErrorMessage(error.message || 'Something went wrong while contacting the backend.');
      addActivity('Agent hit an issue and asked you to check the backend.', 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const avatarPositionClass = {
    boot: 'avatar-step-0',
    connect: 'avatar-step-1',
    prompt: 'avatar-step-2',
  }[step];

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Research Agent</p>
          <h1>Research Agent</h1>
          <p className="hero-text">A lively React experience for multi-agent business research — with movement, chatter, and a cheerful assistant guiding every step.</p>
        </div>
        <div className="hero-badge"></div>
      </header>

      <section className="launch-panel">
        <div className="workflow-card">
          <div className="workflow-title">Agent says...</div>
          <div className="workflow-copy">{currentStep.description}</div>
          <div className="stage-indicator">
            {STEPS.map((item) => (
              <div key={item.id} className={`step-pill ${step === item.id ? 'active' : ''}`}>
                <span>{item.label}</span>
              </div>
            ))}
          </div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${progressValue}%` }} />
            <div className={`progress-marker ${progressValue >= 25 ? 'active' : ''}`} style={{ left: '6%' }} />
            <div className={`progress-marker ${progressValue >= 65 ? 'active' : ''}`} style={{ left: '48%' }} />
            <div className={`progress-marker ${progressValue >= 100 ? 'active' : ''}`} style={{ left: '92%' }} />
          </div>
          <div className="avatar-stage">
            <div className="holo-overlay" />
            <div className="sparkle sparkle1" />
            <div className="sparkle sparkle2" />
            <div className="sparkle sparkle3" />
            <div className="sparkle sparkle4" />
            <div className={`samantha-physical ${avatarPositionClass}`}>
              <img
                className={`samantha-avatar ${isProcessing ? 'active' : ''}`}
                src="/samantha.jpg"
                alt="Agent avatar"
              />
            </div>
            <div className="dialogue-box">
              <strong>Agent</strong>
              <p>{assistantQuote}</p>
            </div>
            <div className="tip-box">
              <strong>Tip</strong>
              <p>{assistantTip}</p>
            </div>
          </div>
        </div>

        <div className="forms-card">
          <div className="card-header">
            <div>
              <h2>Interactive setup</h2>
              <p>The agent is already connected to live Groq and Tavily intelligence internally. Just type your prompt and it will work its magic.</p>
            </div>
            <div className="chip">Step {STEPS.findIndex((s) => s.id === step) + 1}/3</div>
          </div>

          <div className="status-grid internal-status">
            <div className="status-pill">AI core: online</div>
            <div className="status-pill">Groq engine: connected</div>
            <div className="status-pill">Tavily pipeline: synced</div>
            <div className="status-pill">Research pipeline: ready</div>
          </div>

          <div className="field-group">
            <label>Your research prompt</label>
            <textarea
              rows="4"
              value={prompt}
              placeholder="Ask the research agent something like 'What is the latest growth strategy for Shopify?'"
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <div className="button-row">
            <button className="primary-button" onClick={handleSend} disabled={isProcessing}>
              {isProcessing ? 'Researching...' : 'Send'}
            </button>
            <div className="click-hint">Click to launch the agent!</div>
          </div>
          {errorMessage && <div className="error-box">{errorMessage}</div>}
        </div>
      </section>

      <section className="main-grid">
        <div className="chat-panel">
          <div className="glass-card chat-card">
            <div className="chat-header">
              <div>
                <h2>Research chat</h2>
                <p>Center your prompt and answers here — the agent lives in the conversation, just like an LLM workspace.</p>
              </div>
              <span className={`status-pill ${isProcessing ? 'live' : 'idle'}`}>
                {isProcessing ? 'Researching...' : 'Ready'}
              </span>
            </div>

            <div className="chat-list">
              {chatHistory.length === 0 && (
                <div className="empty-state">Start the conversation by entering a prompt below.</div>
              )}
              {chatHistory.map((message, index) => (
                <div key={index} className={`chat-bubble ${message.role}`}>
                  <div className="bubble-role">{message.role === 'user' ? 'You' : 'Agent'}</div>
                  <div
                    className="bubble-text"
                    dangerouslySetInnerHTML={{
                      __html:
                        message.role === 'assistant'
                          ? formatMessageText(message.text)
                          : escapeHtml(message.text).replace(/\n/g, '<br/>'),
                    }}
                  />
                </div>
              ))}
            </div>

            <div className="chat-input-panel">
              <textarea
                rows="4"
                value={prompt}
                placeholder="Ask the research agent something like 'What is the latest growth strategy for Shopify?'"
                onChange={(e) => setPrompt(e.target.value)}
              />
              <button className="primary-button" onClick={handleSend} disabled={isProcessing}>
                {isProcessing ? 'Researching...' : 'Send'}
              </button>
            </div>
            {errorMessage && <div className="error-box">{errorMessage}</div>}
          </div>
        </div>

        <aside className="assistant-panel">
          <div className="workflow-card">
            <div className="workflow-title">Agent says...</div>
            <div className="workflow-copy">{currentStep.description}</div>
            <div className="stage-indicator">
              {STEPS.map((item) => (
                <div key={item.id} className={`step-pill ${step === item.id ? 'active' : ''}`}>
                  <span>{item.label}</span>
                </div>
              ))}
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${progressValue}%` }} />
              <div className={`progress-marker ${progressValue >= 25 ? 'active' : ''}`} style={{ left: '6%' }} />
              <div className={`progress-marker ${progressValue >= 65 ? 'active' : ''}`} style={{ left: '48%' }} />
              <div className={`progress-marker ${progressValue >= 100 ? 'active' : ''}`} style={{ left: '92%' }} />
            </div>
            <div className="avatar-stage compact-avatar">
              <div className="holo-overlay" />
              <div className="sparkle sparkle1" />
              <div className="sparkle sparkle2" />
              <div className="sparkle sparkle3" />
              <div className="sparkle sparkle4" />
              <div className={`samantha-physical ${avatarPositionClass}`}>
                <img
                  className={`samantha-avatar ${isProcessing ? 'active' : ''}`}
                  src="/samantha.jpg"
                  alt="Agent avatar"
                />
              </div>
              <div className="dialogue-box">
                <strong>Agent</strong>
                <p>{assistantQuote}</p>
              </div>
            </div>
            <div className="status-grid internal-status compact-status">
              <div className="status-pill">AI core: online</div>
              <div className="status-pill">Groq engine: connected</div>
              <div className="status-pill">Tavily pipeline: synced</div>
              <div className="status-pill">Research pipeline: ready</div>
            </div>
          </div>

          <div className="glass-card pink-card">
            <div className="card-heading">Live activity</div>
            <div className="activity-list">
              {activityFeed.map((event) => (
                <div key={event.id} className={`activity-item ${event.status}`}>
                  <span className="marker" />
                  <div>
                    <div className="activity-text">{event.text}</div>
                    <div className="activity-sub">{event.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>

      <footer className="footer-note">Use <strong>npm install</strong> inside <code>frontend</code> and run the React preview with <strong>npm run dev</strong>.</footer>
    </div>
  );
}

export default App;
