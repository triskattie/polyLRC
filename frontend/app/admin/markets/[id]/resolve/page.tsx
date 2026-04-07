"use client"

import { use, useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import type { Market, Outcome } from "@/lib/types"
import Link from "next/link"

export default function ResolveMarketPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()

  const [selectedOutcomeId, setSelectedOutcomeId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const { data: market, isLoading, isError } = useQuery<Market>({
    queryKey: ["market", id],
    queryFn: async () => (await api.get(`/markets/${id}`)).data,
  })

  const canResolve = market && ["CLOSED", "OPEN"].includes(market.state)
  const isAlreadyResolved = market?.state === "RESOLVED"

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    if (!selectedOutcomeId) {
      setError("Please select a winning outcome.")
      setLoading(false)
      return
    }

    try {
      await api.post(`/markets/${id}/resolve`, {
        winning_outcome_id: selectedOutcomeId,
      })
      setSuccess(true)
      setTimeout(() => {
        router.push(`/markets/${id}`)
      }, 2000)
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Failed to resolve market.")
    } finally {
      setLoading(false)
    }
  }

  if (isLoading) return <p style={{ padding: 40, fontFamily: "monospace" }}>Loading...</p>
  if (isError) return <p style={{ padding: 40, fontFamily: "monospace" }}>Market not found.</p>
  if (!market) return null

  return (
    <main className="app-shell">

      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/dashboard" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          <Link href={`/markets/${id}`} style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>← Market</Link>
          <Link href="/markets" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>Markets</Link>
        </div>
      </nav>

      <section style={{ padding: "60px 48px", maxWidth: 800, margin: "0 auto" }}>
        <p style={{ fontSize: 12, marginBottom: 16, color: "#d4af37", letterSpacing: "0.08em" }}>ADMIN — RESOLVE MARKET</p>
        
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 48 }}>
          <div>
            <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 400, marginBottom: 12 }}>
              Resolve <em style={{ color: "#d4af37" }}>market.</em>
            </h1>
          </div>
          <Link href={`/markets/${id}`} className="button button-outline" style={{ fontSize: 11 }}>
            View market
          </Link>
        </div>

        <p style={{ fontSize: 20, marginBottom: 20, color: "#d4af37"}}>{market.title}</p>

        {isAlreadyResolved ? (
          <div style={{ padding: "20px 24px", border: "1px solid rgba(74,222,128,0.2)", background: "rgba(74,222,128,0.05)", marginBottom: 32 }}>
            <p style={{ fontSize: 12, color: "#4ade80" }}>
              Market is already resolved. Winning outcome: <strong>{market.outcomes.find(o => o.id === market.winning_outcome_id)?.name ?? "Unknown"}</strong>
            </p>
          </div>
        ) : !canResolve ? (
          <div style={{ padding: "20px 24px", border: "1px solid rgba(248,113,113,0.2)", background: "rgba(248,113,113,0.05)", marginBottom: 32 }}>
            <p style={{ fontSize: 12, color: "#f87171" }}>
              Market must be in OPEN or CLOSED state to resolve.
            </p>
          </div>
        ) : null}

        <form onSubmit={handleResolve} style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <fieldset style={{ border: "none", padding: 0, margin: 0 }}>
            <legend style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", letterSpacing: "0.08em", marginBottom: 16, textTransform: "uppercase" }}>
              Select Winning Outcome
            </legend>
            
            <div>
              {market.outcomes.map((outcome) => (
                <label
                  key={outcome.id}
                  className={`outcome-option ${selectedOutcomeId === outcome.id ? 'selected' : ''}`}
                  style={{ cursor: canResolve ? "pointer" : "not-allowed", opacity: canResolve ? 1 : 0.6 }}
                >
                  <div className="outcome-name">
                    <input
                      type="radio"
                      name="winning-outcome"
                      value={outcome.id}
                      checked={selectedOutcomeId === outcome.id}
                      onChange={(e) => setSelectedOutcomeId(e.target.value)}
                      disabled={!canResolve}
                    />
                    {outcome.name}
                  </div>
                  {outcome.description && (
                    <span className="outcome-description">{outcome.description}</span>
                  )}
                </label>
              ))}
            </div>
          </fieldset>

          {error && (
            <p style={{ fontSize: 12, color: "#f87171", padding: "10px 14px", border: "1px solid rgba(248,113,113,0.2)", background: "rgba(248,113,113,0.05)" }}>
              {error}
            </p>
          )}

          {success && (
            <p style={{ fontSize: 12, color: "#4ade80", padding: "10px 14px", border: "1px solid rgba(74,222,128,0.2)", background: "rgba(74,222,128,0.05)" }}>
              Market resolved successfully. Redirecting...
            </p>
          )}

          <div style={{ display: "flex", gap: 12 }}>
            <button
              type="submit"
              disabled={loading || !canResolve || isAlreadyResolved || !selectedOutcomeId}
              className="button button-full"
              style={{ opacity: (loading || !canResolve || isAlreadyResolved || !selectedOutcomeId) ? 0.5 : 1 }}
            >
              {loading ? "Resolving..." : "Resolve market"}
            </button>
            <Link href={`/markets/${id}`} className="button button-outline">
              Cancel
            </Link>
          </div>
        </form>

        <div style={{ marginTop: 48, padding: "24px", border: "1px solid rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.02)" }}>
          <p style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", letterSpacing: "0.08em", marginBottom: 12, textTransform: "uppercase" }}>Market Info</p>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, fontSize: 12 }}>
            <div>
              <p style={{ color: "rgba(255,255,255,0.3)", marginBottom: 4 }}>State</p>
              <p style={{ color: "#d4af37", fontWeight: 500 }}>{market.state}</p>
            </div>
            <div>
              <p style={{ color: "rgba(255,255,255,0.3)", marginBottom: 4 }}>Created</p>
              <p style={{ color: "#e8e6e1", fontFamily: "monospace", fontSize: 11 }}>
                {new Date(market.created_at).toLocaleString()}
              </p>
            </div>
            <div>
              <p style={{ color: "rgba(255,255,255,0.3)", marginBottom: 4 }}>Updated</p>
              <p style={{ color: "#e8e6e1", fontFamily: "monospace", fontSize: 11 }}>
                {new Date(market.updated_at).toLocaleString()}
              </p>
            </div>
          </div>
          {market.description && (
            <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid rgba(255,255,255,0.05)" }}>
              <p style={{ color: "rgba(255,255,255,0.3)", marginBottom: 8, fontSize: 11 }}>Description</p>
              <p style={{ color: "rgba(255,255,255,0.6)", fontSize: 12, lineHeight: 1.5 }}>
                {market.description}
              </p>
            </div>
          )}
        </div>
      </section>

      <footer style={{ padding: "24px 48px", display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.2)" }}>PolyLRC - CS final project</span>
        <div style={{ display: "flex", gap: 20, fontSize: 11, color: "rgba(255,255,255,0.3)" }}>
          <a href="https://triskattie.com">triskattie.com</a>
          <Link href="/feedback">Feedback</Link>
          <Link href="/docs">Docs</Link>
          <Link href="/markets">Markets</Link>
        </div>
      </footer>
    </main>
  )
}