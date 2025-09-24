import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import Link from 'next/link';

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default function Companions() {
  const router = useRouter();
  const [companions, setCompanions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/companions`)
      .then(r => r.json())
      .then(data => {
        setCompanions(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load companions:', err);
        setLoading(false);
      });
  }, []);

  const startChat = (companionId: string) => {
    router.push(`/chat/${companionId}`);
  };

  if (loading) {
    return (
      <main style={{ maxWidth: 720, margin: '40px auto', fontFamily: 'system-ui', textAlign: 'center' }}>
        <h1>Loading companions...</h1>
      </main>
    );
  }

  return (
    <main style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'system-ui', padding: '0 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 10px 0' }}>Choose Your Companion</h1>
        <p style={{ color: '#666', fontSize: '1.1rem' }}>
          Select a companion to begin your journey toward sovereignty
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '25px' }}>
        {companions.map((companion: any) => (
          <div key={companion.id} style={{ 
            border: '2px solid #e0e0e0', 
            borderRadius: '16px', 
            padding: '25px', 
            textAlign: 'center',
            transition: 'transform 0.2s',
            cursor: 'pointer'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0px)'}
          >
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>
              {companion.gender === 'female' ? '👸' : '🤴'}
            </div>
            <h3 style={{ margin: '0 0 10px 0', fontSize: '1.4rem' }}>{companion.name}</h3>
            <p style={{ fontSize: '0.9rem', color: '#666', margin: '0 0 15px 0' }}>
              {companion.bio}
            </p>
            <p style={{ fontSize: '0.8rem', color: '#888', margin: '0 0 20px 0', lineHeight: '1.4' }}>
              {companion.backstory}
            </p>
            <div style={{ marginBottom: '20px' }}>
              {companion.traits.map((trait: string) => (
                <span key={trait} style={{ 
                  display: 'inline-block',
                  backgroundColor: '#f0f0f0',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  fontSize: '0.8rem',
                  margin: '2px'
                }}>
                  {trait}
                </span>
              ))}
            </div>
            <button
              onClick={() => startChat(companion.id)}
              style={{ 
                width: '100%', 
                padding: '12px', 
                backgroundColor: '#4CAF50', 
                color: 'white', 
                border: 'none', 
                borderRadius: '8px',
                fontSize: '1rem',
                cursor: 'pointer'
              }}
            >
              Start Conversation
            </button>
          </div>
        ))}
      </div>

      <div style={{ textAlign: 'center', marginTop: '50px', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '12px' }}>
        <p style={{ margin: '0 0 15px 0', color: '#666' }}>
          Free tier: 20 messages total with basic Aurora
        </p>
        <Link href="/pricing" style={{ 
          color: '#2196F3', 
          textDecoration: 'none',
          fontSize: '1.1rem',
          fontWeight: 'bold'
        }}>
          Upgrade for unlimited conversations →
        </Link>
      </div>
    </main>
  );
            }
