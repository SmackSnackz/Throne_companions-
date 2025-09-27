import React, { useState } from "react";

const SolicitationPanel = ({ questions, starterPrompts, tag, companionName, onSubmit, onSkip, coaching, tier, features }) => {
  const [answers, setAnswers] = useState({});
  
  const handleAnswerChange = (questionIndex, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: value
    }));
  };
  
  const handleSubmit = (chosenStarter = null) => {
    onSubmit(answers, chosenStarter);
  };

  return (
    <div className="solicitation-panel">
      <div className="solicitation-header">
        <h3 className="solicitation-title">
          Let me understand what you need...
        </h3>
        <div className="solicitation-tag">{tag}</div>
        <button className="skip-solicitation" onClick={onSkip}>Skip ×</button>
      </div>

      {/* Tier-specific coaching message */}
      {coaching && (
        <div className="coaching-message">
          <div className="coaching-icon">💡</div>
          <div className="coaching-text">{coaching}</div>
        </div>
      )}

      <div className="solicitation-questions">
        {questions.map((question, index) => (
          <div key={index} className="question-group">
            <div className="question-text">{question}</div>
            <input
              type="text"
              className="question-input"
              placeholder="Your answer..."
              value={answers[index] || ""}
              onChange={(e) => handleAnswerChange(index, e.target.value)}
            />
          </div>
        ))}
      </div>

      <div className="starter-prompts">
        <div className="starters-label">Or choose a quick path:</div>
        <div className="starter-buttons">
          {starterPrompts.map((prompt, index) => (
            <div key={index} className="starter-button-container">
              <button
                className="starter-prompt-btn"
                onClick={() => handleSubmit(prompt)}
              >
                {prompt}
              </button>
              {/* Save prompt feature for Regent/Sovereign tiers */}
              {features?.save_prompt && (
                <button className="save-prompt-btn" title="Save this prompt">
                  📌
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Tier-specific features */}
      {features && (
        <div className="tier-features">
          {features.voice_toggle && (
            <button className="feature-btn">🎤 Voice Mode</button>
          )}
          {features.search_history && (
            <button className="feature-btn">🔍 Search History</button>
          )}
        </div>
      )}

      <div className="solicitation-footer">
        <button
          className="continue-btn"
          onClick={() => handleSubmit()}
        >
          Continue with {companionName}
        </button>
      </div>
    </div>
  );
};

export default SolicitationPanel;