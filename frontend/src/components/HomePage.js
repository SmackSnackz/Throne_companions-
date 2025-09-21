import React from "react";
import { Link } from "react-router-dom";

const HomePage = () => {
  return (
    <div className="landing-container">
      <div className="logo-container">
        <img src="/assets/logo.png" alt="Throne Companions" className="logo" />
      </div>
      
      <h1 className="main-title">Throne Companions</h1>
      <p className="subtitle">Enter a realm of sophisticated conversation</p>
      
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