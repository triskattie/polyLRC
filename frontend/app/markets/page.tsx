"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type { MarketsPage, Market, WalletResponse, User } from "@/lib/types"

const marketStateClass = {
  OPEN: "market-state--open",
  CLOSED: "market-state--closed",
  RESOLVED: "market-state--resolved",
  DRAFT: "market-state--draft",
} as const

export default function MarketsListPage() {
  const { data, isLoading, isError } = useQuery<MarketsPage>({
    queryKey: ["markets"],
    queryFn: async () => {
      const res = await api.get("/markets")
      return res.data
    },
  })

  const { data: wallet } = useQuery<WalletResponse>({
    queryKey: ["wallet"],
    queryFn: async () => (await api.get("/wallet")).data
  })

  const { data: user } = useQuery<User>({
    queryKey: ["user"],
    queryFn: async () => (await api.get("/users/me")).data
  })

  return (
    <main className="app-shell">
      <nav className="site-nav">
        <Link href="/dashboard" className="site-brand">POLYLRC</Link>
        <div className="site-nav-links">
          <Link href="/dashboard" className="site-nav-link">← Dashboard</Link>
          {user?.role === "admin" && (<Link href="/admin/markets/create" className="site-nav-link">Create market</Link>)}
          <p className="accent" style={{ fontSize: 13, letterSpacing: "0.08em", margin: 0 }}>{wallet ? parseFloat(wallet.balance).toFixed(2) : "-"} POLY</p>
        </div>
      </nav>

      <section className="section section--spacious">
        <p className="page-eyebrow">
          PREDICTION MARKETS
        </p>
        <h1 className="page-title page-title--xl" style={{ marginBottom: 48 }}>
          Open <em className="accent">markets.</em>
        </h1>

        {isLoading && (
          <p className="page-copy">Loading...</p>
        )}

        {isError && (
          <p className="red" style={{ fontSize: 12, padding: "10px 14px", border: "1px solid rgba(248,113,113,0.2)" }}>
            Failed to load markets.
          </p>
        )}

        {data?.markets.length === 0 && (
          <p className="page-copy">No markets yet.</p>
        )}

        <div className="surface-list">
          {data?.markets.map((market: Market) => (
            <Link key={market.id} href={`/markets/${market.id}`} className="market-card">
              <div className="market-card-header">
                <strong className="market-card-title">{market.title}</strong>
                <span className={`market-state ${marketStateClass[market.state as keyof typeof marketStateClass] ?? "market-state--draft"}`}>
                  {market.state}
                </span>
              </div>
              <p className="market-card-description">{market.description}</p>
              <div className="market-card-outcomes">
                {market.outcomes.map(o => (
                  <span key={o.id} className={`market-pill ${o.id === market.winning_outcome_id ? "market-pill--selected" : ""}`}>
                    {o.name}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </section>

      <footer className="site-footer">
        <span className="site-footer-copy">PolyLRC - CS final project</span>
        <div className="site-footer-links">
          <a className="site-footer-link" href="https://triskattie.com">triskattie.com</a>
          <Link href="/feedback">Feedback</Link>
          <Link href="/docs">Docs</Link>
          <Link href="/markets">Markets</Link>
          <Link href="/register">Register</Link>
          <Link href="/login">Login</Link>
        </div>
      </footer>
    </main>
  )
}