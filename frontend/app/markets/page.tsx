"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type { MarketsPage, Market, WalletResponse, User } from "@/lib/types"

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
    <main style={{ fontFamily: "'IBM Plex Mono', monospace", background: "#0d0f14", color: "#e8e6e1", minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .button-full { background: #d4af37; color: #000000; }
        .button-outline { border: 1px solid rgba(255,255,255,0.3); color: #e8e6e1; }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.08em; }
        .market-card { border: 1px solid rgba(255,255,255,0.1); padding: 24px; transition: border-color 0.2s; text-decoration: none; color: inherit; display: block; }
        .market-card:hover { border-color: rgba(212,175,55,0.4); }
        a { text-decoration: none; color: inherit; }
      `}</style>

      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          <Link href="/wallet" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, letterSpacing: "0.08em" }}>Wallet</Link>
          {user?.role === "admin" && (<Link href="/admin/markets/create" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, letterSpacing: "0.08em" }}>Create market</Link>)}
          <Link href="/login" className="button button-full" style={{ fontSize: 11 }}>Account</Link>
          <p style={{ color: "#d4af37", fontSize: 14, letterSpacing: "0.08em" }}>{wallet ? parseFloat(wallet.balance).toFixed(2) : "-"} POLY</p>
        </div>
      </nav>

      <section style={{ padding: "80px 48px", maxWidth: 1000, margin: "0 auto" }}>
        <p style={{ fontSize: 12, marginBottom: 25, color: "#d4af37", letterSpacing: "0.08em" }}>
          PREDICTION MARKETS
        </p>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(36px, 5vw, 60px)", fontWeight: 400, lineHeight: 1.05, marginBottom: 48 }}>
          Open <em style={{ color: "#d4af37" }}>markets.</em>
        </h1>

        {isLoading && (
          <p style={{ color: "rgba(255,255,255,0.4)", fontSize: 13 }}>Loading...</p>
        )}

        {isError && (
          <p style={{ fontSize: 12, color: "#f87171", padding: "10px 14px", border: "1px solid rgba(248,113,113,0.2)" }}>
            Failed to load markets.
          </p>
        )}

        {data?.markets.length === 0 && (
          <p style={{ color: "rgba(255,255,255,0.4)", fontSize: 13 }}>No markets yet.</p>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 1, background: "rgba(255,255,255,0.04)" }}>
          {data?.markets.map((market: Market) => (
            <Link key={market.id} href={`/markets/${market.id}`} className="market-card" style={{ background: "#0d0f14" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                <strong style={{ fontSize: 15, fontFamily: "'Playfair Display', serif", fontWeight: 400 }}>{market.title}</strong>
                <span style={{ fontSize: 11, color: market.state === "OPEN" ? "#4ade80" : "rgba(255,255,255,0.3)", letterSpacing: "0.08em", marginLeft: 16, flexShrink: 0 }}>
                  {market.state}
                </span>
              </div>
              <p style={{ fontSize: 12, marginBottom: 16, color: "rgba(255,255,255,0.4)", lineHeight: 1.6 }}>{market.description}</p>
              <div style={{ display: "flex", gap: 8 }}>
                {market.outcomes.map(o => (
                  <span key={o.id} style={{ fontSize: 11, border: "1px solid rgba(255,255,255,0.15)", padding: "2px 10px", letterSpacing: "0.05em" }}>
                    {o.name}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </section>

      <footer style={{ padding: "24px 48px", display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.2)" }}>PolyLRC - CS final project</span>
        <div style={{ display: "flex", gap: 20, fontSize: 11, color: "rgba(255,255,255,0.3)" }}>
          <a href="https://triskattie.com">triskattie.com</a>
          <Link href="/register">Register</Link>
          <Link href="/login">Login</Link>
        </div>
      </footer>
    </main>
  )
}