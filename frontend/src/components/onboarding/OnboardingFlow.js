import React, { useState, useEffect } from "react";
import WelcomeScreen from "./WelcomeScreen";
import ComplianceFlow from "../compliance/ComplianceFlow";
import CompanionSelection from "./CompanionSelection";
import TierSelection from "./OnboardingTierSelection";
import FirstGuidedChat from "./FirstGuidedChat";

const OnboardingFlow = ({ onOnboardingComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [onboardingData, setOnboardingData] = useState({});
  const [startTime] = useState(Date.now());

  // Onboarding steps
  const steps = [
    "welcome",
    "compliance", 
    "companion_selection",
    "tier_selection",
    "first_chat"
  ];

  useEffect(() => {
    // Check for existing onboarding progress
    const savedProgress = localStorage.getItem('throneCompanionsOnboarding');
    if (savedProgress) {
      const progress = JSON.parse(savedProgress);
      
      // Find last incomplete step
      let lastStep = 0;
      if (progress.completed_welcome) lastStep = 1;
      if (progress.completed_compliance) lastStep = 2;
      if (progress.chosen_companion) lastStep = 3;
      if (progress.chosen_tier) lastStep = 4;
      if (progress.first_chat_started) {
        // Onboarding complete, notify parent
        if (onOnboardingComplete) {
          onOnboardingComplete();
        }
        return;
      }
      
      setCurrentStep(lastStep);
      setOnboardingData(progress);
    }

    // Track onboarding start
    trackOnboardingEvent('onboarding_started');
  }, [onOnboardingComplete]);

  const trackOnboardingEvent = (event, data = {}) => {
    // In production, this would send to analytics
    console.log('Onboarding Event:', event, {
      ...data,
      step: steps[currentStep],
      time_elapsed: Date.now() - startTime
    });
  };

  const saveProgress = (stepData) => {
    const updatedData = { ...onboardingData, ...stepData };
    setOnboardingData(updatedData);
    
    try {
      localStorage.setItem('throneCompanionsOnboarding', JSON.stringify(updatedData));
      console.log('Onboarding progress saved:', updatedData);
    } catch (error) {
      console.error('Failed to save onboarding progress:', error);
    }
  };

  const nextStep = (stepData = {}) => {
    console.log('nextStep called with:', stepData, 'current step:', currentStep);
    saveProgress(stepData);
    
    if (currentStep < steps.length - 1) {
      const nextStepIndex = currentStep + 1;
      console.log('Moving to step:', nextStepIndex, steps[nextStepIndex]);
      setCurrentStep(nextStepIndex);
      trackOnboardingEvent(`step_${steps[nextStepIndex]}_started`);
    }
  };

  const handleWelcomeComplete = () => {
    trackOnboardingEvent('welcome_completed');
    nextStep({ completed_welcome: true });
  };

  const handleComplianceComplete = () => {
    trackOnboardingEvent('compliance_completed');
    nextStep({ completed_compliance: true });
  };

  const handleCompanionSelected = (companionId) => {
    console.log('Companion selected:', companionId);
    trackOnboardingEvent('companion_selected', { companion: companionId });
    nextStep({ chosen_companion: companionId });
  };

  const handleTierSelected = (tier) => {
    trackOnboardingEvent('tier_selected', { tier });
    nextStep({ chosen_tier: tier });
  };

  const handleFirstChatStarted = () => {
    const completionTime = Date.now() - startTime;
    trackOnboardingEvent('onboarding_completed', { 
      completion_time_ms: completionTime,
      completion_time_minutes: Math.round(completionTime / 60000 * 100) / 100
    });
    
    saveProgress({ 
      first_chat_started: true,
      onboarding_completed: true,
      completion_time: completionTime
    });
    
    // Notify parent that onboarding is complete
    if (onOnboardingComplete) {
      onOnboardingComplete();
    }
  };

  const renderCurrentStep = () => {
    switch (steps[currentStep]) {
      case "welcome":
        return <WelcomeScreen onComplete={handleWelcomeComplete} />;
      
      case "compliance":
        return <ComplianceFlow onComplianceComplete={handleComplianceComplete} />;
      
      case "companion_selection":
        return (
          <CompanionSelection 
            onCompanionSelected={handleCompanionSelected}
            selectedCompanion={onboardingData.chosen_companion}
          />
        );
      
      case "tier_selection":
        return (
          <TierSelection 
            onTierSelected={handleTierSelected}
            selectedTier={onboardingData.chosen_tier || "novice"}
            isOnboarding={true}
          />
        );
      
      case "first_chat":
        return (
          <FirstGuidedChat
            companion={onboardingData.chosen_companion}
            tier={onboardingData.chosen_tier || "novice"}
            onChatStarted={handleFirstChatStarted}
          />
        );
      
      default:
        return <WelcomeScreen onComplete={handleWelcomeComplete} />;
    }
  };

  return (
    <div className="onboarding-flow">
      {currentStep > 0 && currentStep < 4 && (
        <div className="onboarding-progress">
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
              />
            </div>
            <div className="progress-text">
              Step {currentStep + 1} of {steps.length}
            </div>
          </div>
        </div>
      )}
      
      <div className="onboarding-content">
        {renderCurrentStep()}
      </div>
    </div>
  );
};

export default OnboardingFlow;