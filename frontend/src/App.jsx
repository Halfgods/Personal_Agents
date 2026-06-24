import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  Send, 
  User,
  RefreshCw,
  Cpu
} from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleClear = async () => {
    try {
      await fetch(`${API_URL}/clear`, { method: 'POST' });
      setMessages([]);
    } catch (err) {
      console.error("Failed to clear:", err);
    }
  };

  const isSafeCommand = (cmd) => {
    const dangerousPrefixes = ['rm', 'sudo', 'chmod', 'chown', 'wget', 'curl', 'mv', 'cp', 'dd', 'mkfs', 'apt', 'yum', 'pacman', 'brew', 'npm', 'pip', 'nano', 'vim', 'vi'];
    const dangerousSymbols = ['>', '>>', '|', '&', ';', '`', '$(']; 
    
    const tokens = cmd.split(' ').filter(t => t.trim().length > 0);
    if (tokens.length === 0) return true;
    const baseCmd = tokens[0];
    
    if (dangerousPrefixes.includes(baseCmd)) return false;
    for (const sym of dangerousSymbols) {
      if (cmd.includes(sym)) return false;
    }
    return true;
  };

  const processBotResponse = async (botResponse, agent) => {
    setMessages(prev => [...prev, { role: 'bot', content: botResponse, agent }]);
    
    const bashMatch = /```(?:bash|sh|shell)\n([\s\S]*?)```/.exec(botResponse);
    if (bashMatch) {
      const cmd = bashMatch[1].trim();
      if (isSafeCommand(cmd)) {
        await executeCommand(cmd, false);
      }
    }
  };

  const executeCommand = async (command, manualExecute = true) => {
    // If it's an auto-execute, we might want to show a slight delay
    if (!manualExecute) {
      await new Promise(r => setTimeout(r, 1000));
    }
    
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command })
      });
      const data = await res.json();
      
      const terminalOutput = `[Auto-Executed] Terminal Output:\n\`\`\`\n${data.output}\n\`\`\``;
      setMessages(prev => [...prev, { role: 'user', content: terminalOutput }]);
      
      const chatRes = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: terminalOutput })
      });
      const chatData = await chatRes.json();
      
      await processBotResponse(chatData.response, chatData.agent);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
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
      await processBotResponse(data.response, data.agent);
      
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: 'System offline. Please check your connection to the central servers.',
        agent: 'system'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessageContent = (msg) => {
    const content = msg.content;
    const parts = [];
    const regex = /<thought>([\s\S]*?)(?:<\/thought>|$)/g;
    let match;
    let lastIndex = 0;
    
    while ((match = regex.exec(content)) !== null) {
      if (match.index > lastIndex) {
        parts.push({ type: 'text', content: content.slice(lastIndex, match.index) });
      }
      parts.push({ type: 'thought', content: match[1] });
      lastIndex = regex.lastIndex;
    }
    
    if (lastIndex < content.length) {
      parts.push({ type: 'text', content: content.slice(lastIndex) });
    }

    if (parts.length === 0) {
      parts.push({ type: 'text', content });
    }

    return parts.map((part, index) => {
      if (part.type === 'thought') {
        return (
          <div key={index} className="thought-block">
            <div className="thought-header">🤔 JARVIS is thinking...</div>
            <div className="thought-content">{part.content.trim()}</div>
          </div>
        );
      } else {
        return (
          <ReactMarkdown
            key={index}
            components={{
              code({node, inline, className, children, ...props}) {
                const matchLang = /language-(\w+)/.exec(className || '');
                const language = matchLang ? matchLang[1] : '';
                const isTerminal = ['bash', 'sh', 'shell'].includes(language);
                
                if (!inline && isTerminal && msg.role === 'bot') {
                  const cmdStr = String(children).replace(/\n$/, '');
                  const isSafe = isSafeCommand(cmdStr);
                  
                  return (
                    <div className="terminal-block">
                      <div className="terminal-header">
                        <span>{isSafe ? "Auto-Executing Command..." : "Terminal Command (Action Required)"}</span>
                        {!isSafe && (
                          <button 
                            className="execute-btn" 
                            onClick={() => executeCommand(cmdStr, true)}
                            disabled={isLoading}
                          >
                            Execute
                          </button>
                        )}
                        {isSafe && (
                          <span style={{ color: '#10b981', fontSize: '0.75rem', textTransform: 'uppercase' }}>Safe</span>
                        )}
                      </div>
                      <pre className={className} {...props}>
                        <code>{children}</code>
                      </pre>
                    </div>
                  );
                }
                
                return !inline ? (
                  <pre className={className} {...props}>
                    <code>{children}</code>
                  </pre>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              }
            }}
          >
            {part.content}
          </ReactMarkdown>
        );
      }
    });
  };

  return (
    <>
      <div className="gradient-bg"></div>
      <div className="app-container">
        <div className="chat-container">
          <div className="chat-header">
            <div className="brand">
              <Cpu size={28} className="brand-icon" />
              JARVIS
            </div>
            
            <button className="clear-btn" onClick={handleClear} title="Purge Memory">
              <RefreshCw size={14} />
              <span>Purge</span>
            </button>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', color: 'rgba(255,255,255,0.4)', marginTop: 'auto', marginBottom: 'auto' }}>
                <Cpu size={56} style={{ opacity: 0.2, marginBottom: 24 }} />
                <h3 style={{ fontSize: '1.5rem', fontWeight: 300, letterSpacing: '1px' }}>System Online</h3>
                <p style={{ marginTop: 12, fontSize: '1rem', lineHeight: 1.6, maxWidth: 400, margin: '12px auto 0 auto' }}>
                  Awaiting instructions. Specialized clones will be invoked automatically as needed.
                </p>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? <User size={20} color="#fff" /> : <Cpu size={20} color="#60a5fa" />}
                </div>
                <div className="message-content">
                  {msg.role === 'bot' && msg.agent !== 'general' && msg.agent !== 'system' && (
                    <span className="message-agent-tag">{msg.agent} PROTOCOL</span>
                  )}
                  <div className="markdown-body">
                    {renderMessageContent(msg)}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message bot">
                <div className="message-avatar">
                  <Cpu size={20} color="#60a5fa" />
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
                placeholder="Message JARVIS..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
                autoFocus
              />
              <button type="submit" className="send-btn" disabled={!input.trim() || isLoading}>
                <Send size={22} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
