"use client"

import Link from "next/link"

const sections = [
  "What is a prediction market?",
  "The order book",
  "Placing an order",
  "How matching works",
  "Resolution and payout",
  "Full example",
]

export default function DocsPage() {
  return (
    <main style={{ fontFamily: "'IBM Plex Mono', monospace", background: "#0d0f14", color: "#e8e6e1", minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        a { text-decoration: none; color: inherit; }
        .button-full { background: #d4af37; color: #000000; }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.08em; }
        h2 { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 400; margin-bottom: 16px; color: #e8e6e1; }
        p { font-size: 13px; line-height: 2; color: rgba(232,230,225,0.7); margin-bottom: 16px; }
        .callout { border-left: 2px solid #d4af37; padding: 12px 20px; background: rgba(212,175,55,0.05); margin: 24px 0; }
        .callout p { margin: 0; }
        table { width: 100%; border-collapse: collapse; margin: 24px 0; font-size: 12px; }
        th { text-align: left; padding: 10px 16px; border-bottom: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.4); font-weight: 400; letter-spacing: 0.08em; font-size: 11px; }
        td { padding: 10px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); color: rgba(232,230,225,0.7); }
        .green { color: #4ade80; }
        .red { color: #f87171; }
        .gold { color: #d4af37; }
        .section { padding: 60px 0; border-top: 1px solid rgba(255,255,255,0.06); }
        .section:first-of-type { border-top: none; }
        .toc-link { font-size: 12px; color: rgba(255,255,255,0.35); transition: color 0.2s; display: block; padding: 4px 0; }
        .toc-link:hover { color: #d4af37; }
        .num { font-size: 11px; color: rgba(212,175,55,0.4); margin-bottom: 12px; letter-spacing: 0.06em; }
      `}</style>

      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          <Link href="/markets" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>Markets</Link>
          <Link href="/register" className="button button-full" style={{ fontSize: 11 }}>Get started</Link>
        </div>
      </nav>

      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "60px 48px", display: "grid", gridTemplateColumns: "180px 1fr", gap: 64 }}>

        <div style={{ position: "sticky", top: 40, alignSelf: "start" }}>
          <p style={{ fontSize: 11, color: "rgba(255,255,255,0.25)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 16 }}>Contents</p>
          {sections.map((s, i) => (
            <a key={i} href={`#section-${i}`} className="toc-link">{s}</a>
          ))}
        </div>

        <div>

          <p style={{ fontSize: 11, color: "#d4af37", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 16 }}>PolyLRC — Documentation</p>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 400, marginBottom: 24 }}>
            How PolyLRC <em style={{ color: "#d4af37" }}>works.</em>
          </h1>
          <p style={{ fontSize: 14, lineHeight: 2, maxWidth: 560, marginBottom: 0 }}>
            PolyLRC is a prediction market. This page explains everything you need to know to trade without financial background.
          </p>

          <div className="section" id="section-0">
            <div className="num">01</div>
            <h2>What is a prediction market?</h2>
            <p>
              A prediction market is a place where people trade on the outcome of future events. Instead of betting money, you buy shares in an outcome. Each share is worth either <strong style={{ color: "#d4af37" }}>1 POLY</strong> (if that outcome wins) or <strong style={{ color: "#d4af37" }}>0 POLY</strong> (if it loses).
            </p>
            <p>
              The price of a share reflects how likely people think that outcome is. A YES share trading at 0.70 means the people betting on the market thinks there is roughly a 70% chance of YES winning.
            </p>
            <div className="callout">
              <p>Think of it like this: if you buy a YES share for 0.30 POLY and YES wins, you receive 1 POLY back, a profit of 0.70 POLY. If NO wins, your share is worth nothing, losing 0.30 POLY.</p>
            </div>
            <p>
              On PolyLRC, every market has exactly two outcomes, usually YES and NO. Only one can win.
            </p>
          </div>

          <div className="section" id="section-1">
            <div className="num">02</div>
            <h2>The order book</h2>
            <p>
              PolyLRC uses an <strong style={{ color: "#e8e6e1" }}>order book</strong> to match buyers and sellers. An order book is a list of all the open buy and sell offers for a market.
            </p>
            <p>
              There are two sides to the book:
            </p>
            <table>
              <thead>
                <tr>
                  <th>Side</th>
                  <th>Who places it</th>
                  <th>What it means</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="green">BID (Buy)</td>
                  <td>A buyer</td>
                  <td>"I want to buy shares at this price or lower"</td>
                </tr>
                <tr>
                  <td className="red">ASK (Sell)</td>
                  <td>A seller</td>
                  <td>"I want to sell shares at this price or higher"</td>
                </tr>
              </tbody>
            </table>
            <p>
              Prices are always between 0 and 1. A price of 0.50 means you are paying 0.50 POLY per share.
            </p>
            <div className="callout">
              <p>Example order book for YES shares:</p>
              <table style={{ marginTop: 12, marginBottom: 0 }}>
                <thead>
                  <tr><th>Side</th><th>Price</th><th>Amount</th></tr>
                </thead>
                <tbody>
                  <tr><td className="red">ASK</td><td>0.65</td><td>100</td></tr>
                  <tr><td className="red">ASK</td><td>0.60</td><td>200</td></tr>
                  <tr><td className="green">BID</td><td>0.50</td><td>150</td></tr>
                  <tr><td className="green">BID</td><td>0.45</td><td>300</td></tr>
                </tbody>
              </table>
            </div>
            <p style={{ marginTop: 24 }}>
              The lowest ask (0.60) and the highest bid (0.50) don't overlap, so no trade happens yet: the book is resting.
            </p>
          </div>

          <div className="section" id="section-2">
            <div className="num">03</div>
            <h2>Placing an order</h2>
            <p>
              PolyLRC uses <strong style={{ color: "#e8e6e1" }}>limit orders</strong>. When you place a limit order you specify two things:
            </p>
            <table>
              <thead><tr><th>Field</th><th>What it means</th></tr></thead>
              <tbody>
                <tr><td className="gold">Price</td><td>The maximum you are willing to pay (BUY) or the minimum you will accept (SELL). Between 0 and 1.</td></tr>
                <tr><td className="gold">Amount</td><td>How many shares you want to buy or sell.</td></tr>
              </tbody>
            </table>
            <p>
              When you submit a BUY order, <strong style={{ color: "#e8e6e1" }}>collateral is locked immediately</strong>. This means the POLY needed to pay for your shares is reserved from your wallet right away: you cannot spend it on something else while the order is open.
            </p>
            <div className="callout">
              <p>You place a BUY order: 100 shares at 0.60. Your wallet is immediately reduced by 60 POLY (100 × 0.60). If your order is cancelled, the 60 POLY is returned.</p>
            </div>
            <p>
              For SELL orders, the collateral locked is <strong style={{ color: "#e8e6e1" }}>(1 − price) × amount</strong>. This covers your potential loss if the outcome you are selling wins against you.
            </p>
          </div>

          <div className="section" id="section-3">
            <div className="num">04</div>
            <h2>How matching works</h2>
            <p>
              When you place an order, PolyLRC checks the other side of the book to see if any existing orders can be matched with yours immediately.
            </p>
            <p>
              Matching follows two rules:
            </p>
            <table>
              <thead><tr><th>Rule</th><th>Meaning</th></tr></thead>
              <tbody>
                <tr><td className="gold">Price priority</td><td>The best-priced order matches first. For asks, the lowest price. For bids, the highest price.</td></tr>
                <tr><td className="gold">Time priority</td><td>If two orders have the same price, the one placed earlier matches first.</td></tr>
              </tbody>
            </table>
            <p>
              The trade executes at the <strong style={{ color: "#e8e6e1" }}>maker's price</strong>: the price of the order already resting in the book, not the incoming order.
            </p>
            <p>
              <strong style={{ color: "#e8e6e1" }}>Partial fills</strong> are supported. If you want to buy 200 shares but only 150 are available at your price, you will receive 150 shares immediately and the remaining 50 will rest in the book waiting for a seller.
            </p>
            <div className="callout">
              <p>You submit a BUY for 200 shares at 0.65. The book has an ASK for 200 shares at 0.60. Your order matches immediately at 0.60: you pay 120 POLY instead of 130 POLY, because the maker's price is used.</p>
            </div>
          </div>

          <div className="section" id="section-4">
            <div className="num">05</div>
            <h2>Resolution and payout</h2>
            <p>
              Once the event has concluded, an admin resolves the market by selecting the winning outcome.
            </p>
            <p>
              What happens next:
            </p>
            <table>
              <thead><tr><th>If you hold...</th><th>Payout</th></tr></thead>
              <tbody>
                <tr><td className="green">Winning outcome shares</td><td>1 POLY per share is added to your wallet</td></tr>
                <tr><td className="red">Losing outcome shares</td><td>Your position is cleared, no payout</td></tr>
              </tbody>
            </table>
            <p>
              All open (unmatched) orders are also cancelled at resolution. Any locked collateral from those orders is returned to your wallet.
            </p>
          </div>

          <div className="section" id="section-5">
            <div className="num">06</div>
            <h2>Full example</h2>
            <p>Let's walk through a complete trade from start to finish.</p>

            <p style={{ color: "#d4af37", fontSize: 12, letterSpacing: "0.08em", marginBottom: 8, marginTop: 24 }}>THE MARKET</p>
            <p>Market: <em>"Will our school get a 'very weak' rating again?"</em>, outcomes: YES and NO.</p>

            <p style={{ color: "#d4af37", fontSize: 12, letterSpacing: "0.08em", marginBottom: 8, marginTop: 24 }}>STEP 1 — You claim tokens</p>
            <p>You register and use the faucet to claim 200 POLY.</p>

            <p style={{ color: "#d4af37", fontSize: 12, letterSpacing: "0.08em", marginBottom: 8, marginTop: 24 }}>STEP 2 — You place a BUY order</p>
            <p>You think the school will get a 'very weak' rating. You place a BUY order for 200 YES shares at 0.70.</p>
            <p>Your wallet is reduced by 140 POLY (200 × 0.70) immediately as collateral.</p>

            <p style={{ color: "#d4af37", fontSize: 12, letterSpacing: "0.08em", marginBottom: 8, marginTop: 24 }}>STEP 3 — Your order matches</p>
            <p>There is a resting SELL order for 200 YES shares at 0.50. Since 0.50 is below your limit of 0.70, your order matches at 0.50. You only pay 100 POLY: 40 POLY is returned to your wallet from the locked collateral.</p>

            <table>
              <thead><tr><th>After matching</th><th></th></tr></thead>
              <tbody>
                <tr><td>Wallet</td><td>100 POLY (started with 200, paid 100)</td></tr>
                <tr><td>YES shares</td><td>200</td></tr>
              </tbody>
            </table>

            <p style={{ color: "#d4af37", fontSize: 12, letterSpacing: "0.08em", marginBottom: 8, marginTop: 24 }}>STEP 4 — Market resolves YES</p>
            <p>The school does get a 'very weak' rating. Admin resolves the market as YES.</p>
            <p>You receive 200 × 1 POLY = 200 POLY payout.</p>

            <table>
              <thead><tr><th>Final state</th><th></th></tr></thead>
              <tbody>
                <tr><td>Wallet</td><td className="green">300 POLY</td></tr>
                <tr><td>Profit</td><td className="green">+100 POLY</td></tr>
              </tbody>
            </table>

            <div className="callout" style={{ marginTop: 24 }}>
              <p>If YES had lost instead, your 200 shares would be worth 0 and you would have ended with 100 POLY: a loss of 100 POLY.</p>
            </div>
          </div>

          <div style={{ marginTop: 60, paddingTop: 40, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
            <p style={{ marginBottom: 20 }}>Ready to try it?</p>
            <Link href="/register" className="button button-full">Create account</Link>
          </div>

        </div>
      </div>

      <footer style={{ padding: "24px 48px", display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.2)" }}>PolyLRC - CS final project</span>
        <div style={{ display: "flex", gap: 20, fontSize: 11, color: "rgba(255,255,255,0.3)" }}>
          <a href="https://triskattie.com">triskattie.com</a>
          <Link href="/markets">Markets</Link>
        </div>
      </footer>
    </main>
  )
}