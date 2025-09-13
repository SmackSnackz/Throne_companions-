import Link from 'next/link';
import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_BACKEND_URL!;

export default function Companions() {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => { fetch(`${API}/companions`).then(r=>r.json()).then(setData); }, []);
  return (
    <main style={{maxWidth:900, margin:'40px auto', fontFamily:'system-ui'}}>
      <h1>Companions</h1>
      <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(220px, 1fr))', gap:16}}>
        {data.map(c => (
          <div key={c.id} style={{border:'1px solid #ddd', padding:16, borderRadius:12}}>
            <h3>{c.name}</h3>
            <p>{c.bio}</p>
            <Link href={`/chat/${c.id}`}>Chat</Link>
          </div>
        ))}
      </div>
    </main>
  );
}
