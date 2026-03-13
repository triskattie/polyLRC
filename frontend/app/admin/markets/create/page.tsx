"use client"

import Link from "next/link"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"

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

  return (
    <main style={{ padding: 40, maxWidth: 600, margin: "0 auto" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        input, textarea { width: 100%; padding: 10px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 13px; background: transparent; border: 1px solid rgba(255,255,255,0.2); color: inherit; }
        input:focus, textarea:focus { outline: none; border-color: #ffb300; }
        label { display: flex; flex-direction: column; gap: 8px; font-size: 11px; }
        textarea { resize: vertical; min-height: 80px; }
      `}</style>

      <nav style={{ display: "flex", justifyContent: "space-between", marginBottom: 40 }}>
        <Link href="/">PolyLRC</Link>
        <Link href="/markets">← Markets</Link>
      </nav>

      <h1 style={{ marginBottom: 8 }}>Create market</h1>
      <p style={{ fontSize: 13, opacity: 0.5, marginBottom: 32 }}>Admin only. Market starts in PRE state.</p>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 20 }}>
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

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "11px 24px",
            background: "#ffb300",
            color: "#000",
            border: "none",
            fontFamily: "'IBM Plex Mono', monospace",
            fontSize: 14,
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.6 : 1,
            marginTop: 8,
          }}
        >
          {loading ? "Creating..." : "Create market"}
        </button>
      </form>
    </main>
  )
}