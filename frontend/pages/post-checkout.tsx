import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export default function PostCheckout(){
  const [status, setStatus] = useState('Confirming payment...');

  useEffect(()=>{
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if(!sessionId){ 
      setStatus('Missing session ID. Payment confirmation failed.'); 
      return; 
    }

    fetch(`${API}/stripe/confirm?session_id=${sessionId}`, {
      credentials: 'include'
    })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'confirmed') {
          setStatus('Payment confirmed! Redirecting to companions...');
          setTimeout(() => {
            window.location.href = '/companions';
          }, 2000);
        } else {
          setStatus('Payment confirmation failed. Please contact support.');
        }
      })
      .catch(() => {
        setStatus('Payment confirmation failed. Please contact support.');
      });
  }, []);

  return (
    <main style={{ 
      maxWidth: 720, 
      margin: '40px auto', 
      fontFamily: 'system-ui',
      textAlign: 'center',
      padding: '0 20px'
    }}>
      <div style={{ 
        padding: '40px',
        backgroundColor: '#f9f9f9',
        borderRadius: '16px',
        margin: '40px 0'
      }}>
        <div style={{ fontSize: '3rem', marginBottom: '20px' }}>
          {status.includes('confirmed') ? '✅' : 
           status.includes('failed') ? '❌' : '⏳'}
        </div>
        <h1 style={{ margin: '0 0 20px 0' }}>Payment Status</h1>
        <p style={{ fontSize: '1.1rem', color: '#666' }}>{status}</p>
        
        {status.includes('failed') && (
          <div style={{ marginTop: '30px' }}>
            <button
              onClick={() => window.location.href = '/pricing'}
              style={{
                padding: '12px 24px',
                backgroundColor: '#2196F3',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                marginRight: '10px'
              }}
            >
              Try Again
            </button>
            <button
              onClick={() => window.location.href = '/'}
              style={{
                padding: '12px 24px',
                backgroundColor: '#666',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              Go Home
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
