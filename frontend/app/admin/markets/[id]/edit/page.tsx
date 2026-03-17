"use client"

import { use, useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import type { Market } from "@/lib/types"
import Link from "next/link"

export default function EditMarketPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()

  const [form, setForm] = useState({
    title: "",
    description: "",
    state: "",
  })
  const [original, setOriginal] = useState({ title: "", description: "", state: "" })
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const { data: market, isLoading, isError } = useQuery<Market>({
    queryKey: ["market", id],
    queryFn: async () => (await api.get(`/markets/${id}`)).data,
  })

  useEffect(() => {
    if (market) {
      const initial = {
				title: market.title,
				description: market.description ?? "",
				state: market.state,
      }
      setForm(initial)
      setOriginal(initial)
    }
  }, [market])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const patch: Record<string, string> = {}
    if (form.title !== original.title) patch.title = form.title
    if (form.description !== original.description) patch.description = form.description
    if (form.state !== original.state) patch.state = form.state

    if (Object.keys(patch).length === 0) {
      setError("No changes to save.")
      setLoading(false)
      return
    }

    try {
      await api.patch(`/markets/${id}`, patch)
      setSuccess(true)
      setOriginal(form)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Failed to update market.")
    } finally {
      setLoading(false)
    }
  }

  if (isLoading) return <p style={{ padding: 40, fontFamily: "monospace" }}>Loading...</p>
  if (isError) return <p style={{ padding: 40, fontFamily: "monospace" }}>Market not found.</p>
  if (!market) return null

  return (
    <main style={{ fontFamily: "'IBM Plex Mono', monospace", background: "#0d0f14", color: "#e8e6e1", minHeight: "100vh" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .button-full { background: #d4af37; color: #000000; }
        .button-outline { border: 1px solid rgba(255,255,255,0.3); color: #e8e6e1; }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.08em; }
        a { text-decoration: none; color: inherit; }
        input, textarea, select { width: 100%; padding: 10px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 13px; background: transparent; border: 1px solid rgba(255,255,255,0.2); color: #e8e6e1; }
        input:focus, textarea:focus, select:focus { outline: none; border-color: #d4af37; }
        input.changed, textarea.changed, select.changed { border-color: rgba(212,175,55,0.5); }
        select option { background: #0d0f14; }
        label { display: flex; flex-direction: column; gap: 8px; font-size: 11px; color: rgba(255,255,255,0.4); letter-spacing: 0.08em; }
        textarea { resize: vertical; min-height: 80px; }
      `}</style>

      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/dashboard" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          <Link href={`/markets/${id}`} style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>← Market</Link>
          <Link href="/markets" style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>Markets</Link>
        </div>
      </nav>

      <section style={{ padding: "60px 48px", maxWidth: 800, margin: "0 auto" }}>
        <p style={{ fontSize: 12, marginBottom: 16, color: "#d4af37", letterSpacing: "0.08em" }}>ADMIN — EDIT MARKET</p>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 48 }}>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 400 }}>
            Edit <em style={{ color: "#d4af37" }}>market.</em>
          </h1>
          <Link href={`/markets/${id}`} className="button button-outline" style={{ fontSize: 11 }}>
            View market
          </Link>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 600 }}>
          <label>
            Title
            <input
              type="text"
              value={form.title}
              className={form.title !== original.title ? "changed" : ""}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
              required
            />
          </label>

          <label>
            Description
            <textarea
              value={form.description}
              className={form.description !== original.description ? "changed" : ""}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              required
            />
          </label>

          <label>
            State
            <select
              value={form.state}
              className={form.state !== original.state ? "changed" : ""}
              onChange={e => setForm(f => ({ ...f, state: e.target.value }))}
            >
              <option value="PRE">PRE</option>
              <option value="OPEN">OPEN</option>
              <option value="CLOSED">CLOSED</option>
              <option value="RESOLVED">RESOLVED</option>
            </select>
          </label>

          {Object.keys({
            ...(form.title !== original.title ? { title: true } : {}),
            ...(form.description !== original.description ? { description: true } : {}),
            ...(form.state !== original.state ? { state: true } : {}),
          }).length > 0 && (
            <p style={{ fontSize: 11, color: "rgba(212,175,55,0.6)" }}>
              Changed: {[
                form.title !== original.title && "title",
                form.description !== original.description && "description",
                form.state !== original.state && "state",
              ].filter(Boolean).join(", ")}
            </p>
          )}

          {error && (
            <p style={{ fontSize: 12, color: "#f87171", padding: "10px 14px", border: "1px solid rgba(248,113,113,0.2)" }}>
              {error}
            </p>
          )}

          {success && (
            <p style={{ fontSize: 12, color: "#4ade80", padding: "10px 14px", border: "1px solid rgba(74,222,128,0.2)" }}>
              Market updated.
            </p>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="button button-full"
              style={{ opacity: loading ? 0.6 : 1, cursor: loading ? "not-allowed" : "pointer" }}
            >
              {loading ? "Saving..." : "Save changes"}
            </button>
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
          <Link href="/markets">Markets</Link>
        </div>
      </footer>
    </main>
  )
}