import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

type Msg = { role: 'user'|'assistant', content: string };

export default function Chat() {
  const router = useRouter();
  const { id } = router.query;
  const [msg, setMsg] = useState('');
  const [log, setLog] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);
  const [companion, setCompanion] = useState<any>(null);

  // Load companion info when ID is available
  useEffect(() => {
    if (id) {
      fetch(`${API}/companions`)
        .then(r => r.json())
        .then(companions => {
          const comp = companions.find((c: any) => c.id === id);
          if (comp) setCompanion(comp);
        })
        .catch(err => console.error('Failed to load companion:', err));
    }
  }, [id]);

  const send = async () => {
    if (!msg || busy || !id) return;
    const m = msg; 
    setMsg(''); 
    setLog(l => [...l, {role:'user', content:m}]); 
    setBusy(true);
    
    try {
      const r = await fetch(`${API}/chat`, { 
        method:'POST', 
        headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify({ 
          companion_id: id, 
          message: m,
          user_id: "demo_user" 
        }) 
      });
      
      if (!r.ok) {
        const errorText = await r.text();
        throw new Error(errorText);
      }
      
      const j = await r.json();
      setLog(l => [...l, {role:'assistant', content: j.reply }]);
    } catch (e: any) {
      const errorMsg = e?.message || 'Chat failed';
      if (errorMsg.includes('not available') || errorMsg.includes('403')) {
        setLog(l => [...l, {role:'assistant', content: 'This companion is not available for your current tier. Please upgrade to access all companions!'}]);
      } else if (errorMsg.includes('limit reached') || errorMsg.includes('429')) {
        setLog(l => [...l, {role:'assistant', content: 'You have reached your message limit for the free tier. Please upgrade to continue chatting!'}]);
      } else {
        setLog(l => [...l, {role:'assistant', content: 'Error: '+ errorMsg}]);
      }
    } finally { 
      setBusy(false); 
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <main style={{maxWidth:720, margin:'40px auto', fontFamily:'system-ui', padding: '0 20px'}}>
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={() => router.push('/companions')}
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#f0f0f0', 
            border: '1px solid #ddd', 
            borderRadius: '6px',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
        >
          ← Back to Companions
        </button>
        
        {companion && (
          <div style={{ 
            textAlign: 'center', 
            marginBottom: '20px',
            padding: '20px',
            backgroundColor: '#f9f9f9',
            borderRadius: '12px'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>
              {companion.gender === 'female' ? '👸' : '🤴'}
            </div>
            <h1 style={{ margin: '0 0 5px 0' }}>Chat with {companion.name}</h1>
            <p style={{ color: '#666', margin: '0 0 10px 0' }}>{companion.bio}</p>
            <div>
              {companion.traits.map((trait: string) => (
                <span key={trait} style={{ 
                  display: 'inline-block',
                  backgroundColor: '#e0e0e0',
                  padding: '3px 8px',
                  borderRadius: '10px',
                  fontSize: '0.8rem',
                  margin: '2px'
                }}>
                  {trait}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div style={{
        border:'1px solid #ddd', 
        padding:16, 
        borderRadius:12, 
        minHeight:400,
        backgroundColor: '#fafafa',
        marginBottom: '16px',
        maxHeight: '500px',
        overflowY: 'auto'
      }}>
        {log.length === 0 && (
          <p style={{ color: '#888', textAlign: 'center', margin: '20px 0' }}>
            Start your conversation with {companion?.name || 'your companion'}...
          </p>
        )}
        {log.map((m,i)=>(
          <div key={i} style={{ 
            marginBottom: '16px',
            padding: '12px',
            borderRadius: '8px',
            backgroundColor: m.role === 'user' ? '#e3f2fd' : '#f5f5f5'
          }}>
            <p style={{ margin: '0', fontSize: '0.9rem' }}>
              <strong style={{ color: m.role === 'user' ? '#1976d2' : '#4caf50' }}>
                {m.role === 'user' ? 'You' : companion?.name || 'Companion'}:
              </strong>
            </p>
            <p style={{ margin: '8px 0 0 0', lineHeight: '1.4' }}>{m.content}</p>
          </div>
        ))}
      </div>

      <div style={{display:'flex', gap:8, marginBottom: '20px'}}>
        <textarea 
          value={msg} 
          onChange={e=>setMsg(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..." 
          style={{
            flex:1, 
            padding:12, 
            borderRadius: '8px',
            border: '1px solid #ddd',
            resize: 'vertical',
            minHeight: '60px',
            fontFamily: 'inherit'
          }} 
        />
        <button 
          onClick={send} 
          disabled={busy}
          style={{
            padding: '12px 24px',
            backgroundColor: busy ? '#ccc' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: busy ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {busy ? 'Sending...' : 'Send'}
        </button>
      </div>

      <div style={{ 
        textAlign: 'center', 
        padding: '15px',
        backgroundColor: '#fff3e0',
        borderRadius: '8px',
        border: '1px solid #ffcc02'
      }}>
        <p style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#f57c00' }}>
          Free tier: Limited messages • Upgrade for unlimited conversations
        </p>
        <button
          onClick={() => router.push('/pricing')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#ff9800',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          View Upgrade Options
        </button>
      </div>
    </main>
  );
}
