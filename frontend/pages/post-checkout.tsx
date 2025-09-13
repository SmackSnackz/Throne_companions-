import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_BACKEND_URL!;

export default function PostCheckout(){
  const [ok, setOk] = useState('Confirming…');
  useEffect(()=>{
    const id = new URLSearchParams(window.location.search).get('session_id');
    if(!id){ setOk('Missing session_id'); return; }
    fetch(`${API}/stripe/confirm?session_id=`+id, {credentials:'include'})
      .then(r=>r.json()).then(()=>{
        setOk('Confirmed. Redirecting…');
        setTimeout(()=>window.location.href='/companions', 800);
      }).catch(()=>setOk('Confirmation failed'));
  },[]);
  return <main style={{maxWidth:720, margin:'40px auto', fontFamily:'system-ui'}}><h1>{ok}</h1></main>
}
