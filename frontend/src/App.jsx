import "./App.css";
import axios from "axios";
import {
  Activity,
  Archive,
  Check,
  ChevronDown,
  ChevronRight,
  CircleAlert,
  FileText,
  Menu,
  MessageSquare,
  Mic,
  Plus,
  Search,
  Send,
  Settings,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
const API = import.meta.env.DEV
  ? (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000")
  : "";
const AGENTFLOW_TOKEN = import.meta.env.DEV
  ? import.meta.env.VITE_AGENTFLOW_TOKEN
  : undefined;
const STORAGE_KEY = "agentflow.conversations.v2";
function createConversation() {
  return {
    id: crypto.randomUUID(),
    title: "New conversation",
    createdAt: Date.now(),
    messages: [],
    steps: [],
  };
}
function getConversationTitle(text) {
  const clean = text.replace(/\s+/g, " ").trim();
  if (!clean) return "New conversation";
  return clean.length > 34 ? `${clean.slice(0, 34)}…` : clean;
}
function groupConversations(conversations) {
  const now = new Date();
  const today = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate()
  ).getTime();
  const yesterday = today - 86400000;
  const week = today - 6 * 86400000;
  return {
    Today: conversations.filter((c) => c.createdAt >= today),
    Yesterday: conversations.filter(
      (c) => c.createdAt >= yesterday && c.createdAt < today
    ),
    "Previous 7 days": conversations.filter(
      (c) => c.createdAt >= week && c.createdAt < yesterday
    ),
    Older: conversations.filter((c) => c.createdAt < week),
  };
}
function ExecutionCard({ steps, busy }) {
  const [open, setOpen] = useState(true);
  if (!steps?.length && !busy) return null;
  const completed = steps.filter((s) => s.status === "success").length;
  const failed = steps.some((s) => s.status === "failed");
  const total = steps.length;
  return (
    <div className={`execution-card ${failed ? "has-error" : ""}`}>
      <button
        className="execution-header"
        onClick={() => setOpen((v) => !v)}
      >
        <span
          className={`execution-orb ${
            busy ? "running" : failed ? "failed" : "done"
          }`}
        >
          {failed ? (
            <CircleAlert size={15} />
          ) : busy ? (
            <Activity size={15} />
          ) : (
            <Check size={15} />
          )}
        </span>
        <span className="execution-title">
          {busy
            ? "Agent is working"
            : failed
              ? "Task needs attention"
              : "Task completed"}
        </span>
        <span className="execution-meta">
          {total ? `${completed}/${total} actions` : "Preparing"}
        </span>
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </button>
      {open && (
        <div className="execution-body">
          {steps.map((step, index) => (
            <div
              className="execution-step"
              key={`${step.description}-${index}`}
            >
              <span className={`step-status ${step.status}`}>
                {step.status === "success" ? (
                  <Check size={13} />
                ) : (
                  <X size={13} />
                )}
              </span>
              <div className="step-copy">
                <span>
                  {step.description || step.action?.type || "Action"}
                </span>
                {step.result && <small>{String(step.result)}</small>}
              </div>
            </div>
          ))}
          {busy && (
            <div className="execution-live">
              <span />
              Executing the current plan
            </div>
          )}
        </div>
      )}
    </div>
  );
}
function Message({ message, steps, busy }) {
  if (message.role === "user") {
    return (
      <div className="message-row user-row">
        <div className="user-message">{message.text}</div>
      </div>
    );
  }
  return (
    <div className="message-row assistant-row">
      <div className="assistant-mark">
        <Sparkles size={16} />
      </div>
      <div className="assistant-content">
        <div className="assistant-name">AgentFlow</div>
        <div className="assistant-text">{message.text}</div>
        {steps?.length > 0 && (
          <ExecutionCard steps={steps} busy={busy} />
        )}
      </div>
    </div>
  );
}
export default function App() {
  const [conversations, setConversations] = useState(() => {
    try {
      const saved = JSON.parse(
        localStorage.getItem(STORAGE_KEY) || "[]"
      );
      return saved.length ? saved : [createConversation()];
    } catch {
      return [createConversation()];
    }
  });
  const [activeId, setActiveId] = useState(() => {
    try {
      const saved = JSON.parse(
        localStorage.getItem(STORAGE_KEY) || "[]"
      );
      return saved[0]?.id || null;
    } catch {
      return null;
    }
  });
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [search, setSearch] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [error, setError] = useState("");
  const endRef = useRef(null);
  const activeConversation =
    conversations.find((c) => c.id === activeId) || conversations[0];
  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(conversations)
    );
  }, [conversations]);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeConversation?.messages, busy]);
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return conversations;
    return conversations.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.messages.some((m) =>
          m.text.toLowerCase().includes(q)
        )
    );
  }, [conversations, search]);
  const groups = groupConversations(filtered);
  function updateConversation(id, updater) {
    setConversations((items) =>
      items.map((c) => (c.id === id ? updater(c) : c))
    );
  }
  function newChat() {
    const conversation = createConversation();
    setConversations((items) => [conversation, ...items]);
    setActiveId(conversation.id);
    setInput("");
    setError("");
    if (window.innerWidth < 900) {
      setSidebarOpen(false);
    }
  }
  function deleteConversation(id) {
    setConversations((items) => {
      const remaining = items.filter((c) => c.id !== id);
      if (!remaining.length) {
        const fresh = createConversation();
        setActiveId(fresh.id);
        return [fresh];
      }
      if (id === activeId) {
        setActiveId(remaining[0].id);
      }
      return remaining;
    });
  }
  function startVoiceInput() {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError(
        "Speech recognition is not supported in this browser."
      );
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onstart = () => setListening(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) =>
        prev ? `${prev} ${transcript}` : transcript
      );
    };
    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);
    recognition.start();
  }
  async function sendMessage(e) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || busy || !activeConversation) return;
    if (import.meta.env.DEV && !AGENTFLOW_TOKEN) {
      setError(
        "Missing local test token. Configure VITE_AGENTFLOW_TOKEN in frontend/.env.local and restart Vite."
      );
      return;
    }
    setError("");
    setInput("");
    setBusy(true);
    const id = activeConversation.id;
    updateConversation(id, (conversation) => ({
      ...conversation,
      title:
        conversation.messages.length === 0
          ? getConversationTitle(text)
          : conversation.title,
      messages: [
        ...conversation.messages,
        { role: "user", text },
      ],
      steps: [],
    }));
    try {
      const res = await axios.post(
        `${API}/api/chat`,
        {
          message: text,
          session_id: id,
        },
        {
          ...(AGENTFLOW_TOKEN
            ? { headers: { "x-agentflow-token": AGENTFLOW_TOKEN } }
            : {}),
          timeout: 65000,
        }
      );
      const reply = res.data.message || "Task completed.";
      const steps = res.data.steps || [];
      updateConversation(id, (conversation) => ({
        ...conversation,
        messages: [
          ...conversation.messages,
          { role: "assistant", text: reply, steps },
        ],
        steps,
      }));
    } catch (err) {
      const errorMessage =
        err.response?.data?.detail ||
        (err.response
          ? `AgentFlow returned HTTP ${err.response.status}.`
          : "I couldn't reach the AgentFlow backend. Make sure the backend is running.");
      setError(errorMessage);
      updateConversation(id, (conversation) => ({
        ...conversation,
        messages: [
          ...conversation.messages,
          {
            role: "assistant",
            text: errorMessage,
            error: true,
          },
        ],
      }));
    } finally {
      setBusy(false);
    }
  }
  function selectConversation(id) {
    setActiveId(id);
    setError("");
    if (window.innerWidth < 900) {
      setSidebarOpen(false);
    }
  }
  function renderGroup(title, items) {
    if (!items.length) return null;
    return (
      <div className="history-group" key={title}>
        <div className="history-label">{title}</div>
        {items.map((conversation) => (
          <div
            className={`conversation-item ${
              conversation.id === activeConversation?.id
                ? "active"
                : ""
            }`}
            key={conversation.id}
          >
            <button
              className="conversation-main"
              onClick={() => selectConversation(conversation.id)}
            >
              <MessageSquare size={15} />
              <span>{conversation.title}</span>
            </button>
            <button
              className="conversation-menu"
              title="Delete conversation"
              onClick={() => deleteConversation(conversation.id)}
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>
    );
  }
  const hasMessages =
    activeConversation?.messages?.length > 0;
  return (
    <div className="app-shell">
      <aside
        className={`sidebar ${sidebarOpen ? "open" : "closed"}`}
      >
        <div className="brand">
          <div className="brand-mark">
            <Sparkles size={18} />
          </div>
          <div className="brand-copy">
            <strong>AgentFlow</strong>
            <span>Computer automation</span>
          </div>
        </div>
        <button className="new-chat" onClick={newChat}>
          <Plus size={17} />
          <span>New conversation</span>
        </button>
        <div className="search-box">
          <Search size={16} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search conversations"
          />
        </div>
        <div className="history">
          {renderGroup("Today", groups.Today)}
          {renderGroup("Yesterday", groups.Yesterday)}
          {renderGroup(
            "Previous 7 days",
            groups["Previous 7 days"]
          )}
          {renderGroup("Older", groups.Older)}
          {!filtered.length && (
            <div className="empty-history">
              No conversations found.
            </div>
          )}
        </div>
        <div className="sidebar-footer">
          <button>
            <Settings size={16} />
            Settings
          </button>
          <button>
            <Archive size={16} />
            About AgentFlow
          </button>
        </div>
      </aside>
      {!sidebarOpen && (
        <div
          className="mobile-overlay"
          onClick={() => setSidebarOpen(true)}
        />
      )}
      <section className="chat-shell">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="icon-button mobile-menu"
              onClick={() => setSidebarOpen((v) => !v)}
              title="Toggle sidebar"
            >
              <Menu size={19} />
            </button>
            <div className="conversation-heading">
              <strong>
                {activeConversation?.title || "AgentFlow"}
              </strong>
              <span>
                {busy
                  ? "Working on your request"
                  : "Private local computer assistant"}
              </span>
            </div>
          </div>
          <div className={`status-pill ${busy ? "working" : ""}`}>
            <span />
            {busy ? "Working" : "Ready"}
          </div>
        </header>
        <main className="chat-area">
          {!hasMessages ? (
            <div className="welcome">
              <div className="welcome-mark">
                <Sparkles size={22} />
              </div>
              <h1>How can I help?</h1>
              <p>
                Tell AgentFlow what you want to do on your computer.
              </p>
              <div className="suggestions">
                {[
                  [
                    "Open Calculator",
                    "Open Calculator and add 203 and 34.",
                  ],
                  [
                    "Search the web",
                    "Open Chrome and search for artificial intelligence.",
                  ],
                  [
                    "Create a file",
                    "Create a text file called notes.txt on my Desktop.",
                  ],
                  [
                    "Write a document",
                    "Open Word and write a paragraph about APJ Abdul Kalam.",
                  ],
                ].map(([label, prompt]) => (
                  <button
                    key={label}
                    onClick={() => setInput(prompt)}
                  >
                    <FileText size={16} />
                    <span>{label}</span>
                    <ChevronRight size={15} />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="conversation">
              {activeConversation.messages.map(
                (message, index) => (
                  <Message
                    key={`${activeConversation.id}-${index}`}
                    message={message}
                    steps={
                      message.role === "assistant"
                        ? message.steps
                        : null
                    }
                    busy={
                      busy &&
                      index ===
                        activeConversation.messages.length - 1 &&
                      message.role === "assistant"
                    }
                  />
                )
              )}
              {busy && (
                <div className="message-row assistant-row working-message">
                  <div className="assistant-mark">
                    <Sparkles size={16} />
                  </div>
                  <div className="assistant-content">
                    <div className="assistant-name">AgentFlow</div>
                    <div className="typing">
                      <span />
                      <span />
                      <span />
                    </div>
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>
          )}
        </main>
        <div className="composer-wrap">
          {error && (
            <div className="error-banner">
              <CircleAlert size={15} />
              {error}
            </div>
          )}
          <form className="composer" onSubmit={sendMessage}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(e);
                }
              }}
              placeholder="Message AgentFlow..."
              rows={1}
              disabled={busy}
            />
            <div className="composer-actions">
              <button
                type="button"
                className={`composer-icon ${
                  listening ? "listening" : ""
                }`}
                onClick={startVoiceInput}
                title="Voice input"
              >
                <Mic size={18} />
              </button>
              <button
                type="submit"
                className="send-button"
                disabled={busy || !input.trim()}
                title="Send message"
              >
                <Send size={17} />
              </button>
            </div>
          </form>
          <div className="composer-note">
            AgentFlow can interact with applications and files on this computer.
          </div>
        </div>
      </section>
    </div>
  );
}
