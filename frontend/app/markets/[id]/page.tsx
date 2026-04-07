"use client"

import { use, useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type { Market, User, WalletResponse, Orderbook } from "@/lib/types"
import Link from "next/link"
import { Bar, BarChart, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"

export default function MarketPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const queryClient = useQueryClient()

  const [selectedOutcome, setSelectedOutcome] = useState<string | null>(null)
  const [side, setSide] = useState<"BUY" | "SELL">("BUY")
  const [price, setPrice] = useState("")
  const [amount, setAmount] = useState("")
  const [orderError, setOrderError] = useState<string | null>(null)
  const [orderSuccess, setOrderSuccess] = useState(false)

  const { data: market, isLoading, isError } = useQuery<Market>({
    queryKey: ["market", id],
    queryFn: async () => (await api.get(`/markets/${id}`)).data,
  })

  const { data: user } = useQuery<User>({
    queryKey: ["user"],
    queryFn: async () => (await api.get("/users/me")).data,
  })

  const { data: wallet } = useQuery<WalletResponse>({
    queryKey: ["wallet"],
    queryFn: async () => (await api.get("/wallet")).data,
  })

  const outcomeId = selectedOutcome ?? market?.outcomes[0]?.id ?? null

  const { data: orderbook } = useQuery<Orderbook>({
    queryKey: ["orderbook", id, outcomeId],
    queryFn: async () => (await api.get(`/markets/${id}/orderbook/${outcomeId}`)).data,
    enabled: !!outcomeId,
    refetchInterval: 5000,
  })

  const orderMutation = useMutation({
    mutationFn: async () => {
      return api.post("/orders", {
        market_id: id,
        outcome_id: outcomeId,
        side,
        price: parseFloat(price),
        amount: parseFloat(amount),
      })
    },
    onSuccess: () => {
      setOrderSuccess(true)
      setOrderError(null)
      setPrice("")
      setAmount("")
      queryClient.invalidateQueries({ queryKey: ["orderbook", id, outcomeId] })
      queryClient.invalidateQueries({ queryKey: ["wallet"] })
      setTimeout(() => setOrderSuccess(false), 3000)
    },
    onError: (err: any) => {
      setOrderError(err.response?.data?.detail ?? "Failed to place order.")
      setOrderSuccess(false)
    },
  })

  const handleOrder = (e: React.FormEvent) => {
    e.preventDefault()
    setOrderError(null)
    orderMutation.mutate()
  }

  const chartData = [
    ...(orderbook?.bids ?? []).map(b => ({ price: parseFloat(b.price).toFixed(2), amount: parseFloat(b.remaining), type: "bid" })),
    ...(orderbook?.asks ?? []).map(a => ({ price: parseFloat(a.price).toFixed(2), amount: parseFloat(a.remaining), type: "ask" })),
  ].sort((a, b) => parseFloat(a.price) - parseFloat(b.price))

  if (isLoading) return <p style={{ padding: 40, fontFamily: "monospace" }}>Loading...</p>
  if (isError) return <p style={{ padding: 40, fontFamily: "monospace" }}>Market not found.</p>
	if (!market) return null

  return (
    <main className="app-shell">

      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/dashboard" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          <Link href="/markets" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, letterSpacing: "0.08em" }}>← Markets</Link>
          {user?.role === "admin" && (
            <Link href="/admin/markets/create" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12, letterSpacing: "0.08em" }}>Create market</Link>
          )}
          <p style={{ color: "#d4af37", fontSize: 13, letterSpacing: "0.08em"}}>{wallet ? parseFloat(wallet.balance).toFixed(2) : "—"} POLY</p>
        </div>
      </nav>

      <section style={{ padding: "40px 48px 24px", maxWidth: 1200, margin: "0 auto" }}>
				<div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
					<div>
						<p style={{ fontSize: 11, color: "#d4af37", letterSpacing: "0.08em", marginBottom: 8 }}>{market.state}</p>
						<h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(24px, 3vw, 40px)", fontWeight: 400 }}>
							{market.title}
						</h1>
					</div>
          <div style={{}}>
            {user?.role === "admin" && market.state === "PRE" && (
              <Link href={`/admin/markets/${id}/seed`} className="button button-full" style={{ marginRight: 12}}>Seed market</Link>
            )}

            {user?.role === "admin" && (market.state === "PRE" || market.state === "OPEN") && (
              <Link href={`/admin/markets/${id}/edit`} className="button button-full" style={{ marginRight: 12}}>Edit market</Link>
            )}

            {user?.role === "admin" && (market.state === "OPEN" || market.state === "CLOSED") && (
              <Link href={`/admin/markets/${id}/resolve`} className="button button-full">Resolve market</Link>
            )}          
          </div>

				</div>
        <p style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", lineHeight: 1.8, maxWidth: 600, marginBottom: 24 }}>
          {market.description}
        </p>
        <div style={{ display: "flex", gap: 8 }}>
          {market.outcomes.map(o => (
            <button key={o.id} className={`outcome-tab ${outcomeId === o.id ? "active" : ""}`} onClick={() => setSelectedOutcome(o.id)}>
              {o.name}
            </button>
          ))}
        </div>
      </section>

      <hr style={{ maxWidth: 1200, margin: "0 auto", border: "none", borderTop: "1px solid rgba(255,255,255,0.08)" }} />

      <section style={{ padding: "32px 48px 60px", maxWidth: 1200, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 320px", gap: 32 }}>

        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

          <div style={{ border: "1px solid rgba(255,255,255,0.1)", padding: 24 }}>
            <p style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 20 }}>
              Order book depth
            </p>
            {chartData.length === 0 ? (
              <p style={{ fontSize: 12, color: "rgba(255,255,255,0.3)" }}>No orders yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                  <XAxis dataKey="price" tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: "rgba(255,255,255,0.3)" }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: "#10131a", border: "1px solid rgba(255,255,255,0.1)", fontFamily: "IBM Plex Mono", fontSize: 12 }}
                    labelStyle={{ color: "#e8e6e1" }}
                    itemStyle={{ color: "rgba(255,255,255,0.6)" }}
                  />
                  <Bar dataKey="amount" radius={[2, 2, 0, 0]}>
                    {chartData.map((entry, i) => (
                      <Cell key={i} fill={entry.type === "bid" ? "rgba(74,222,128,0.6)" : "rgba(248,113,113,0.6)"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div style={{ border: "1px solid rgba(255,255,255,0.1)", padding: 24 }}>
            <p style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 20 }}>
              Order book
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
              <div>
                <p style={{ fontSize: 11, color: "#4ade80", letterSpacing: "0.08em", marginBottom: 12 }}>BIDS</p>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "rgba(255,255,255,0.25)", marginBottom: 8 }}>
                  <span>PRICE</span><span>AMOUNT</span>
                </div>
                {orderbook?.bids.length === 0 && <p style={{ fontSize: 12, color: "rgba(255,255,255,0.3)" }}>No bids.</p>}
                {orderbook?.bids.map((b, i) => (
                  <div key={i} className="ob-row">
                    <span style={{ color: "#4ade80" }}>{parseFloat(b.price).toFixed(4)}</span>
                    <span style={{ color: "rgba(255,255,255,0.5)" }}>{parseFloat(b.remaining).toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <div>
                <p style={{ fontSize: 11, color: "#f87171", letterSpacing: "0.08em", marginBottom: 12 }}>ASKS</p>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "rgba(255,255,255,0.25)", marginBottom: 8 }}>
                  <span>PRICE</span><span>AMOUNT</span>
                </div>
                {orderbook?.asks.length === 0 && <p style={{ fontSize: 12, color: "rgba(255,255,255,0.3)" }}>No asks.</p>}
                {orderbook?.asks.map((a, i) => (
                  <div key={i} className="ob-row">
                    <span style={{ color: "#f87171" }}>{parseFloat(a.price).toFixed(4)}</span>
                    <span style={{ color: "rgba(255,255,255,0.5)" }}>{parseFloat(a.remaining).toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div style={{ border: "1px solid rgba(255,255,255,0.1)", padding: 24, alignSelf: "start" }}>
          <p style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 20 }}>
            Place order
          </p>

          {market.state !== "OPEN" ? (
            <p style={{ fontSize: 12, color: "rgba(255,255,255,0.4)" }}>Market is not open for trading.</p>
          ) : (
            <form onSubmit={handleOrder} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ display: "flex", gap: 8 }}>
                <button type="button" className={`tab ${side === "BUY" ? "active-buy" : ""}`} style={{ flex: 1 }} onClick={() => setSide("BUY")}>BUY</button>
                <button type="button" className={`tab ${side === "SELL" ? "active-sell" : ""}`} style={{ flex: 1 }} onClick={() => setSide("SELL")}>SELL</button>
              </div>

              <label>
                Outcome
                <select value={outcomeId ?? ""} onChange={e => setSelectedOutcome(e.target.value)}>
                  {market.outcomes.map(o => (
                    <option key={o.id} value={o.id}>{o.name}</option>
                  ))}
                </select>
              </label>

              <label>
                Price (0–1)
                <input type="number" min="0.01" max="0.99" step="0.01" placeholder="0.50" value={price} onChange={e => setPrice(e.target.value)} required />
              </label>

              <label>
                Amount
                <input type="number" min="1" step="1" placeholder="100" value={amount} onChange={e => setAmount(e.target.value)} required />
              </label>

              {price && amount && (
                <p style={{ fontSize: 11, color: "rgba(255,255,255,0.35)" }}>
                  Cost: {(parseFloat(price) * parseFloat(amount)).toFixed(2)} POLY
                </p>
              )}

              {orderError && (
                <p style={{ fontSize: 12, color: "#f87171", padding: "8px 12px", border: "1px solid rgba(248,113,113,0.2)" }}>
                  {orderError}
                </p>
              )}

              {orderSuccess && (
                <p style={{ fontSize: 12, color: "#4ade80", padding: "8px 12px", border: "1px solid rgba(74,222,128,0.2)" }}>
                  Order placed.
                </p>
              )}

              <button
                type="submit"
                disabled={orderMutation.isPending}
                style={{
                  padding: "12px",
                  background: side === "BUY" ? "rgba(74,222,128,0.15)" : "rgba(248,113,113,0.15)",
                  border: `1px solid ${side === "BUY" ? "rgba(74,222,128,0.4)" : "rgba(248,113,113,0.4)"}`,
                  color: side === "BUY" ? "#4ade80" : "#f87171",
                  fontFamily: "'IBM Plex Mono', monospace",
                  fontSize: 12,
                  letterSpacing: "0.08em",
                  cursor: orderMutation.isPending ? "not-allowed" : "pointer",
                  opacity: orderMutation.isPending ? 0.6 : 1,
                }}
              >
                {orderMutation.isPending ? "Placing..." : `Place ${side}`}
              </button>
            </form>
          )}
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