import React, { useState } from "react";

const SolicitationPanel = ({ questions, starterPrompts, tag, onSubmit, companionName }) => {
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
      </div>

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
            <button
              key={index}
              className="starter-prompt-btn"
              onClick={() => handleSubmit(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

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