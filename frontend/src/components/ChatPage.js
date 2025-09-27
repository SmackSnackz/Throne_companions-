import React, { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import SolicitationPanel from "./SolicitationPanel";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const FREE_LIMIT = 20;

const ChatPage = () => {
  const { id } = useParams();
  const [companion, setCompanion] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState("");
  const [usedCount, setUsedCount] = useState(0);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [solicitation, setSolicitation] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Generate or get session ID
    let sid = localStorage.getItem('tc_session_id');
    if (!sid) {
      sid = `s_${Math.random().toString(36).slice(2)}_${Date.now()}`;
      localStorage.setItem('tc_session_id', sid);
    }
    setSessionId(sid);
    
    // Check if user has an existing admin token, otherwise create user token
    const createDemoAuth = async () => {
      try {
        let token = localStorage.getItem('tc_jwt');
        if (!token) {
          // Create a regular user token for public users
          const response = await axios.post(`${API}/auth/create-token`, {
            email: "user@thronecompanions.com",
            role: "user" // Public users are regular users
          });
          token = response.data.token;
          localStorage.setItem('tc_jwt', token);
        }
        
        // Verify token and get user info
        const verifyResponse = await axios.get(`${API}/auth/verify`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setIsAdmin(verifyResponse.data.is_admin);
      } catch (err) {
        console.error("Auth setup failed:", err);
      }
    };
    
    createDemoAuth();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchCompanionAndMessages = async () => {
      try {
        // Fetch companion data
        const companionResponse = await axios.get(`${API}/companions/${id}`);
        setCompanion(companionResponse.data);

        // Fetch messages
        const messagesResponse = await axios.get(`${API}/companions/${id}/messages`);
        setMessages(messagesResponse.data);
      } catch (err) {
        setError("Failed to load companion or messages");
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchCompanionAndMessages();
    }
  }, [id]);

  const sendMessage = async (e, solicitationAnswers = null, chosenStarter = null) => {
    if (e) e.preventDefault();
    
    if ((!newMessage.trim() && !chosenStarter) || sending || !sessionId) return;

    setSending(true);
    setSolicitation(null); // Clear any pending solicitation
    
    try {
      const token = localStorage.getItem('tc_jwt') || '';
      
      // Prepare request payload
      const requestData = {
        companion_id: id,
        message: chosenStarter || newMessage.trim(),
        session_id: sessionId
      };
      
      // Add solicitation data if provided
      if (solicitationAnswers) {
        requestData.solicitation_answers = solicitationAnswers;
      }
      if (chosenStarter) {
        requestData.chosen_starter = chosenStarter;
      }
      
      // Use new chat endpoint
      const response = await axios.post(`${API}/chat`, requestData, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        }
      });

      const data = response.data;
      
      // Check if we got a solicitation response
      if (data.type === 'solicitation') {
        setSolicitation(data);
        setSending(false);
        return;
      }
      
      // Add user message to display
      const userMsg = {
        id: `user-${Date.now()}`,
        message: chosenStarter || newMessage.trim(),
        is_user: true,
        timestamp: new Date().toISOString()
      };
      
      // Add companion response to display  
      const companionMsg = {
        id: `companion-${Date.now()}`,
        message: data.reply,
        is_user: false,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, userMsg, companionMsg]);
      setNewMessage("");
      
      // Update usage stats
      if (data.used !== undefined) setUsedCount(data.used);
      if (data.upgrade) setShowUpgrade(true);
      
    } catch (err) {
      console.error("Error sending message:", err);
      const errorMsg = {
        id: `error-${Date.now()}`,
        message: "Sorry, I'm having trouble responding right now. Please try again.",
        is_user: false,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setSending(false);
    }
  };
  
  const handleSolicitationSubmit = (answers, chosenStarter = null) => {
    sendMessage(null, answers, chosenStarter);
  };

  if (loading) {
    return <div className="loading">Loading companion...</div>;
  }

  if (error || !companion) {
    return <div className="error">{error || "Companion not found"}</div>;
  }

  return (
    <div className="chat-container">
      <div className={`chat-header ${companion.id}-chat`}>
        <img 
          src={companion.image} 
          alt={companion.name}
          className="chat-backdrop"
        />
        <Link to="/companions" className="back-button">
          ← Back to Companions
        </Link>
        <div className="chat-header-content">
          <h1 className="chat-companion-name">{companion.name}</h1>
          <p className="chat-companion-status">Ready to chat</p>
          {isAdmin && <span className="admin-badge">Admin Mode</span>}
          {!isAdmin && (
            <p className="usage-counter">
              {usedCount} of {FREE_LIMIT} free messages used
            </p>
          )}
        </div>
      </div>

      <div className="chat-content">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div style={{ textAlign: "center", color: "var(--throne-silver)", padding: "2rem" }}>
              <p>Start a conversation with {companion.name}!</p>
              <p style={{ fontSize: "0.9rem", marginTop: "0.5rem", opacity: 0.8 }}>
                {companion.description}
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div 
                key={message.id} 
                className={`message ${message.is_user ? 'user' : 'companion'}`}
              >
                {message.message}
              </div>
            ))
          )}
          {sending && <div className="message companion typing">Typing...</div>}
          <div ref={messagesEndRef} />
        </div>

        {/* Solicitation Panel */}
        {solicitation && (
          <SolicitationPanel
            questions={solicitation.questions}
            starterPrompts={solicitation.starter_prompts}
            tag={solicitation.tag}
            companionName={companion.name}
            onSubmit={handleSolicitationSubmit}
          />
        )}

        {/* Regular Message Input */}
        {!solicitation && (
          <form onSubmit={sendMessage} className="message-input-container">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder={`Message ${companion.name}...`}
              className="message-input"
              disabled={sending}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={sending || !newMessage.trim()}
            >
              {sending ? "Sending..." : "Send"}
            </button>
          </form>
        )}
      </div>

      {showUpgrade && (
        <div className="upgrade-modal-overlay">
          <div className="upgrade-modal">
            <h3>Continue Your Journey</h3>
            <p>You've reached the free message limit. Upgrade to continue chatting with {companion?.name}.</p>
            <div className="upgrade-buttons">
              <Link to="/tiers" className="upgrade-btn primary">
                Upgrade Now
              </Link>
              <button 
                className="upgrade-btn secondary"
                onClick={() => setShowUpgrade(false)}
              >
                Save Conversation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPage;