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
      try {
        const onboardingData = localStorage.getItem('throneCompanionsOnboarding');
        console.log('Checking onboarding data:', onboardingData);
        
        if (onboardingData) {
          const parsed = JSON.parse(onboardingData);
          console.log('Parsed onboarding data:', parsed);
          
          // More lenient check for onboarding completion
          if (parsed.onboarding_completed || parsed.first_chat_started || 
              (parsed.completed_compliance && parsed.chosen_companion && parsed.chosen_tier)) {
            console.log('User is onboarded, showing main app');
            setIsOnboarded(true);
          } else {
            console.log('User needs onboarding');
          }
        } else {
          console.log('No onboarding data found');
          // For demo purposes, skip onboarding for now
          setIsOnboarded(true);
        }
      } catch (error) {
        console.error('Error checking onboarding status:', error);
        // For demo purposes, skip onboarding on error
        setIsOnboarded(true);
      }
      setIsLoading(false);
    };

    checkOnboarding();
  }, []);

  const handleOnboardingComplete = () => {
    setIsOnboarded(true);
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

  // Show onboarding flow for new users
  if (!isOnboarded) {
    return <OnboardingFlow onOnboardingComplete={handleOnboardingComplete} />;
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