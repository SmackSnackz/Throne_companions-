import React, { useState, useEffect } from "react";
import AgeVerification from "./AgeVerification";
import TermsAndPrivacy from "./TermsAndPrivacy";
import DMCAPolicy from "./DMCAPolicy";

const ComplianceFlow = ({ onComplianceComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState({
    ageVerified: false,
    termsAccepted: false,
    dmcaAcknowledged: false
  });

  // Check if user has already completed compliance
  useEffect(() => {
    const compliance = localStorage.getItem('throneCompanionsCompliance');
    if (compliance) {
      const parsed = JSON.parse(compliance);
      if (parsed.ageVerified && parsed.termsAccepted && parsed.dmcaAcknowledged) {
        onComplianceComplete();
        return;
      }
    }
  }, [onComplianceComplete]);

  const handleStepComplete = (stepName, data) => {
    const newCompletedSteps = {
      ...completedSteps,
      [stepName]: true
    };
    
    setCompletedSteps(newCompletedSteps);

    // Store in localStorage for persistence
    const complianceData = {
      ...newCompletedSteps,
      timestamp: new Date().toISOString(),
      ...data
    };
    localStorage.setItem('throneCompanionsCompliance', JSON.stringify(complianceData));

    // Move to next step
    if (currentStep < 2) {
      setCurrentStep(currentStep + 1);
    } else {
      // All steps completed
      onComplianceComplete();
    }
  };

  const steps = [
    {
      component: AgeVerification,
      title: "Age Verification",
      stepName: "ageVerified"
    },
    {
      component: TermsAndPrivacy,
      title: "Terms & Privacy",
      stepName: "termsAccepted"
    },
    {
      component: DMCAPolicy,
      title: "Content Policy",
      stepName: "dmcaAcknowledged"
    }
  ];

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="compliance-flow">
      <div className="compliance-container">
        <div className="compliance-header">
          <img src="/assets/logo.png" alt="Throne Companions" className="compliance-logo" />
          <h1 className="compliance-title">Welcome to Throne Companions</h1>
          <p className="compliance-subtitle">Please complete the following requirements to proceed</p>
        </div>

        <div className="compliance-progress">
          <div className="progress-bar">
            {steps.map((step, index) => (
              <div 
                key={index} 
                className={`progress-step ${index <= currentStep ? 'active' : ''} ${completedSteps[step.stepName] ? 'completed' : ''}`}
              >
                <div className="step-number">{index + 1}</div>
                <div className="step-title">{step.title}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="compliance-content">
          <CurrentStepComponent 
            onComplete={(data) => handleStepComplete(steps[currentStep].stepName, data)}
          />
        </div>
      </div>
    </div>
  );
};

export default ComplianceFlow;