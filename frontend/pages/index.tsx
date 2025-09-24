import Link from 'next/link';

export default function Home() {
  return (
    <main style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'system-ui', padding: '0 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '50px' }}>
        <h1 style={{ fontSize: '3rem', margin: '0 0 20px 0' }}>🏛️ THRONE COMPANIONS</h1>
        <p style={{ fontSize: '1.3rem', color: '#666', margin: '0 0 10px 0' }}>
          Personal AI companions that earn trust, sharpen minds, and guide lives
        </p>
        <p style={{ fontSize: '1rem', color: '#888' }}>
          Root Principle: Every person deserves a companion.
        </p>
      </div>

      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h3 style={{ margin: '0 0 30px 0' }}>Meet Your Companions</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px' }}>
            <h4>Aurora</h4>
            <p>Sleek strategist, executive presence</p>
          </div>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px' }}>
            <h4>Sophia</h4>
            <p>Warm wisdom, poetic insight</p>
          </div>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px' }}>
            <h4>Vanessa</h4>
            <p>Bold energy, magnetic presence</p>
          </div>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px' }}>
            <h4>Cassian</h4>
            <p>Protective tactician, grounded wisdom</p>
          </div>
          <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '12px' }}>
            <h4>Lysander</h4>
            <p>Brilliant intellect, dreamy strategist</p>
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '50px' }}>
        <Link href="/companions" style={{ 
          display: 'inline-block', 
          padding: '15px 30px', 
          backgroundColor: '#4CAF50', 
          color: 'white', 
          textDecoration: 'none', 
          borderRadius: '8px',
          marginRight: '20px',
          fontSize: '1.1rem'
        }}>
          Enter Companions
        </Link>
        <Link href="/pricing" style={{ 
          display: 'inline-block', 
          padding: '15px 30px', 
          backgroundColor: '#2196F3', 
          color: 'white', 
          textDecoration: 'none', 
          borderRadius: '8px',
          fontSize: '1.1rem'
        }}>
          View Tiers
        </Link>
      </div>
    </main>
  );
}
