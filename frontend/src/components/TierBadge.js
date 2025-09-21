import React from "react";

const TierBadge = ({ tier, size = "small" }) => {
  const tierConfig = {
    novice: {
      name: "Novice",
      color: "bronze",
      icon: "📜"
    },
    apprentice: {
      name: "Apprentice", 
      color: "silver",
      icon: "⚡"
    },
    regent: {
      name: "Regent",
      color: "gold", 
      icon: "👑"
    },
    sovereign: {
      name: "Sovereign",
      color: "platinum",
      icon: "💎"
    }
  };

  const config = tierConfig[tier] || tierConfig.novice;

  return (
    <div className={`tier-badge tier-${config.color} tier-${size}`}>
      <span className="tier-icon">{config.icon}</span>
      <span className="tier-text">{config.name}</span>
    </div>
  );
};

export default TierBadge;