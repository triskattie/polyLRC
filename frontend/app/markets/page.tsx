"use client"

import Link from "next/link"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type { MarketsPage, Market } from "@/lib/types"

export default function MarketsPage() {
  const { data, isLoading, isError } = useQuery<MarketsPage>({
    queryKey: ["markets"],
    queryFn: async () => {
      const res = await api.get("/markets")
      return res.data
    },
  })

  if (isLoading) return <p style={{ padding: 40 }}>Loading...</p>
  if (isError) return <p style={{ padding: 40 }}>Failed to load markets.</p>

  return (
    <main style={{ padding: 40, maxWidth: 800, margin: "0 auto" }}>
      <nav style={{ display: "flex", justifyContent: "space-between", marginBottom: 40 }}>
        <Link href="/">PolyLRC</Link>
        <Link href="/wallet">Wallet</Link>
      </nav>

      <h1 style={{ marginBottom: 24 }}>Markets</h1>

      {data?.markets.length === 0 && <p>No markets yet.</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {data?.markets.map((market: Market) => (
          <Link key={market.id} href={`/markets/${market.id}`} style={{ textDecoration: "none", color: "inherit" }}>
            <div style={{ border: "1px solid rgba(255,255,255,0.15)", padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <strong>{market.title}</strong>
                <span>{market.state}</span>
              </div>
              <p style={{ fontSize: 13, marginBottom: 12, opacity: 0.6 }}>{market.description}</p>
              <div style={{ display: "flex", gap: 8 }}>
                {market.outcomes.map(o => (
                  <span key={o.id} style={{ fontSize: 12, border: "1px solid rgba(255,255,255,0.2)", padding: "2px 8px" }}>
                    {o.name}
                  </span>
                ))}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </main>
  )
}