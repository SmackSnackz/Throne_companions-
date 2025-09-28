import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminLogin = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [accessCode, setAccessCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [codeResult, setCodeResult] = useState(null);

  const handleRequestCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/request-admin-code`, {
        email: email
      });

      if (response.data.success) {
        setCodeSent(true);
        setCodeResult(response.data);
        setError('');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send access code');
      console.error('Code request failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/verify-admin-code`, {
        email: email,
        code: accessCode
      });

      if (response.data.success && response.data.token) {
        localStorage.setItem('tc_admin_jwt', response.data.token);
        localStorage.setItem('tc_admin_session', Date.now().toString());
        onLoginSuccess(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid access code');
      console.error('Code verification failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-container">
      <div className="admin-login-form">
        <h2>🔐 Admin Access</h2>
        <p>Secure admin view for tier behavior testing</p>
        
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Admin Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@thronecompanions.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Access Code:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Admin access code"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="admin-login-btn">
            {loading ? 'Verifying...' : 'Access Admin Panel'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;