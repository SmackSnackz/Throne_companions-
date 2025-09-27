import React, { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

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
    
    // Check if user is admin (for demo, create admin token)
    const createDemoAuth = async () => {
      try {
        // For demo purposes, check if we have an admin token
        let token = localStorage.getItem('tc_jwt');
        if (!token) {
          // Create a demo user token (or admin for testing)
          const response = await axios.post(`${API}/auth/create-token`, {
            email: "demo@thronecompanions.com",
            role: "user" // Change to "admin" for testing admin features
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

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim() || sending) return;

    setSending(true);
    
    try {
      // Send user message
      await axios.post(`${API}/companions/${id}/messages`, {
        companion_id: id,
        message: newMessage.trim(),
        is_user: true
      });

      // Clear input
      setNewMessage("");

      // Fetch updated messages (includes both user message and companion response)
      const messagesResponse = await axios.get(`${API}/companions/${id}/messages`);
      setMessages(messagesResponse.data);

    } catch (err) {
      console.error("Error sending message:", err);
      // You might want to show an error message to the user here
    } finally {
      setSending(false);
    }
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
          <div ref={messagesEndRef} />
        </div>

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
      </div>
    </div>
  );
};

export default ChatPage;