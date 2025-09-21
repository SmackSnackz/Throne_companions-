import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TierSelection = ({ onTierSelected, currentTier = "novice" }) => {
  const [tiers, setTiers] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedTier, setSelectedTier] = useState(currentTier);

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

  const handleTierSelect = async (tierKey) => {
    try {
      const response = await axios.put(`${API}/user`, {
        tier: tierKey
      });
      setSelectedTier(tierKey);
      if (onTierSelected) {
        onTierSelected(tierKey, response.data);
      }
    } catch (err) {
      console.error("Error updating tier:", err);
    }
  };

  if (loading) {
    return <div className="loading">Loading tiers...</div>;
  }

  const tierOrder = ["novice", "apprentice", "regent", "sovereign"];

  return (
    <div className="tier-selection">
      <div className="tier-header">
        <h2>Choose Your Path</h2>
        <p>Select the tier that best suits your journey with your companion</p>
      </div>

      <div className="tiers-grid">
        {tierOrder.map((tierKey) => {
          const tier = tiers[tierKey];
          if (!tier) return null;

          const isSelected = selectedTier === tierKey;
          const isCurrent = currentTier === tierKey;

          return (
            <div 
              key={tierKey} 
              className={`tier-card ${tierKey} ${isSelected ? 'selected' : ''} ${isCurrent ? 'current' : ''}`}
              onClick={() => handleTierSelect(tierKey)}
            >
              <div className="tier-card-header">
                <h3 className="tier-name">{tier.display_name}</h3>
                <div className="tier-price">
                  {tier.price === 0 ? 'Free' : `$${tier.price}/month`}
                </div>
              </div>

              <div className="tier-features">
                <div className="feature-group">
                  <h4>Memory</h4>
                  <p>{tier.memory_retention_days === 36500 ? '100 years' : 
                      tier.memory_retention_days === 3650 ? '10 years' : 
                      tier.memory_retention_days === 7 ? '1 week' : '1 day'}</p>
                </div>

                <div className="feature-group">
                  <h4>Communication</h4>
                  <div className="modes-list">
                    {tier.allowed_modes.includes('all') ? 
                      ['Text', 'Voice', 'Visuals', 'Finance', 'Custom'].map(mode => (
                        <span key={mode} className="mode-badge enabled">{mode}</span>
                      )) :
                      ['Text', 'Voice', 'Visuals', 'Finance', 'Custom'].map(mode => (
                        <span 
                          key={mode} 
                          className={`mode-badge ${tier.allowed_modes.includes(mode.toLowerCase()) ? 'enabled' : 'disabled'}`}
                        >
                          {mode}
                        </span>
                      ))
                    }
                  </div>
                </div>

                <div className="feature-group">
                  <h4>Response Style</h4>
                  <p>{tier.response_style.length} responses, {tier.response_style.formality} tone</p>
                </div>

                <div className="feature-group">
                  <h4>Mastery Level</h4>
                  <p className="mastery-level">{tier.prompting_mastery}</p>
                </div>

                {tier.tools_enabled.length > 0 && (
                  <div className="feature-group">
                    <h4>Tools</h4>
                    <div className="tools-list">
                      {tier.tools_enabled.map(tool => (
                        <span key={tool} className="tool-badge">{tool.replace('_', ' ')}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="tier-card-footer">
                {isCurrent && <div className="current-badge">Current Plan</div>}
                {!isCurrent && (
                  <button className="select-tier-btn">
                    {tier.price === 0 ? 'Select Free' : 'Upgrade'}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="tier-comparison">
        <h3>Quick Comparison</h3>
        <div className="comparison-table">
          <div className="comparison-row header">
            <div className="feature-name">Feature</div>
            <div className="tier-col">Novice</div>
            <div className="tier-col">Apprentice</div>
            <div className="tier-col">Regent</div>
            <div className="tier-col">Sovereign</div>
          </div>
          
          <div className="comparison-row">
            <div className="feature-name">Memory Retention</div>
            <div className="tier-col">1 day</div>
            <div className="tier-col">1 week</div>
            <div className="tier-col">10 years</div>
            <div className="tier-col">100 years</div>
          </div>
          
          <div className="comparison-row">
            <div className="feature-name">Voice Responses</div>
            <div className="tier-col">❌</div>
            <div className="tier-col">✅</div>
            <div className="tier-col">✅</div>
            <div className="tier-col">✅</div>
          </div>
          
          <div className="comparison-row">
            <div className="feature-name">Visual Content</div>
            <div className="tier-col">❌</div>
            <div className="tier-col">✅</div>
            <div className="tier-col">✅</div>
            <div className="tier-col">✅</div>
          </div>
          
          <div className="comparison-row">
            <div className="feature-name">Finance Tools</div>
            <div className="tier-col">❌</div>
            <div className="tier-col">❌</div>
            <div className="tier-col">✅</div>
            <div className="tier-col">✅</div>
          </div>
          
          <div className="comparison-row">
            <div className="feature-name">Custom Persona</div>
            <div className="tier-col">❌</div>
            <div className="tier-col">❌</div>
            <div className="tier-col">❌</div>
            <div className="tier-col">✅</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TierSelection;