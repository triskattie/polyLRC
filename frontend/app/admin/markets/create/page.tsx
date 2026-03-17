"use client"
 
import Link from "next/link"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { useQuery } from "@tanstack/react-query"
import type { User } from "@/lib/types"
 
export default function CreateMarketPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    title: "",
    description: "",
    outcome_a: "",
    outcome_b: "",
  })
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
 
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await api.post("/markets", {
        title: form.title,
        description: form.description,
        outcomes: [
          { name: form.outcome_a },
          { name: form.outcome_b },
        ],
      })
      router.push(`/markets/${res.data.market_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Failed to create market.")
    } finally {
      setLoading(false)
    }
  }
  
  const { data: user } = useQuery<User>({
    queryKey: ["me"],
    queryFn: async () => (await api.get("/users/me")).data,
  })

  useEffect(() => {
  if (user && user.role !== "admin") {
    router.push("/markets")
  }
}, [user])

  return (
    <main style={{ fontFamily: "'IBM Plex Mono', monospace", background: "#0d0f14", color: "#e8e6e1", minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .button-full { background: #d4af37; color: #000000; }
        .button-outline { border: 1px solid rgba(255,255,255,0.3); color: #e8e6e1; }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.08em; }
        input, textarea { width: 100%; padding: 10px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 13px; background: transparent; border: 1px solid rgba(255,255,255,0.2); color: #e8e6e1; }
        input:focus, textarea:focus { outline: none; border-color: #d4af37; }
        label { display: flex; flex-direction: column; gap: 8px; font-size: 11px; color: rgba(255,255,255,0.4); letter-spacing: 0.08em; }
        textarea { resize: vertical; min-height: 80px; }
      `}</style>
 
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/dashboard" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
        <Link href="/markets" className="button button-full" style={{ fontSize: 11 }}>Markets</Link>
      </nav>
 
      <section style={{ padding: "100px 48px 80px", maxWidth: 1000, margin: "0 auto" }}>
        <p style={{ fontSize: 12, marginBottom: 25, color: "#d4af37", letterSpacing: "0.08em" }}>
          ADMIN — CREATE MARKET
        </p>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(40px, 7vw, 80px)", fontWeight: 400, lineHeight: 1.05, marginBottom: 25 }}>
          New <em style={{ color: "#d4af37" }}>market.</em>
        </h1>
        <p style={{ marginBottom: 48, maxWidth: 500, color: "rgba(255,255,255,0.4)", lineHeight: 2, fontSize: 13 }}>
          Market starts in PRE state. Seed liquidity before opening.
        </p>
 
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 600 }}>
          <label>
            Title
            <input
              type="text"
              value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              required
            />
          </label>
 
          <label>
            Description
            <textarea
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            />
          </label>
 
          <label>
            Outcome A
            <input
              type="text"
              placeholder="e.g. YES"
              value={form.outcome_a}
              onChange={e => setForm(f => ({ ...f, outcome_a: e.target.value }))}
              required
            />
          </label>
 
          <label>
            Outcome B
            <input
              type="text"
              placeholder="e.g. NO"
              value={form.outcome_b}
              onChange={e => setForm(f => ({ ...f, outcome_b: e.target.value }))}
              required
            />
          </label>
 
          {error && (
            <p style={{ fontSize: 12, color: "#f87171", padding: "10px 14px", border: "1px solid rgba(248,113,113,0.2)" }}>
              {error}
            </p>
          )}
 
          <div>
            <button
              type="submit"
              disabled={loading}
              className="button button-full"
              style={{ opacity: loading ? 0.6 : 1, cursor: loading ? "not-allowed" : "pointer" }}
            >
              {loading ? "Creating..." : "Create market"}
            </button>
          </div>
        </form>
      </section>
 
      <footer style={{ padding: "24px 48px", display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
        <span>PolyLRC - CS final project</span>
        <div style={{ display: "flex", gap: 20 }}>
          <a href="https://triskattie.com">triskattie.com</a>
          <Link href="/markets">Markets</Link>
        </div>
      </footer>
    </main>
  )
}
