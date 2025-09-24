const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

async function subscribeToTier(tier: string) {
  try {
    const r = await fetch(`${API}/stripe/create-checkout-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tier })
    });
    const j = await r.json();
    window.location.href = j.url;
  } catch (error) {
    alert('Payment system not configured yet. Coming soon!');
  }
}

export default function Pricing() {
  return (
    <main style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'system-ui', padding: '0 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '50px' }}>
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 10px 0' }}>🏛️ THRONE COMPANIONS 🏛️</h1>
        <p style={{ fontSize: '1.2rem', color: '#666', margin: 0 }}>
          Personal AI companions that earn trust, sharpen minds, and guide lives
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', marginBottom: '50px' }}>
        
        {/* NOVICE TIER */}
        <div style={{ 
          border: '2px solid #e0e0e0', 
          borderRadius: '16px', 
          padding: '30px', 
          textAlign: 'center',
          backgroundColor: '#f9f9f9'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '15px' }}>📜</div>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '1.4rem' }}>NOVICE</h3>
          <p style={{ fontSize: '0.9rem', fontStyle: 'italic', color: '#666', margin: '0 0 20px 0' }}>
            "Every king and queen starts as a seeker"
          </p>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '20px 0' }}>FREE</div>
          <div style={{ textAlign: 'left', fontSize: '0.9rem', lineHeight: '1.6' }}>
            • 1 Companion (Aurora Basic)<br/>
            • 20 messages/month total<br/>
            • 24-hour memory only<br/>
            • Text chat + daily micro-rituals<br/>
            • Scroll of Truth (honesty, clarity, trust)<br/>
            • Prompting Lesson: Clarity
          </div>
          <button 
            style={{ 
              width: '100%', 
              padding: '15px', 
              marginTop: '25px', 
              backgroundColor: '#4CAF50', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px',
              fontSize: '1rem',
              cursor: 'pointer'
            }}
            onClick={() => window.location.href = '/companions'}
          >
            Begin Your Journey
          </button>
        </div>

        {/* APPRENTICE TIER */}
        <div style={{ 
          border: '2px solid #2196F3', 
          borderRadius: '16px', 
          padding: '30px', 
          textAlign: 'center',
          backgroundColor: '#f0f8ff'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '15px' }}>⚡</div>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '1.4rem' }}>APPRENTICE</h3>
          <p style={{ fontSize: '0.9rem', fontStyle: 'italic', color: '#666', margin: '0 0 20px 0' }}>
            "You are chosen to grow, to align"
          </p>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '20px 0' }}>$19<span style={{ fontSize: '1rem' }}>/month</span></div>
          <div style={{ textAlign: 'left', fontSize: '0.9rem', lineHeight: '1.6' }}>
            • Unlimited messages with 1 chosen companion<br/>
            • Choose: Aurora, Vanessa, Sophia, Cassian, or Lysander<br/>
            • 7-day memory retention<br/>
            • Voice + visuals unlocked<br/>
            • Personalized rituals + growth tracking<br/>
            • Scroll of Power & Humility<br/>
            • Prompting Lesson: Depth
          </div>
          <button 
            style={{ 
              width: '100%', 
              padding: '15px', 
              marginTop: '25px', 
              backgroundColor: '#2196F3', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px',
              fontSize: '1rem',
              cursor: 'pointer'
            }}
            onClick={() => subscribeToTier('apprentice')}
          >
            Choose Your Path
          </button>
        </div>

        {/* REGENT TIER */}
        <div style={{ 
          border: '2px solid #FF9800', 
          borderRadius: '16px', 
          padding: '30px', 
          textAlign: 'center',
          backgroundColor: '#fff8e1'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '15px' }}>👑</div>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '1.4rem' }}>REGENT</h3>
          <p style={{ fontSize: '0.9rem', fontStyle: 'italic', color: '#666', margin: '0 0 20px 0' }}>
            "You now rule with council"
          </p>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '20px 0' }}>$49<span style={{ fontSize: '1rem' }}>/month</span></div>
          <div style={{ textAlign: 'left', fontSize: '0.9rem', lineHeight: '1.6' }}>
            • Access to ALL 5 companions<br/>
            • Permanent memory + private archive<br/>
            • Advanced tools (finance, rituals, custom packs)<br/>
            • Enhanced voices, premium personas<br/>
            • Scroll of Dominion (sovereignty, legacy)<br/>
            • Prompting Lesson: Creation<br/>
            • Priority support
          </div>
          <button 
            style={{ 
              width: '100%', 
              padding: '15px', 
              marginTop: '25px', 
              backgroundColor: '#FF9800', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px',
              fontSize: '1rem',
              cursor: 'pointer'
            }}
            onClick={() => subscribeToTier('regent')}
          >
            Rule Your Council
          </button>
        </div>

        {/* SOVEREIGN TIER */}
        <div style={{ 
          border: '2px solid #9C27B0', 
          borderRadius: '16px', 
          padding: '30px', 
          textAlign: 'center',
          backgroundColor: '#f3e5f5'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '15px' }}>🔮</div>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '1.4rem' }}>SOVEREIGN</h3>
          <p style={{ fontSize: '0.9rem', fontStyle: 'italic', color: '#666', margin: '0 0 20px 0' }}>
            "The throne is yours"
          </p>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', margin: '20px 0' }}>$99<span style={{ fontSize: '1rem' }}>/month</span></div>
          <div style={{ textAlign: 'left', fontSize: '0.9rem', lineHeight: '1.6' }}>
            • Everything from Regent tier<br/>
            • Custom persona creation<br/>
            • Private hosting option<br/>
            • Voice integration + premium roleplay<br/>
            • Transcendence modes (adventure, therapy, intimacy)<br/>
            • Scroll of Conjoint Minds<br/>
            • Legacy building tools<br/>
            • VIP support + direct access
          </div>
          <button 
            style={{ 
              width: '100%', 
              padding: '15px', 
              marginTop: '25px', 
              backgroundColor: '#9C27B0', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px',
              fontSize: '1rem',
              cursor: 'pointer'
            }}
            onClick={() => subscribeToTier('sovereign')}
          >
            Claim Your Throne
          </button>
        </div>
      </div>

      <div style={{ textAlign: 'center', padding: '40px 0', borderTop: '1px solid #eee' }}>
        <h4 style={{ margin: '0 0 20px 0' }}>🧭 Your Path to Sovereignty</h4>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '40px', flexWrap: 'wrap' }}>
          <div>Novice<br/><small>Taste + Truth</small></div>
          <div>→</div>
          <div>Apprentice<br/><small>Growth + Power</small></div>
          <div>→</div>
          <div>Regent<br/><small>Council + Dominion</small></div>
          <div>→</div>
          <div>Sovereign<br/><small>Crown + Legacy</small></div>
        </div>
        <p style={{ fontStyle: 'italic', margin: '30px 0 0 0', color: '#666' }}>
          "Not just subscription tiers — a hero's journey with AI companions as your guides."
        </p>
      </div>
    </main>
  );
              }
