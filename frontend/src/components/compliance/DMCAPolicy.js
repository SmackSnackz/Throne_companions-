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
        <h2>Content Policy & DMCA Compliance</h2>
        <p>Please acknowledge our content policy and copyright compliance requirements.</p>
      </div>

      <div className="dmca-content">
        <div className="policy-section">
          <h3>🚫 Prohibited Content</h3>
          <div className="policy-box">
            <p><strong>The following content is strictly prohibited on Throne Companions:</strong></p>
            <ul>
              <li>Copyrighted material without permission</li>
              <li>Illegal content of any kind</li>
              <li>Content that infringes on intellectual property rights</li>
              <li>Harassment, threats, or abusive content</li>
              <li>Spam or commercial solicitation</li>
              <li>Malicious software or harmful code</li>
            </ul>
          </div>
        </div>

        <div className="policy-section">
          <h3>⚖️ DMCA Compliance</h3>
          <div className="policy-box">
            <p><strong>Digital Millennium Copyright Act (DMCA) Notice:</strong></p>
            <p>We respect intellectual property rights and comply with the DMCA. If you believe your copyrighted work has been used inappropriately:</p>
            
            <div className="contact-info">
              <h4>File a DMCA Takedown Request:</h4>
              <p><strong>Email:</strong> <a href="mailto:dmca@thronecompanions.com">dmca@thronecompanions.com</a></p>
              <p><strong>Subject Line:</strong> DMCA Takedown Request</p>
            </div>

            <h4>Required Information:</h4>
            <ul>
              <li>Description of the copyrighted work claimed to be infringed</li>
              <li>Location of the infringing material on our platform</li>
              <li>Your contact information (name, address, phone, email)</li>
              <li>Statement of good faith belief that use is not authorized</li>
              <li>Statement that information is accurate and you are authorized to act</li>
              <li>Your physical or electronic signature</li>
            </ul>
          </div>
        </div>

        <div className="policy-section">
          <h3>🛡️ User Responsibility</h3>
          <div className="policy-box">
            <p><strong>By using Throne Companions, you agree to:</strong></p>
            <ul>
              <li>Only share content you own or have permission to use</li>
              <li>Respect others' intellectual property rights</li>
              <li>Report any copyright infringement you discover</li>
              <li>Comply with all applicable laws and regulations</li>
              <li>Accept responsibility for all content you create or share</li>
            </ul>
          </div>
        </div>

        <div className="policy-section">
          <h3>⚡ Enforcement</h3>
          <div className="policy-box">
            <p>Violations of this policy may result in:</p>
            <ul>
              <li>Content removal</li>
              <li>Account suspension or termination</li>
              <li>Legal action when appropriate</li>
              <li>Cooperation with law enforcement</li>
            </ul>
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
                <strong>I acknowledge and agree to comply</strong> with the Content Policy and DMCA requirements. I understand that violations may result in account termination.
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