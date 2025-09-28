import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InvestigationPanel = ({ userEmail, sessionId, isVisible, onClose }) => {
  const [investigationActive, setInvestigationActive] = useState(false);
  const [tierPreview, setTierPreview] = useState(null);
  const [effectiveConfig, setEffectiveConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isVisible && sessionId) {
      checkInvestigationStatus();
    }
  }, [isVisible, sessionId]);

  const checkInvestigationStatus = async () => {
    try {
      const token = localStorage.getItem('tc_jwt');
      const response = await axios.get(`${API}/admin/effective_tier_config`, {
        params: { session_id: sessionId },
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setEffectiveConfig(response.data);
      setInvestigationActive(response.data.has_override);
    } catch (err) {
      console.error('Failed to check investigation status:', err);
    }
  };

  const activateInvestigation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('tc_jwt');
      const response = await axios.post(`${API}/admin/activate_sovereign_investigation`, {
        session_id: sessionId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setInvestigationActive(true);
      await loadTierPreview();
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Activation failed');
      console.error('Investigation activation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTierPreview = async () => {
    try {
      const token = localStorage.getItem('tc_jwt');
      const response = await axios.get(`${API}/admin/tier_investigation_preview`, {
        params: { session_id: sessionId },
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setTierPreview(response.data);
    } catch (err) {
      console.error('Failed to load tier preview:', err);
    }
  };

  const deactivateInvestigation = async () => {
    setLoading(true);
    
    try {
      const token = localStorage.getItem('tc_jwt');
      await axios.post(`${API}/admin/deactivate_override`, {
        session_id: sessionId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setInvestigationActive(false);
      setTierPreview(null);
      setEffectiveConfig(null);
      
    } catch (err) {
      console.error('Deactivation failed:', err);
      setError('Deactivation failed');
    } finally {
      setLoading(false);
    }
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="investigation-panel-overlay">
      <div className="investigation-panel">
        <div className="investigation-header">
          <h2>🔒 Tier Investigation Panel</h2>
          <p>Quantum Sovereign Access Level</p>
          <button onClick={onClose} className="close-investigation">×</button>
        </div>

        <div className="investigation-content">
          {!investigationActive ? (
            <div className="investigation-activation">
              <h3>Activate Investigation Mode</h3>
              <p>This will grant temporary access to all tier configurations, finance modules, and custom logic for investigation purposes.</p>
              
              {error && (
                <div className="investigation-error">
                  ⚠️ {error}
                </div>
              )}
              
              <button 
                onClick={activateInvestigation}
                disabled={loading}
                className="activate-investigation-btn"
              >
                {loading ? 'Activating...' : '🚀 Activate Quantum Sovereign Access'}
              </button>
            </div>
          ) : (
            <div className="investigation-active">
              <div className="investigation-status">
                <div className="status-indicator active">
                  🟢 Investigation Mode Active
                </div>
                <p>Access Level: Quantum Sovereign</p>
                <p>Investigator: {userEmail}</p>
                <p>Session: {sessionId}</p>
              </div>

              {effectiveConfig && (
                <div className="effective-config">
                  <h4>Current Effective Configuration</h4>
                  <div className="config-display">
                    <p><strong>Base Tier:</strong> {effectiveConfig.base_tier}</p>
                    <p><strong>Effective Tier:</strong> {effectiveConfig.effective_config.tier_level}</p>
                    <p><strong>Display Name:</strong> {effectiveConfig.effective_config.display_name}</p>
                    <p><strong>Memory Retention:</strong> {effectiveConfig.effective_config.memory_retention_days === -1 ? 'Unlimited' : effectiveConfig.effective_config.memory_retention_days + ' days'}</p>
                  </div>
                </div>
              )}

              {tierPreview && (
                <div className="tier-preview">
                  <h4>All Tier Configurations</h4>
                  <div className="tier-grid">
                    {Object.entries(tierPreview.tier_configurations).map(([tierName, config]) => (
                      <div key={tierName} className="tier-card">
                        <h5>{config.display_name}</h5>
                        <p><strong>Price:</strong> {config.price}</p>
                        <p><strong>Memory:</strong> {config.memory_retention_days === -1 ? 'Unlimited' : config.memory_retention_days + ' days'}</p>
                        
                        {config.finance_features && (
                          <div className="finance-features">
                            <h6>Finance Features:</h6>
                            {Object.entries(config.finance_features).map(([feature, enabled]) => (
                              <span key={feature} className={`feature-tag ${enabled ? 'enabled' : 'disabled'}`}>
                                {feature}: {enabled ? '✅' : '❌'}
                              </span>
                            ))}
                          </div>
                        )}
                        
                        {config.memory_details && (
                          <div className="memory-details">
                            <h6>Memory Details:</h6>
                            <p>Context: {config.memory_details.context_depth}</p>
                            <p>Personalization: {config.memory_details.personalization}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {tierPreview.finance_modules && (
                    <div className="finance-modules">
                      <h4>Finance Modules</h4>
                      {Object.entries(tierPreview.finance_modules).map(([moduleName, moduleData]) => (
                        <div key={moduleName} className="finance-module">
                          <h5>{moduleName}</h5>
                          <p>{moduleData.description}</p>
                          <div className="module-features">
                            {moduleData.features.map((feature, index) => (
                              <span key={index} className="feature-tag enabled">{feature}</span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {tierPreview.custom_logic && (
                    <div className="custom-logic">
                      <h4>Custom Logic Preview</h4>
                      {Object.entries(tierPreview.custom_logic).map(([logicName, logicData]) => (
                        <div key={logicName} className="logic-module">
                          <h5>{logicName}</h5>
                          <p>{logicData.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <button 
                onClick={deactivateInvestigation}
                disabled={loading}
                className="deactivate-investigation-btn"
              >
                {loading ? 'Deactivating...' : '🔒 Deactivate Investigation Mode'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InvestigationPanel;