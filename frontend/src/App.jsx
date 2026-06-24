import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  ShieldCheck, 
  Send, 
  Trash2, 
  Bot, 
  User,
  Calendar,
  Leaf,
  PartyPopper,
  Pill,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000';

const AGENT_ICONS = {
  general: <Sparkles />,
  scheduler: <Calendar />,
  gardener: <Leaf />,
  party: <PartyPopper />,
  medicator: <Pill />,
};

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [agents, setAgents] = useState([]);
  const [activeAgent, setActiveAgent] = useState('general');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API_URL}/agents`);
      if (res.ok) {
        const data = await res.json();
        setAgents(data);
      }
    } catch (err) {
      console.error("Failed to fetch agents:", err);
      // Fallback
      setAgents([
        { name: 'general', description: 'General Q&A and everyday tasks' },
        { name: 'scheduler', description: 'Schedule, tasks, and calendar' },
        { name: 'gardener', description: 'Garden and crop planning' },
        { name: 'party', description: 'Party and event planning' },
        { name: 'medicator', description: 'Medication management' }
      ]);
    }
  };

  const handleClear = async () => {
    try {
      await fetch(`${API_URL}/clear`, { method: 'POST' });
      setMessages([]);
    } catch (err) {
      console.error("Failed to clear:", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });
      
      const data = await res.json();
      
      setActiveAgent(data.agent);
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: data.response,
        agent: data.agent
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: 'Sorry, I encountered a network error while connecting to the local server. Make sure the Python backend is running on port 8000.',
        agent: 'system'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="brand">
            <Bot size={28} color="#60a5fa" />
            Concierge Agents
          </div>
          <div className="privacy-badge">
            <ShieldCheck size={14} />
            100% Local & Private
          </div>
        </div>
        
        <div className="agent-list">
          {agents.map(agent => (
            <div 
              key={agent.name} 
              className={`agent-item ${agent.name} ${activeAgent === agent.name ? 'active' : ''}`}
            >
              <div className="agent-icon-wrapper">
                {AGENT_ICONS[agent.name] || <Bot />}
              </div>
              <div className="agent-info">
                <h3>{agent.name}</h3>
                <p>{agent.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-container">
        <div className="chat-header">
          <div className="active-agent-display">
            <div className="agent-icon-wrapper" style={{ width: 40, height: 40, background: 'rgba(255,255,255,0.1)', color: 'var(--text-main)' }}>
              {AGENT_ICONS[activeAgent] || <Bot />}
            </div>
            <h2>{activeAgent} Agent</h2>
          </div>
          
          <button className="clear-btn" onClick={handleClear} title="Clear Context">
            <RefreshCw size={16} />
            <span>Reset</span>
          </button>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: 'auto', marginBottom: 'auto' }}>
              <Bot size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
              <h3>How can we assist you today?</h3>
              <p style={{ marginTop: 8, fontSize: '0.9rem' }}>
                Type your request below. Our agentic routing will automatically<br/>assign the best specialized agent to help you.
              </p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'user' ? <User size={20} color="#fff" /> : (AGENT_ICONS[msg.agent] || <Bot size={20} color="#fff" />)}
              </div>
              <div className="message-content">
                {msg.role === 'bot' && (
                  <span className="message-agent-tag">{msg.agent} replied</span>
                )}
                <div className="markdown-body">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message bot">
              <div className="message-avatar">
                {AGENT_ICONS[activeAgent] || <Bot size={20} color="#fff" />}
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <form className="chat-input-wrapper" onSubmit={handleSubmit}>
            <input
              type="text"
              className="chat-input"
              placeholder="Ask for gardening advice, plan a party, or manage your schedule..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
