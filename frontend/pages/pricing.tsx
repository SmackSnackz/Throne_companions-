const API = process.env.NEXT_PUBLIC_BACKEND_URL!;

async function go(tier: string){
  const r = await fetch(`${API}/stripe/create-checkout-session`,{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({tier})});
  const j = await r.json();
  window.location.href = j.url;
}

export default function Pricing(){
  return (
    <main style={{maxWidth:720, margin:'40px auto', fontFamily:'system-ui'}}>
      <h1>Pricing</h1>
      <ul>
        <li><b>Friend</b> – $9.99/mo <button onClick={()=>go('friend')}>Subscribe</button></li>
        <li><b>Lover</b> – $29.99/mo <button onClick={()=>go('lover')}>Subscribe</button></li>
        <li><b>Spouse</b> – $99.99/mo <button onClick={()=>go('spouse')}>Subscribe</button></li>
      </ul>
    </main>
  );
}
