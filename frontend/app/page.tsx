import Link from "next/link"
import { start } from "repl"

export default function LandingPage() {
  return (
    <main>
      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .button-full { background: #ffb300}
        .button-outline { border: 1px solid rgba(255,255,255, 0.3); }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 14px}
      `}</style>
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px" }}>
        <Link href="">PolyLRC</Link>
        <a href="triskattie.com">triskattie.com</a>
        <Link href="/markets">Launch App</Link>
      </nav>
      <section style={{ padding: "100px 48px 80px", maxWidth: 1000, margin: "0 auto" }}>
        <p>CS final project - prediction market</p>
        <h1 style={{ alignContent: "center", fontFamily: "'Playfair Display', serif", fontSize: "clamp(40px, 7vw, 60px)", fontWeight: 400, lineHeight: 1.05 }}>
          Trade what you <br /> <em style={{ color: "#ffc800"}}>think will happen</em>
          </h1>
        <p style={{ marginBottom: "10px" }}>A minimal prediction market where you trade outcomes on school events using a real orderbook exchange.</p>
        <div>
          <Link href="/markets" className="button button-full">Get started</Link>
          <Link href="/docs" className="button button-outline">How it works</Link>
        </div>
      </section>
    </main>
  )
}