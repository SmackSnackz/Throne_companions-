import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const OnboardingTierSelection = ({ onTierSelected, selectedTier = "novice", isOnboarding = false }) => {
  const [tiers, setTiers] = useState({});
  const [loading, setLoading] = useState(true);
  const [currentTier, setCurrentTier] = useState(selectedTier);

  useEffect(() => {
    const fetchTiers = async () => {
      try {
        const response = await axios.get(`${API}/tiers`);
        setTiers(response.data);
      } catch (err) {
        console.error("Error fetching tiers:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTiers();
  }, []);

  const handleTierSelect = (tierKey) => {
    setCurrentTier(tierKey);
    
    // For free tier, proceed immediately
    if (tierKey === "novice") {
      onTierSelected(tierKey);
    } else {
      // For paid tiers, just select for now (payment integration comes later)
      // But still allow proceeding for testing
      onTierSelected(tierKey);
    }
  };

  if (loading) {
    return <div className="loading">Loading tiers...</div>;
  }

  const tierOrder = ["novice", "apprentice", "regent", "sovereign"];

  return (
    <div className="tier-selection-onboarding">
      <div className="tier-header">
        <h2>Choose Your Path</h2>
        <p>Start with Novice (Free) and upgrade anytime. Each tier unlocks new powers.</p>
      </div>

      <div className="tiers-onboarding-grid">
        {tierOrder.map((tierKey) => {
          const tier = tiers[tierKey];
          if (!tier) return null;

          const isSelected = currentTier === tierKey;
          const isRecommended = tierKey === "novice";

          return (
            <div 
              key={tierKey} 
              className={`tier-onboarding-card ${tierKey} ${isSelected ? 'selected' : ''} ${isRecommended ? 'recommended' : ''}`}
              onClick={() => handleTierSelect(tierKey)}
            >
              {isRecommended && (
                <div className="recommended-badge">
                  <span>Start Here</span>
                </div>
              )}

              <div className="tier-card-header">
                <h3 className="tier-name">{tier.display_name}</h3>
                <div className="tier-price">
                  {tier.price === 0 ? 'Free Forever' : `$${tier.price}/month`}
                </div>
              </div>

              <div className="tier-key-features">
                <div className="key-feature">
                  <span className="feature-icon">🧠</span>
                  <span className="feature-text">
                    {tier.memory_retention_days === 36500 ? '100 years memory' : 
                     tier.memory_retention_days === 3650 ? '10 years memory' : 
                     tier.memory_retention_days === 7 ? '1 week memory' : '24 hour memory'}
                  </span>
                </div>

                <div className="key-feature">
                  <span className="feature-icon">💬</span>
                  <span className="feature-text">
                    {tier.allowed_modes.includes('all') ? 'All communication modes' :
                     tier.allowed_modes.length === 1 ? 'Text only' :
                     `${tier.allowed_modes.length} communication modes`}
                  </span>
                </div>

                <div className="key-feature">
                  <span className="feature-icon">⚡</span>
                  <span className="feature-text">
                    {tier.prompting_mastery} level mastery
                  </span>
                </div>

                {tier.tools_enabled.length > 0 && (
                  <div className="key-feature">
                    <span className="feature-icon">🛠️</span>
                    <span className="feature-text">
                      {tier.tools_enabled.length} tools included
                    </span>
                  </div>
                )}
              </div>

              <div className="tier-selection-footer">
                {isSelected && (
                  <div className="selected-indicator">
                    <span className="checkmark">✓</span>
                    Selected
                  </div>
                )}
                {!isSelected && (
                  <button 
                    className="select-tier-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTierSelect(tierKey);
                    }}
                  >
                    {tier.price === 0 ? 'Start Free' : 'Choose Plan'}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="tier-benefits">
        <h3>Why start with Novice?</h3>
        <div className="benefits-grid">
          <div className="benefit">
            <span className="benefit-icon">🆓</span>
            <span className="benefit-text">Completely free forever</span>
          </div>
          <div className="benefit">
            <span className="benefit-icon">🚀</span>
            <span className="benefit-text">Get started immediately</span>
          </div>
          <div className="benefit">
            <span className="benefit-icon">⬆️</span>
            <span className="benefit-text">Upgrade anytime with one click</span>
          </div>
        </div>
      </div>

      {isOnboarding && (
        <div className="onboarding-tier-footer">
          <button 
            className="continue-with-tier-btn"
            onClick={() => handleTierSelect(currentTier)}
          >
            Continue with {tiers[currentTier]?.display_name}
          </button>
        </div>
      )}
    </div>
  );
};

export default OnboardingTierSelection;