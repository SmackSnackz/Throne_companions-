import React, { useState } from 'react';

const PersonaSelector = ({ 
  selectedPersona, 
  onPersonaChange, 
  isVisible = true, 
  className = "" 
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const personas = [
    { id: 'Lover', icon: '💖', label: 'Lover', description: 'Romantic and passionate connection' },
    { id: 'Wife', icon: '💍', label: 'Wife', description: 'Devoted life partner' },
    { id: 'Spouse', icon: '👑', label: 'Spouse', description: 'Equal partnership and support' },
    { id: 'Mother', icon: '🤱', label: 'Mother', description: 'Nurturing and protective care' },
    { id: 'Sister', icon: '👭', label: 'Sister', description: 'Loyal family bond' },
    { id: 'Confidant', icon: '🤝', label: 'Confidant', description: 'Trusted advisor and keeper of secrets' },
    { id: 'Friend', icon: '😊', label: 'Friend', description: 'Casual and supportive companion' },
    { id: 'Psychiatrist', icon: '🧠', label: 'Psychiatrist', description: 'Professional therapeutic guidance' }
  ];

  const currentPersona = personas.find(p => p.id === selectedPersona) || personas[5]; // Default to Confidant

  const handlePersonaSelect = (persona) => {
    onPersonaChange(persona.id);
    setIsOpen(false);
  };

  if (!isVisible) return null;

  return (
    <div className={`persona-selector ${className}`}>
      <div className="persona-selector-label">
        How should I respond to you?
      </div>
      
      <div className="persona-dropdown">
        <button 
          className="persona-current" 
          onClick={() => setIsOpen(!isOpen)}
          type="button"
        >
          <span className="persona-icon">{currentPersona.icon}</span>
          <span className="persona-name">{currentPersona.label}</span>
          <span className="dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
        </button>

        {isOpen && (
          <div className="persona-options">
            {personas.map((persona) => (
              <button
                key={persona.id}
                className={`persona-option ${persona.id === selectedPersona ? 'selected' : ''}`}
                onClick={() => handlePersonaSelect(persona)}
                type="button"
              >
                <span className="persona-icon">{persona.icon}</span>
                <div className="persona-details">
                  <span className="persona-name">{persona.label}</span>
                  <span className="persona-description">{persona.description}</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonaSelector;