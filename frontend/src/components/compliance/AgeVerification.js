import React, { useState } from "react";

const AgeVerification = ({ onComplete }) => {
  const [isVerified, setIsVerified] = useState(false);
  const [showError, setShowError] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!isVerified) {
      setShowError(true);
      return;
    }

    setShowError(false);
    onComplete({ ageVerified: true, verificationDate: new Date().toISOString() });
  };

  const handleCheckboxChange = (e) => {
    setIsVerified(e.target.checked);
    if (e.target.checked) {
      setShowError(false);
    }
  };

  return (
    <div className="verification-step">
      <div className="step-header">
        <h2>Age Verification Required</h2>
        <p>You must be 18 years or older to access Throne Companions.</p>
      </div>

      <div className="verification-content">
        <div className="warning-notice">
          <div className="warning-icon">⚠️</div>
          <div className="warning-text">
            <strong>Adult Content Warning</strong>
            <p>This platform contains mature content and conversations intended for adults only. By proceeding, you confirm you are of legal age in your jurisdiction.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="verification-form">
          <div className="checkbox-container">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={isVerified}
                onChange={handleCheckboxChange}
                className="checkbox-input"
              />
              <span className="checkbox-checkmark"></span>
              <span className="checkbox-text">
                <strong>I certify that I am 18 years or older</strong> and of legal age to access adult content in my jurisdiction.
              </span>
            </label>
          </div>

          {showError && (
            <div className="error-message">
              <span className="error-icon">❌</span>
              You must verify your age to proceed.
            </div>
          )}

          <div className="button-container">
            <button 
              type="submit" 
              className={`continue-button ${isVerified ? 'enabled' : 'disabled'}`}
              disabled={!isVerified}
            >
              Continue
            </button>
          </div>
        </form>

        <div className="exit-option">
          <p>If you are under 18, please <a href="https://www.google.com" className="exit-link">exit this site</a>.</p>
        </div>
      </div>
    </div>
  );
};

export default AgeVerification;