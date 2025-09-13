import Link from 'next/link';

export default function Home() {
  return (
    <main style={{maxWidth:720, margin:'40px auto', fontFamily:'system-ui'}}>
      <h1>Throne Companions</h1>
      <p>Meet Sophia, Vanessa, and Aurora. Chat free. Upgrade for more.</p>
      <p>
        <Link href="/companions">Enter Companions</Link> ·{' '}
        <Link href="/pricing">Pricing</Link>
      </p>
    </main>
  );
}
