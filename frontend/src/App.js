import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import OnboardingFlow from "./components/onboarding/OnboardingFlow";
import HomePage from "./components/HomePage";
import CompanionsPage from "./components/CompanionsPage";
import ChatPage from "./components/ChatPage";
import TierSelection from "./components/tiers/TierSelection";

function App() {
  const [isOnboarded, setIsOnboarded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user has completed onboarding
    const checkOnboarding = () => {
      const onboardingData = localStorage.getItem('throneCompanionsOnboarding');
      if (onboardingData) {
        const parsed = JSON.parse(onboardingData);
        if (parsed.onboarding_completed || parsed.first_chat_started) {
          setIsOnboarded(true);
        }
      }
      setIsLoading(false);
    };

    checkOnboarding();
  }, []);

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

  // Show onboarding flow for new users
  if (!isOnboarded) {
    return <OnboardingFlow />;
  }

  // Show main app for onboarded users
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/companions" element={<CompanionsPage />} />
          <Route path="/chat/:id" element={<ChatPage />} />
          <Route path="/tiers" element={<TierSelection />} />
          <Route path="/onboarding" element={<OnboardingFlow />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;