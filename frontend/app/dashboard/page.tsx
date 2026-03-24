"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type { MarketsPage, Market, WalletResponse, Order, User, TransactionsPage } from "@/lib/types"

export default function DashboardPage() {
  const { data: wallet } = useQuery<WalletResponse>({
    queryKey: ["wallet"],
    queryFn: async () => (await api.get("/wallet")).data,
  })

  const { data: markets } = useQuery<MarketsPage>({
    queryKey: ["markets", "open"],
    queryFn: async () => (await api.get("/markets", { params: { state: "OPEN", limit: 5 } })).data,
  })

  // const { data: orders } = useQuery<Order[]>({
  //   queryKey: ["orders", "recent"],
  //   queryFn: async () => (await api.get("/orders", { params: { limit: 5 } })).data,
  // })

  const { data: transactions } = useQuery<TransactionsPage>({
    queryKey: ["transactions"],
    queryFn: async () => (await api.get("/wallet/transactions")).data,
  })

  const { data: user } = useQuery<User>({
    queryKey: ["me"],
    queryFn: async () => (await api.get("/users/me")).data,
  })

  return (
    <main style={{ fontFamily: "'IBM Plex Mono', monospace", background: "#0d0f14", color: "#e8e6e1", minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .button-full { background: #d4af37; color: #000000; }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.08em; }
        a { text-decoration: none; color: inherit; }
        .card { border: 1px solid rgba(255,255,255,0.1); padding: 24px; }
        .row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 12px; }
        .row:last-child { border-bottom: none; }
        .section-title { font-size: 11px; color: rgba(255,255,255,0.3); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
        .dim { color: rgba(255,255,255,0.4); }
        .green { color: #4ade80; }
        .gold { color: #d4af37; }
      `}</style>

      <nav style={{ display: "flex", justifyContent: "space-between", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
        <div style={{ display: "flex", gap: 24}}>
          <Link href="/markets" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, letterSpacing: "0.08em" }}>Markets</Link>
          {/* <Link href="/wallet" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, letterSpacing: "0.08em" }}>Wallet</Link> */}
          {user?.role === "admin" && (<Link href="/admin/markets/create" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, letterSpacing: "0.08em" }}>Create market</Link>)}
          <p style={{ color: "#d4af37", fontSize: 14, letterSpacing: "0.08em" }}>{wallet ? parseFloat(wallet.balance).toFixed(2) : "-"} POLY</p>
        </div>
      </nav>

      <section style={{ padding: "60px 48px", maxWidth: 1000, margin: "0 auto" }}>
        <p style={{ fontSize: 12, marginBottom: 16, color: "#d4af37", letterSpacing: "0.08em" }}>DASHBOARD</p>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 400, lineHeight: 1.05, marginBottom: 48 }}>
          Overview.
        </h1>

        <div className="card" style={{ marginBottom: 24 }}>
          <div className="section-title">
            <span>Wallet balance</span>
            <Link href="/wallet" className="dim" style={{ fontSize: 11 }}>View all →</Link>
          </div>
          <p style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 300, color: "#d4af37" }}>
            {wallet ? parseFloat(wallet.balance).toFixed(2) : "-"}
            <span style={{ fontSize: 16, color: "rgba(255,255,255,0.3)", marginLeft: 8 }}>POLY</span>
          </p>
        </div>

        <div style={{ marginBottom: 24 }}>
          <div className="card">
            <div className="section-title">
              <span>Recent transactions</span>
            </div>
            {!transactions?.transactions.length && <p className="dim" style={{ fontSize: 12 }}>No transactions yet.</p>}
            {transactions?.transactions.map((t) => (
              <div key={t.transaction_id} className="row">
                <span>{t.transaction_type}</span>
                <span style={{ color: parseFloat(t.amount) >= 0 ? "#4ade80" : "#f87171" }}>
                  {parseFloat(t.amount) >= 0 ? "+" : ""}{parseFloat(t.amount).toFixed(2)} POLY
                </span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: 24 }}>
          <div className="card">
            <div className="section-title">
              <span>Open markets</span>
              <Link href="/markets" className="dim" style={{ fontSize: 11 }}>View all →</Link>
            </div>
            {!markets?.markets.length && <p className="dim" style={{ fontSize: 12 }}>No open markets.</p>}
            {markets?.markets.map((m: Market) => (
              <div key={m.id} className="row">
                <Link href={`/markets/${m.id}`} style={{ fontSize: 12 }}>{m.title}</Link>
                <span className="green" style={{ fontSize: 11 }}>OPEN</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer style={{ padding: "24px 48px", display: "flex", justifyContent: "space-between", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.2)" }}>PolyLRC - CS final project</span>
        <div style={{ display: "flex", gap: 20, fontSize: 11, color: "rgba(255,255,255,0.3)" }}>
          <a href="https://triskattie.com">triskattie.com</a>
          <Link href="/markets">Markets</Link>
        </div>
      </footer>
    </main>
  )
}