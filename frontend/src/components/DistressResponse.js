import React from "react";
import tracker from "../utils/mixpanel";

const DistressResponse = ({ response, companionName, onExpansionRequest, onContinue }) => {
  const handleExpansionClick = () => {
    if (onExpansionRequest) {
      onExpansionRequest("go deeper");
    }
  };

  return (
    <div className="distress-response">
      <div className="distress-header">
        <h3 className="distress-title">
          {companionName} understands...
        </h3>
        <div className="distress-tag">{response.tag}</div>
      </div>

      <div className="distress-content">
        {/* Step 1: Acknowledge */}
        <div className="distress-section acknowledge">
          <div className="distress-icon">🤝</div>
          <p>{response.acknowledge}</p>
        </div>

        {/* Step 2: Re-anchor */}
        <div className="distress-section reanchor">
          <div className="distress-icon">🎯</div>
          <p><strong>{response.reanchor}</strong></p>
        </div>

        {/* Step 3: Next Steps */}
        <div className="distress-section nextsteps">
          <div className="distress-icon">📋</div>
          <div>
            <p className="steps-intro">{response.steps_intro}</p>
            <ol className="next-steps-list">
              {response.next_steps.map((step, index) => (
                <li key={index} className="step-item">{step}</li>
              ))}
            </ol>
          </div>
        </div>
      </div>

      <div className="distress-footer">
        {response.expansion_available && (
          <button 
            className="expansion-btn"
            onClick={handleExpansionClick}
          >
            Go Deeper
          </button>
        )}
        <button 
          className="continue-btn"
          onClick={onContinue}
        >
          Continue with {companionName}
        </button>
      </div>
    </div>
  );
};

export default DistressResponse;