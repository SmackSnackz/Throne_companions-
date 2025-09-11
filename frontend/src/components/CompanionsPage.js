import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CompanionsPage = () => {
  const [companions, setCompanions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCompanions = async () => {
      try {
        const response = await axios.get(`${API}/companions`);
        setCompanions(response.data);
      } catch (err) {
        setError("Failed to load companions");
        console.error("Error fetching companions:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanions();
  }, []);

  if (loading) {
    return <div className="loading">Loading companions...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="companions-container">
      <div className="companions-header">
        <h1>Your Companions</h1>
        <p>Choose your companion for an engaging conversation. Each brings their unique personality and perspective to every interaction.</p>
      </div>
      
      <div className="companions-grid">
        {companions.map((companion) => (
          <Link 
            key={companion.id} 
            to={`/chat/${companion.id}`} 
            className="companion-card"
            style={{ textDecoration: 'none' }}
          >
            <div className="companion-image-container">
              <img 
                src={companion.image} 
                alt={companion.name}
                className="companion-image"
              />
            </div>
            <div className="companion-info">
              <h3 className="companion-name">{companion.name}</h3>
              <p className="companion-description">{companion.description}</p>
              <button className="chat-button">Start Chatting</button>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default CompanionsPage;