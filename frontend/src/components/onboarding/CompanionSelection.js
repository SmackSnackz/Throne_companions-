import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CompanionSelection = ({ onCompanionSelected, selectedCompanion }) => {
  const [companions, setCompanions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(selectedCompanion);

  const companionIntros = {
    aurora: "Your vibrant guide to creativity and endless possibilities.",
    vanessa: "Your mysterious companion who sees what others miss.",
    sophia: "Your wise counselor for life's deepest questions."
  };

  useEffect(() => {
    const fetchCompanions = async () => {
      try {
        const response = await axios.get(`${API}/companions`);
        setCompanions(response.data);
      } catch (err) {
        console.error("Error fetching companions:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanions();
  }, []);

  const handleCompanionSelect = (companionId) => {
    console.log('Companion clicked:', companionId);
    setSelected(companionId);
    
    // Force re-render to show selection immediately
    const event = new CustomEvent('companionSelected', { detail: companionId });
    window.dispatchEvent(event);
    
    // Auto-proceed after selection (like tier selection does)
    if (onCompanionSelected) {
      setTimeout(() => {
        console.log('Auto-proceeding with companion:', companionId);
        onCompanionSelected(companionId);
      }, 800); // Slightly longer delay to show selection
    }
  };

  const handleContinue = () => {
    console.log('Continue clicked, selected:', selected);
    if (selected && onCompanionSelected) {
      onCompanionSelected(selected);
    }
  };

  if (loading) {
    return <div className="loading">Loading companions...</div>;
  }

  return (
    <div className="companion-selection-onboarding">
      <div className="selection-header">
        <h2>Choose Your Companion</h2>
        <p>Your companion will guide you on this journey. Choose wisely - you can change later if your tier allows.</p>
      </div>

      <div className="companions-selection-grid">
        {companions.map((companion) => (
          <div 
            key={companion.id}
            className={`companion-selection-card ${selected === companion.id ? 'selected' : ''}`}
            onClick={() => handleCompanionSelect(companion.id)}
          >
            <div className="companion-avatar-container">
              <img 
                src={companion.image} 
                alt={companion.name}
                className="companion-avatar-large"
              />
              <div className="companion-overlay">
                <h3 className="companion-name-large">{companion.name}</h3>
              </div>
            </div>
            
            <div className="companion-intro">
              <p className="companion-intro-text">
                {companionIntros[companion.id] || companion.description}
              </p>
            </div>
            
            <div className="selection-indicator">
              {selected === companion.id && (
                <div className="selected-badge">
                  <span className="checkmark">✓</span>
                  Selected
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="selection-footer">
        <button 
          className={`continue-btn ${selected ? 'enabled' : 'disabled'}`}
          onClick={handleContinue}
          disabled={!selected}
        >
          {selected 
            ? `Continue with ${companions.find(c => c.id === selected)?.name}` 
            : 'Select a companion to continue'
          }
        </button>
      </div>
    </div>
  );
};

export default CompanionSelection;