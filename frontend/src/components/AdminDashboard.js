import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = ({ onLogout }) => {
  const [tierBehaviors, setTierBehaviors] = useState({});
  const [errorLogs, setErrorLogs] = useState([]);
  const [selectedTier, setSelectedTier] = useState('sovereign');
  const [testSession, setTestSession] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchErrorLogs();
  }, []);

  const fetchErrorLogs = async () => {
    try {
      const token = localStorage.getItem('tc_admin_jwt');
      const response = await axios.get(`${API}/admin/error-logs`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setErrorLogs(response.data.logs || []);
    } catch (err) {
      console.error('Failed to fetch error logs:', err);
    }
  };

  const testTierBehavior = async (tier) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('tc_admin_jwt');
      
      // First activate tier override for testing
      await axios.post(`${API}/admin/activate_sovereign_investigation`, {
        session_id: `admin_tier_test_${tier}_${Date.now()}`
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Then test actual chat with the tier
      const chatResponse = await axios.post(`${API}/chat`, {
        companion_id: "sophia",
        message: "Tell me about starting a business",
        session_id: `admin_tier_test_${tier}_${Date.now()}`,
        user_mode: "Confidant",
        affection_dial: 2
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setTierBehaviors(prev => ({
        ...prev,
        [tier]: {
          response: chatResponse.data.reply,
          memory_summaries: chatResponse.data.memory_summaries || 0,
          features_used: {
            memory_access: chatResponse.data.memory_access || false,
            unlimited_messages: chatResponse.data.is_admin || false,
            tier_features: tier
          },
          response_length: chatResponse.data.reply?.length || 0,
          tier: tier
        }
      }));
    } catch (err) {
      console.error('Tier behavior test failed:', err);
      setTierBehaviors(prev => ({
        ...prev,
        [tier]: {
          error: err.response?.data?.detail || 'Test failed',
          tier: tier
        }
      }));
    } finally {
      setLoading(false);
    }
  };

  const clearErrorLogs = async () => {
    try {
      const token = localStorage.getItem('tc_admin_jwt');
      await axios.delete(`${API}/admin/error-logs`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setErrorLogs([]);
    } catch (err) {
      console.error('Failed to clear error logs:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('tc_admin_jwt');
    localStorage.removeItem('tc_admin_session');
    onLogout();
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>🛠️ Admin Dashboard</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      <div className="admin-content">
        {/* Tier Behavior Testing */}
        <div className="admin-section">
          <h2>Tier Behavior Testing</h2>
          <div className="tier-test-controls">
            <select 
              value={selectedTier} 
              onChange={(e) => setSelectedTier(e.target.value)}
              className="tier-select"
            >
              <option value="novice">Novice (Free)</option>
              <option value="apprentice">Apprentice</option>
              <option value="regent">Regent</option>
              <option value="sovereign">Sovereign</option>
            </select>
            <button 
              onClick={() => testTierBehavior(selectedTier)}
              disabled={loading}
              className="test-btn"
            >
              {loading ? 'Testing...' : `Test ${selectedTier} Behavior`}
            </button>
          </div>

          {tierBehaviors[selectedTier] && (
            <div className="tier-behavior-result">
              <h3>{selectedTier} Response:</h3>
              <div className="behavior-details">
                <p><strong>Response Length:</strong> {tierBehaviors[selectedTier].response?.length || 0} chars</p>
                <p><strong>Memory Access:</strong> {tierBehaviors[selectedTier].memory_summaries || 0} summaries</p>
                <p><strong>Features Used:</strong> {JSON.stringify(tierBehaviors[selectedTier].features_used || {})}</p>
                <div className="response-preview">
                  <strong>Preview:</strong>
                  <p>{tierBehaviors[selectedTier].response?.substring(0, 200)}...</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Error Logs */}
        <div className="admin-section">
          <div className="section-header">
            <h2>Error & Loop Logs</h2>
            <button onClick={clearErrorLogs} className="clear-logs-btn">Clear Logs</button>
          </div>
          
          <div className="error-logs">
            {errorLogs.length === 0 ? (
              <p className="no-logs">No error logs found</p>
            ) : (
              errorLogs.map((log, index) => (
                <div key={index} className="error-log-item">
                  <div className="log-header">
                    <span className={`log-type ${log.type}`}>{log.type.toUpperCase()}</span>
                    <span className="log-time">{new Date(log.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="log-message">{log.message}</div>
                  {log.context && (
                    <div className="log-context">
                      <strong>Context:</strong> {JSON.stringify(log.context, null, 2)}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="admin-section">
          <h2>Quick Stats</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <div className="stat-value">{errorLogs.filter(l => l.type === 'loopback').length}</div>
              <div className="stat-label">Loopback Errors</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{errorLogs.filter(l => l.type === 'off_topic').length}</div>
              <div className="stat-label">Off-Topic Resets</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{errorLogs.filter(l => l.type === 'repeated_opener').length}</div>
              <div className="stat-label">Repeated Openers</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;