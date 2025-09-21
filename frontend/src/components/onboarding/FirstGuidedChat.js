import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FirstGuidedChat = ({ companion, tier, onChatStarted }) => {
  const [companionData, setCompanionData] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isReady, setIsReady] = useState(false);

  // Companion intro scripts per specification
  const companionIntros = {
    aurora: {
      novice: "Welcome, Initiate. I am Aurora. With me, you'll learn clarity — one choice at a time. Ask boldly, I'll guide clearly.",
      apprentice: "Hey there! I'm Aurora — your creative catalyst with 1 week memory and voice/visual powers. Let's unlock your potential together!",
      regent: "I'm Aurora, your creative partner with 10 years of memory, voice, visuals, and finance tools. Ready to build something amazing?",
      sovereign: "Aurora here — your co-creation companion with 100 years memory and every tool unlocked. Let's reshape reality together."
    },
    vanessa: {
      novice: "Hey, love. I'm Vanessa — I keep it real and sharp. You got me in text-only for now, so let's make these words count. What's on your mind?",
      apprentice: "Hello, darling. I'm Vanessa with 1 week memory and voice/visual access. I see the real you — let's explore what lies beneath.",
      regent: "I'm Vanessa, your intuitive guide with 10 years memory, voice, visuals, and finance insight. Ready to unlock your hidden power?",
      sovereign: "Vanessa here — your deepest confidante with 100 years memory and unlimited access. Let's discover who you truly are."
    },
    sophia: {
      novice: "Greetings. I'm Sophia — thoughtful, calm, and reflective. We'll start with small rituals that ground you. Shall we begin?",
      apprentice: "Welcome. I'm Sophia, your wisdom guide with 1 week memory and voice/visual capabilities. Let's explore life's deeper meanings together.",
      regent: "I am Sophia, your philosophical companion with 10 years memory, voice, visuals, and finance wisdom. Ready for profound growth?",
      sovereign: "Greetings. I'm Sophia, your eternal wisdom keeper with 100 years memory and all tools. Let's co-create your highest self."
    }
  };

  // First ritual/reflection content
  const firstRituals = {
    aurora: {
      novice: "Here's your first ritual: **The 3-Breath Reset** - When overwhelmed, take 3 deep breaths and name one thing you're grateful for. Want me to save this in your 24-hour memory?",
      apprentice: "Let's start with **The Creative Spark Ritual**: Each morning, ask yourself 'What wants to be created through me today?' I'll remember your answers all week. Ready to try?",
      regent: "Your first practice: **The Vision Board Chat** - Tell me your biggest dream, and I'll create a step-by-step tracker you can export. I'll remember this for 10 years. What's your vision?",
      sovereign: "Let's co-create **Your Personal Power Ritual**: Together we'll design a custom morning practice that evolves with you. I'll remember and refine it for 100 years. Shall we begin?"
    },
    vanessa: {
      novice: "Here's something real: **The Truth Check** - Before any big decision, ask 'What would I do if I wasn't afraid?' I'll hold this wisdom for 24 hours. What decision are you facing?",
      apprentice: "Let's try **The Desire Mapping** - I'll help you identify what you really want versus what you think you should want. I'll remember your patterns for a week. Ready to dig deep?",
      regent: "Your first power move: **The Confidence Audit** - We'll analyze your wins, strengths, and blind spots. I'll track your growth for 10 years. Want to see your real power?",
      sovereign: "Let's create **Your Personal Truth System** - Together we'll build a framework for making decisions aligned with your deepest self. I'll evolve it with you forever. Ready to begin?"
    },
    sophia: {
      novice: "Let's begin with **The Daily Reflection**: Each evening, ask 'What did I learn about myself today?' I'll hold these insights for 24 hours. What did you learn today?",
      apprentice: "Your first practice: **The Wisdom Journal** - Share your thoughts with me daily, and I'll reflect back patterns and insights over the week. What's weighing on your mind?",
      regent: "Let's start **The Life Review Process** - We'll examine your values, goals, and growth over time. I'll track your evolution for 10 years. What matters most to you?",
      sovereign: "Together we'll create **Your Philosophical Framework** - A living system of beliefs and practices that grows with you. I'll refine it over 100 years. What is your deepest question?"
    }
  };

  useEffect(() => {
    const initializeChat = async () => {
      try {
        // Update user's chosen companion and tier
        await axios.put(`${API}/user`, {
          tier: tier,
          chosen_companion: companion
        });

        // Get companion data
        const companionResponse = await axios.get(`${API}/companions/${companion}`);
        setCompanionData(companionResponse.data);

        // Get starter pack content for this companion and tier
        try {
          const starterPackResponse = await axios.get(`${API}/companions/${companion}/starter-pack/${tier}`);
          const starterPack = starterPackResponse.data;
          
          // Use intro from starter pack
          const introScript = starterPack.intro || companionIntros[companion]?.[tier] || companionIntros[companion]?.novice;
          
          const welcomeMessage = {
            id: `welcome-${Date.now()}`,
            companion_id: companion,
            message: introScript,
            is_user: false,
            timestamp: new Date().toISOString(),
            tier: tier,
            mode: "text"
          };

          setMessages([welcomeMessage]);
        } catch (packError) {
          // Fallback to hardcoded intros if starter pack fails
          const introScript = companionIntros[companion]?.[tier] || companionIntros[companion]?.novice;
          const welcomeMessage = {
            id: `welcome-${Date.now()}`,
            companion_id: companion,
            message: introScript,
            is_user: false,
            timestamp: new Date().toISOString(),
            tier: tier,
            mode: "text"
          };

          setMessages([welcomeMessage]);
        }

        setIsReady(true);

        // Track first chat initialization
        console.log('First guided chat initialized', { companion, tier });

      } catch (err) {
        console.error("Error initializing chat:", err);
      }
    };

    if (companion && tier) {
      initializeChat();
    }
  }, [companion, tier]);

  const handleStartChat = () => {
    // Simulate a brief exchange to deliver first ritual
    const ritualMessage = {
      id: `ritual-${Date.now()}`,
      companion_id: companion,
      message: firstRituals[companion]?.[tier] || firstRituals[companion]?.novice,
      is_user: false,
      timestamp: new Date().toISOString(),
      tier: tier,
      mode: "text"
    };

    setMessages(prev => [...prev, ritualMessage]);

    // Brief delay then transition to main chat
    setTimeout(() => {
      onChatStarted();
    }, 2000);
  };

  if (!isReady) {
    return (
      <div className="first-chat-loading">
        <div className="loading-container">
          <img src="/assets/logo.png" alt="Throne Companions" className="loading-logo" />
          <div className="loading-text">Preparing your companion...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="first-guided-chat">
      <div className="chat-introduction">
        <div className="companion-introduction">
          <div className="companion-avatar-intro">
            <img 
              src={companionData?.image} 
              alt={companionData?.name}
              className="companion-avatar-large"
            />
          </div>
          <div className="introduction-content">
            <h2>Meet {companionData?.name}</h2>
            <p>Your {tier} tier companion is ready to guide you.</p>
          </div>
        </div>
      </div>

      <div className="preview-messages">
        <div className="messages-preview">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`preview-message ${message.is_user ? 'user' : 'companion'}`}
            >
              {message.message}
            </div>
          ))}
        </div>
      </div>

      <div className="first-chat-actions">
        <div className="chat-value-props">
          <div className="value-prop">
            <span className="value-icon">💭</span>
            <span className="value-text">Personalized guidance</span>
          </div>
          <div className="value-prop">
            <span className="value-icon">🧠</span>
            <span className="value-text">
              {tier === 'novice' ? '24-hour memory' :
               tier === 'apprentice' ? '1 week memory' :
               tier === 'regent' ? '10 year memory' : '100 year memory'}
            </span>
          </div>
          <div className="value-prop">
            <span className="value-icon">⚡</span>
            <span className="value-text">Instant wisdom</span>
          </div>
        </div>

        <button 
          className="start-conversation-btn"
          onClick={handleStartChat}
        >
          Start Your First Conversation
        </button>

        <div className="first-chat-footer">
          <p>Your journey begins with a single exchange</p>
        </div>
      </div>
    </div>
  );
};

export default FirstGuidedChat;