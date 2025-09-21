import React, { useState } from "react";

const DMCAPolicy = ({ onComplete }) => {
  const [acknowledged, setAcknowledged] = useState(false);

  const handleAcknowledge = () => {
    onComplete({ 
      dmcaAcknowledged: true, 
      acknowledgmentDate: new Date().toISOString() 
    });
  };

  return (
    <div className="dmca-step">
      <div className="step-header">
        <h2>DMCA & Content Policy</h2>
        <p>Please read and acknowledge our content policy and copyright compliance requirements.</p>
      </div>

      <div className="dmca-content">
        <div className="policy-section">
          <h3>1. Copyright Compliance</h3>
          <div className="policy-box">
            <p>We respect the intellectual property rights of others and require all users to do the same.</p>
          </div>
        </div>

        <div className="policy-section">
          <h3>2. Prohibited Content</h3>
          <div className="policy-box">
            <p>You may not upload, share, or distribute:</p>
            <ul>
              <li>Copyrighted material without authorization</li>
              <li>Illegal or abusive content</li>
              <li>Content that violates privacy rights</li>
              <li>Material harmful to minors or promoting hate or violence</li>
            </ul>
          </div>
        </div>

        <div className="policy-section">
          <h3>3. DMCA Takedown Requests</h3>
          <div className="policy-box">
            <p>If you believe content on this platform infringes your copyright, please send a DMCA notice to:</p>
            
            <div className="contact-info">
              <p><strong>Email:</strong> <a href="mailto:dmca@thronecompanions.com">dmca@thronecompanions.com</a></p>
            </div>

            <p><strong>Your notice must include:</strong></p>
            <ul>
              <li>Identification of the copyrighted work</li>
              <li>Identification of the infringing material (with URL if available)</li>
              <li>Your contact information</li>
              <li>A statement under penalty of perjury that you are authorized to act</li>
              <li>Your electronic or physical signature</li>
            </ul>
          </div>
        </div>

        <div className="policy-section">
          <h3>4. Enforcement</h3>
          <div className="policy-box">
            <p>We may remove or disable access to alleged infringing content and may terminate repeat offenders' accounts.</p>
          </div>
        </div>

        <div className="policy-section">
          <h3>5. User Acknowledgment</h3>
          <div className="policy-box">
            <p>By continuing, you acknowledge that you have read and agree to this DMCA & Content Policy.</p>
          </div>
        </div>

        <div className="acknowledgment-section">
          <div className="checkbox-container">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={acknowledged}
                onChange={(e) => setAcknowledged(e.target.checked)}
                className="checkbox-input"
              />
              <span className="checkbox-checkmark"></span>
              <span className="checkbox-text">
                <strong>I acknowledge and agree to comply</strong> with the DMCA & Content Policy. I understand that violations may result in account termination.
              </span>
            </label>
          </div>

          <button 
            onClick={handleAcknowledge}
            className={`acknowledge-button ${acknowledged ? 'enabled' : 'disabled'}`}
            disabled={!acknowledged}
          >
            I Acknowledge and Agree to Comply
          </button>
        </div>
      </div>
    </div>
  );
};

export default DMCAPolicy;