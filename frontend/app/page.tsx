import Link from "next/link"
import { start } from "repl"

export default function LandingPage() {
  return (
    <main style={{ fontFamily: "'IBM Plex Mono', monospace"}}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .button-full { background: #ffb300}
        .button-outline { border: 1px solid rgba(255,255,255, 0.3); }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 14px}
      `}</style>
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px" }}>
        <Link href="">PolyLRC</Link>
        <a href="← https://triskattie.com">triskattie.com</a>
        <Link href="/markets">Launch App</Link>
      </nav>
      <section style={{ padding: "100px 48px 80px", maxWidth: 1000, margin: "0 auto" }}>
        <p style={{ fontSize: "13px", marginBottom: "25px"}}>
          CS FINAL PROJECT - PREDICTION MARKET
        </p>
        <h1 style={{ alignContent: "center", fontFamily: "'Playfair Display', serif", fontSize: "clamp(40px, 7vw, 60px)", fontWeight: 400, lineHeight: 1.05, marginBottom: "25px" }}>
          Trade what you <br /> <em style={{ color: "#ffc800"}}>think will happen.</em>
          </h1>
        <p style={{ marginBottom: "25px", maxWidth: 590 }}>A minimal prediction market where you trade outcomes on school events using a real orderbook exchange. No real money.</p>
        <div>
          <Link href="/markets" className="button button-full">Get started</Link>
          <Link href="/docs" className="button button-outline">How it works</Link>
        </div>
      </section>

      <section style={{ margin: "0 auto", maxWidth: 1000, padding: "80px 48px" }}>
        <h1 style={{ fontSize: 20, marginBottom: "10px"}}>
          What is PolyLRC?
        </h1>
        <p style={{ margin: "auto" }}>
          PolyLRC is a prediction market platform. Users trade binary (YES/NO, TRUE/FALSE) outcomes on school events. Trades are executed through an order-book system with limit orders and price-time priority.
          The platform uses virtual tokens instead of real money.
        </p>
      </section>
      
      <section style={{ margin: "0 auto", maxWidth: 1000, padding: "80px 48px" }}>
        <h1 style={{ fontSize: 20, marginBottom: 20}}>
          How it works
        </h1>
        <ol>
          <li>1. Create an account and claim tokens through the faucet.</li>
          <li>2. Find open markets on upcoming school events.</li>
          <li>3. Submit limit orders at your chosen price. Collateral locked immediately.</li>
          <li>4. Orders match by price-time priority. Partial fills supported.</li>
          <li>5. Admin resolves the market. Winners get paid out.</li>
          <li>6. Your wallet balance updates after settlement</li>
        </ol>
      </section>

      <section style={{ margin: "0 auto", maxWidth: 1000, padding: "80px 48px" }}>
        <h1 style={{ fontSize: 20, marginBottom: 20}}>
          Built with
        </h1>
        <p>FastAPI, PostgreSQL, Redis, Next.js, SQLAlchemy, Podman</p>
      </section>

      <footer style={{ padding: "24px 48px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span>PolyLRC - CS final project</span>
        <div style={{ display: "flex", gap: 20 }}>
          <a href="https://triskattie.com">triskattie.com</a>
          <Link href="/register">Register</Link>
          <Link href="login">Login</Link>
        </div>
      </footer>
    </main>
  )
}