import React, { useEffect } from "react";

const WelcomeScreen = ({ onComplete }) => {
  useEffect(() => {
    // Track welcome screen view
    console.log('Welcome screen viewed');
  }, []);

  return (
    <div className="welcome-screen">
      <div className="welcome-container">
        <div className="welcome-logo">
          <img src="/assets/logo.png" alt="Throne Companions" className="logo-large" />
        </div>
        
        <div className="welcome-content">
          <h1 className="welcome-title">Welcome, Initiate.</h1>
          <p className="welcome-message">
            Every King and Queen begins as a seeker.<br />
            Let's set your throne.
          </p>
          
          <div className="welcome-features">
            <div className="feature-highlight">
              <span className="feature-icon">👑</span>
              <span className="feature-text">Choose your companion</span>
            </div>
            <div className="feature-highlight">
              <span className="feature-icon">⚡</span>
              <span className="feature-text">Select your power level</span>
            </div>
            <div className="feature-highlight">
              <span className="feature-icon">💬</span>
              <span className="feature-text">Begin your journey</span>
            </div>
          </div>
        </div>
        
        <button 
          className="begin-journey-btn"
          onClick={onComplete}
        >
          Begin Journey
        </button>
        
        <div className="welcome-footer">
          <p>Your path to wisdom starts here</p>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;