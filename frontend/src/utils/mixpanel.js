import mixpanel from 'mixpanel-browser';

// Initialize Mixpanel
const MIXPANEL_TOKEN = process.env.REACT_APP_MIXPANEL_TOKEN || 'demo_token';
const isDevelopment = process.env.NODE_ENV === 'development';

// Initialize with lightweight config
mixpanel.init(MIXPANEL_TOKEN, {
  debug: isDevelopment,
  track_pageview: false, // We'll handle this manually
  persistence: 'localStorage',
  ignore_dnt: true
});

// Mixpanel tracking utility
class MixpanelTracker {
  constructor() {
    this.sessionStart = Date.now();
    this.currentSession = this.generateSessionId();
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Track user inputs
  track(eventName, properties = {}) {
    if (!isDevelopment) {
      // In production, send to actual Mixpanel
      mixpanel.track(eventName, {
        ...properties,
        session_id: this.currentSession,
        timestamp: Date.now()
      });
    } else {
      // In development, log to console
      console.log('🔍 Mixpanel Event:', eventName, {
        ...properties,
        session_id: this.currentSession,
        timestamp: Date.now()
      });
    }
  }

  // Track user choices
  trackUserChoice(choice, context = {}) {
    this.track('user_choice', {
      choice: choice,
      context: context,
      event_category: 'user_interaction'
    });
  }

  // Track agent used
  trackAgentUsed(agentId, agentName, tier = 'novice') {
    this.track('agent_used', {
      agent_id: agentId,
      agent_name: agentName,
      user_tier: tier,
      event_category: 'agent_interaction'
    });
  }

  // Track tier engagement
  trackTierEngagement(tier, action, context = {}) {
    this.track('tier_engagement', {
      tier: tier,
      action: action,
      context: context,
      event_category: 'tier_interaction'
    });
  }

  // Track conversation flows
  trackConversationFlow(flow, step, data = {}) {
    this.track('conversation_flow', {
      flow: flow,
      step: step,
      data: data,
      event_category: 'conversation'
    });
  }

  // Track session length when it ends
  trackSessionEnd(additionalData = {}) {
    const sessionLength = Date.now() - this.sessionStart;
    this.track('session_ended', {
      session_length_ms: sessionLength,
      session_length_minutes: Math.round(sessionLength / 60000),
      ...additionalData,
      event_category: 'session'
    });
  }

  // Track message sent
  trackMessageSent(messageData = {}) {
    this.track('message_sent', {
      ...messageData,
      event_category: 'chat'
    });
  }

  // Track persona selection
  trackPersonaSelected(persona, context = {}) {
    this.track('persona_selected', {
      persona: persona,
      context: context,
      event_category: 'personalization'
    });
  }

  // Track go deeper usage
  trackGoDeeper(context = {}) {
    this.track('go_deeper_used', {
      context: context,
      event_category: 'feature_usage'
    });
  }

  // Track onboarding steps
  trackOnboardingStep(step, data = {}) {
    this.track('onboarding_step', {
      step: step,
      data: data,
      event_category: 'onboarding'
    });
  }

  // Set user properties
  setUserProperties(properties) {
    if (!isDevelopment) {
      mixpanel.people.set(properties);
    } else {
      console.log('👤 User Properties:', properties);
    }
  }

  // Identify user
  identify(userId, properties = {}) {
    if (!isDevelopment) {
      mixpanel.identify(userId);
      mixpanel.people.set(properties);
    } else {
      console.log('🆔 User Identified:', userId, properties);
    }
  }
}

// Export singleton instance
export const tracker = new MixpanelTracker();
export default tracker;