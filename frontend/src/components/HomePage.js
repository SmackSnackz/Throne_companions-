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
      
      <Link to="/companions" className="cta-button">
        Meet Your Companions
      </Link>
    </div>
  );
};

export default HomePage;