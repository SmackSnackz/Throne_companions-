import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const [isAdmin, setIsAdmin] = useState(false);
  
  useEffect(() => {
    checkAdminStatus();
  }, []);
  
  const checkAdminStatus = async () => {
    try {
      const token = localStorage.getItem('tc_jwt');
      if (token) {
        const response = await axios.get(`${API}/auth/verify`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setIsAdmin(response.data.is_admin);
      }
    } catch (err) {
      console.log("No valid token found");
    }
  };
  
  const toggleAdmin = async () => {
    try {
      const newRole = isAdmin ? "user" : "admin";
      const response = await axios.post(`${API}/auth/create-token`, {
        email: "demo@thronecompanions.com", 
        role: newRole
      });
      localStorage.setItem('tc_jwt', response.data.token);
      setIsAdmin(!isAdmin);
    } catch (err) {
      console.error("Failed to toggle admin:", err);
    }
  };
  
  return (
    <div className="landing-container">
      <div className="logo-container">
        <img src="/assets/logo.png" alt="Throne Companions" className="logo" />
      </div>
      
      <h1 className="main-title">Throne Companions</h1>
      <p className="subtitle">Enter a realm of sophisticated conversation</p>
      
      <div className="admin-controls" style={{ margin: "1rem 0" }}>
        <button onClick={toggleAdmin} className="admin-toggle">
          {isAdmin ? "👑 Admin Mode" : "👤 User Mode"} (Click to Switch)
        </button>
      </div>
      
      <div className="cta-buttons">
        <Link to="/companions" className="cta-button">
          Meet Your Companions
        </Link>
        <Link to="/tiers" className="cta-button secondary">
          Choose Your Tier
        </Link>
      </div>
    </div>
  );
};

export default HomePage;