'use client';

import { useState } from 'react';
import Link from "next/link"

export default function LandingPage() {
  const [isNotificationVisible, setIsNotificationVisible] = useState(true);

  const handleCloseNotification = () => {
    setIsNotificationVisible(false);
  };

  return (
    <main style={{ fontFamily: "'IBM Plex Mono', monospace", background: "#0d0f14", color: "#e8e6e1", minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .button-full { background: #d4af37; color: #000000}
        .button-outline { border: 1px solid rgba(255,255,255, 0.3); }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 12px, letter-spacing: 0.08em}
      `}</style>

      {isNotificationVisible && (
        <div style={{ background: "rgba(212, 175, 55, 0.1)", borderBottom: "1px solid rgba(212, 175, 55, 0.3)", padding: "16px 48px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <p style={{ fontSize: 12, color: "#d4af37", letterSpacing: "0.08em" }}>
            Welcome to PolyLRC! If you'd like to submit feedback, you may do so by submitting the form in the footer or by pressing <Link href="/feedback" style={{ textDecoration: "underline" }}>this</Link>.
          </p>
          <button 
            onClick={handleCloseNotification}
            style={{ background: "none", border: "none", color: "#d4af37", fontSize: 18, cursor: "pointer", padding: "0 8px" }}
          >
            ×
          </button>
        </div>
      )}

      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255, 255, 255, 0.1" }}>
        <Link href="/" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
        <a href="https://triskattie.com" style={{ color: "rgba(255, 255, 255, 0.3)", fontSize: 12, letterSpacing: "0.08em" }}>← triskattie.com</a>
        <Link href="/dashboard" className="button button-full" style={{ fontSize: 11}}>Launch App</Link>
      </nav>

      <section style={{ padding: "100px 48px 80px", maxWidth: 1000, margin: "0 auto" }}>
        <p style={{ fontSize: "12px", marginBottom: "25px", color: "#d4af37", letterSpacing: "0.08em" }}>
          CS FINAL PROJECT - PREDICTION MARKET
        </p>
        <h1 style={{ alignContent: "center", fontFamily: "'Playfair Display', serif", fontSize: "clamp(40px, 7vw, 80px)", fontWeight: 400, lineHeight: 1.05, marginBottom: "25px" }}>
          Trade what you <br /> <em style={{ color: "#d4af37" }}>think will happen.</em>
          </h1>
        <p style={{ marginBottom: "25px", maxWidth: 500, color: "rgba(255, 255, 255, 0.4)", lineHeight: 2, fontSize: 13 }}>A minimal prediction market where you trade outcomes on school events using a real orderbook exchange. No real money.</p>
        <div style={{ display: "flex", gap: 12 }}>
          <Link href="/dashboard" className="button button-full">Get started</Link>
          <Link href="/docs" className="button button-outline">How it works</Link>
        </div>
      </section>

      <hr style={{ maxWidth: 1000, margin: "0 auto", border: "none", borderTop: "1px solid rgba(255, 255, 255, 0.2)"}}></hr>

      <section style={{ margin: "0 auto", maxWidth: 1000, padding: "80px 48px" }}>
        <h1 style={{ fontSize: 20, marginBottom: "10px"}}>
          What is PolyLRC?
        </h1>
        <p style={{ margin: "auto" }}>
          PolyLRC is a prediction market platform. Users trade binary (YES/NO, TRUE/FALSE) outcomes on school events. Trades are executed through an order-book system with limit orders and price-time priority.
          The platform uses virtual tokens instead of real money.
        </p>
      </section>

      <hr style={{ maxWidth: 1000, margin: "0 auto", border: "none", borderTop: "1px solid rgba(255, 255, 255, 0.2)"}}></hr>

      <section style={{ margin: "0 auto", maxWidth: 1000, padding: "80px 48px" }}>
        <h1 style={{ fontSize: 20, marginBottom: 20}}>
          How it works
        </h1>
        <ul>
          <li>1. Create an account and claim tokens through the faucet.</li>
          <li>2. Find open markets on upcoming school events.</li>
          <li>3. Submit limit orders at your chosen price. Collateral locked immediately.</li>
          <li>4. Orders match by price-time priority. Partial fills supported.</li>
          <li>5. Admin resolves the market. Winners get paid out.</li>
          <li>6. Your wallet balance updates after settlement</li>
        </ul>
      </section>

      <hr style={{ maxWidth: 1000, margin: "0 auto", border: "none", borderTop: "1px solid rgba(255, 255, 255, 0.2)"}}></hr>

      <section style={{ margin: "0 auto", maxWidth: 1000, padding: "80px 48px" }}>
        <h1 style={{ fontSize: 20, marginBottom: 20}}>
          Built with
        </h1>
        <p>FastAPI, PostgreSQL, Redis, Next.js, SQLAlchemy, Podman</p>
      </section>

      <footer style={{ padding: "24px 48px", display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid rgba(255, 255, 255, 0.1)" }}>
        <span>PolyLRC - CS final project</span>
        <div style={{ display: "flex", gap: 20 }}>
          <a href="https://triskattie.com">triskattie.com</a>
          <Link href="/feedback">Feedback</Link>
          <Link href="/register">Register</Link>
          <Link href="login">Login</Link>
        </div>
      </footer>
    </main>
  )
}