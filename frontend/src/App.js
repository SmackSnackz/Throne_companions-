import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ComplianceFlow from "./components/compliance/ComplianceFlow";
import HomePage from "./components/HomePage";
import CompanionsPage from "./components/CompanionsPage";
import ChatPage from "./components/ChatPage";
import TierSelection from "./components/tiers/TierSelection";

function App() {
  const [isCompliant, setIsCompliant] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user has completed compliance on app load
    const checkCompliance = () => {
      const compliance = localStorage.getItem('throneCompanionsCompliance');
      if (compliance) {
        const parsed = JSON.parse(compliance);
        if (parsed.ageVerified && parsed.termsAccepted && parsed.dmcaAcknowledged) {
          setIsCompliant(true);
        }
      }
      setIsLoading(false);
    };

    checkCompliance();
  }, []);

  const handleComplianceComplete = () => {
    setIsCompliant(true);
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-container">
          <img src="/assets/logo.png" alt="Throne Companions" className="loading-logo" />
          <div className="loading-text">Loading Throne Companions...</div>
        </div>
      </div>
    );
  }

  if (!isCompliant) {
    return <ComplianceFlow onComplianceComplete={handleComplianceComplete} />;
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/companions" element={<CompanionsPage />} />
          <Route path="/chat/:id" element={<ChatPage />} />
          <Route path="/tiers" element={<TierSelection />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;