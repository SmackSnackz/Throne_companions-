import { useRouter } from 'next/router';
import { useState } from 'react';

const API = process.env.NEXT_PUBLIC_BACKEND_URL!;

type Msg = { role: 'user'|'assistant', content: string };

export default function Chat() {
  const router = useRouter();
  const { id } = router.query;
  const [msg, setMsg] = useState('');
  const [log, setLog] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);

  const send = async () => {
    if (!msg || busy || !id) return;
    const m = msg; setMsg(''); setLog(l => [...l, {role:'user', content:m}]); setBusy(true);
    try {
      const r = await fetch(`${API}/chat`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ companion_id: id, message: m }) });
      if (!r.ok) {
        const t = await r.text(); throw new Error(t);
      }
      const j = await r.json();
      setLog(l => [...l, {role:'assistant', content: j.reply }]);
    } catch (e:any) {
      setLog(l => [...l, {role:'assistant', content: 'Error: '+ (e?.message || 'failed')}]);
    } finally { setBusy(false); }
  };

  return (
    <main style={{maxWidth:720, margin:'40px auto', fontFamily:'system-ui'}}>
      <h1>Chat: {id}</h1>
      <div style={{border:'1px solid #ddd', padding:16, borderRadius:12, minHeight:300}}>
        {log.map((m,i)=>(<p key={i}><b>{m.role==='user'?'You':'Companion'}:</b> {m.content}</p>))}
      </div>
      <div style={{display:'flex', gap:8, marginTop:12}}>
        <input value={msg} onChange={e=>setMsg(e.target.value)} placeholder="Type..." style={{flex:1, padding:8}} />
        <button onClick={send} disabled={busy}>
          {busy?'Sending…':'Send'}
        </button>
      </div>
      <p style={{marginTop:8}}><a href="/pricing">Upgrade for longer chats</a></p>
    </main>
  );
      }
