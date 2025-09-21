import React, { useState } from "react";

const TermsAndPrivacy = ({ onComplete }) => {
  const [hasScrolled, setHasScrolled] = useState(false);
  const [accepted, setAccepted] = useState(false);

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    if (scrollTop + clientHeight >= scrollHeight - 50) { // Near bottom
      setHasScrolled(true);
    }
  };

  const handleAccept = () => {
    if (hasScrolled) {
      onComplete({ 
        termsAccepted: true, 
        acceptanceDate: new Date().toISOString(),
        ipAddress: 'client-side' // Would be collected server-side in production
      });
    }
  };

  return (
    <div className="terms-step">
      <div className="step-header">
        <h2>Terms of Service & Privacy Policy</h2>
        <p>Please read and accept our terms and privacy policy to continue.</p>
      </div>

      <div className="terms-content">
        <div className="document-container" onScroll={handleScroll}>
          <div className="document-section">
            <h3>Terms of Service</h3>
            
            <h4>1. Acceptance of Terms</h4>
            <p>By accessing Throne Companions, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using this service.</p>

            <h4>2. Use License</h4>
            <p>Permission is granted to temporarily access Throne Companions for personal, non-commercial transitory viewing only. This is the grant of a license, not a transfer of title, and under this license you may not:</p>
            <ul>
              <li>modify or copy the materials</li>
              <li>use the materials for any commercial purpose or for any public display</li>
              <li>attempt to reverse engineer any software contained on the website</li>
              <li>remove any copyright or other proprietary notations from the materials</li>
            </ul>

            <h4>3. User Conduct</h4>
            <p>You agree to use Throne Companions responsibly and in compliance with all applicable laws. You may not:</p>
            <ul>
              <li>Upload, post, or transmit any content that is illegal, harmful, threatening, abusive, or otherwise objectionable</li>
              <li>Impersonate any person or entity or misrepresent your affiliation</li>
              <li>Interfere with or disrupt the service or servers</li>
              <li>Attempt to gain unauthorized access to any part of the service</li>
            </ul>

            <h4>4. AI Companion Interactions</h4>
            <p>Our AI companions are artificial intelligence programs designed for entertainment and conversation. You understand that:</p>
            <ul>
              <li>Conversations are with AI, not real people</li>
              <li>AI responses are generated automatically and may not always be accurate</li>
              <li>We are not responsible for the content of AI-generated responses</li>
              <li>Conversations may be monitored for quality and safety purposes</li>
            </ul>

            <h4>5. Privacy Policy</h4>
            <p>Your privacy is important to us. This Privacy Policy explains how we collect, use, and protect your information.</p>

            <h4>Information We Collect:</h4>
            <ul>
              <li>Account information (username, email if provided)</li>
              <li>Conversation logs with AI companions</li>
              <li>Usage data and analytics</li>
              <li>Device and browser information</li>
            </ul>

            <h4>How We Use Your Information:</h4>
            <ul>
              <li>To provide and improve our service</li>
              <li>To personalize your experience with AI companions</li>
              <li>To ensure safety and prevent abuse</li>
              <li>To communicate with you about our service</li>
            </ul>

            <h4>Data Protection:</h4>
            <ul>
              <li>We use industry-standard security measures</li>
              <li>Your data is encrypted in transit and at rest</li>
              <li>We do not sell your personal information to third parties</li>
              <li>You may request deletion of your data at any time</li>
            </ul>

            <h4>6. Disclaimers</h4>
            <p>The materials on Throne Companions are provided on an 'as is' basis. Throne Companions makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.</p>

            <h4>7. Limitations</h4>
            <p>In no event shall Throne Companions or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on Throne Companions, even if Throne Companions or its authorized representative has been notified orally or in writing of the possibility of such damage.</p>

            <h4>8. Contact Information</h4>
            <p>If you have any questions about these Terms of Service or Privacy Policy, please contact us at: support@thronecompanions.com</p>
          </div>
        </div>

        <div className="acceptance-section">
          {!hasScrolled && (
            <div className="scroll-reminder">
              <span className="scroll-icon">👇</span>
              Please scroll to the bottom to read all terms before accepting.
            </div>
          )}
          
          <button 
            onClick={handleAccept}
            className={`accept-button ${hasScrolled ? 'enabled' : 'disabled'}`}
            disabled={!hasScrolled}
          >
            I Have Read and Accept the Terms of Service & Privacy Policy
          </button>
        </div>
      </div>
    </div>
  );
};

export default TermsAndPrivacy;