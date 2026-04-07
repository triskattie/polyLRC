"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import type { User } from "@/lib/types"
import Link from "next/link"

export default function GiveFeedbackPage() {
  const [form, setForm] = useState({
    type: "",
    description: "",
    page: "",
  })
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const { data: user } = useQuery<User>({
    queryKey: ["me"],
    queryFn: async () => (await api.get("/users/me")).data,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(false)

    if (!form.description.trim()) {
      setError("Please enter your feedback.")
      return
    }

    const webhookUrl = process.env.NEXT_PUBLIC_DISCORD_WEBHOOK_URL
    if (!webhookUrl) {
      setError("Webhook URL not configured.")
      return
    }

    setLoading(true)
    try {
      const res = await fetch(webhookUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: `**New Feedback**\nUser ID: ${user?.user_id}\nEmail: ${user?.email}\nType: ${form.type}\nPage: ${form.page}\nFeedback: ${form.description}`,
        }),
      })

      if (!res.ok) throw new Error("Failed to send feedback")

      setForm({ type: "", description: "", page: "" })
      setSuccess(true)
      setTimeout(() => setSuccess(false), 4000)
    } catch {
      setError("Failed to send feedback. Try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/dashboard" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
      </nav>

      <section style={{ padding: "60px 48px", maxWidth: 800, margin: "0 auto" }}>
        <p style={{ fontSize: 12, marginBottom: 16, color: "#d4af37", letterSpacing: "0.08em" }}>USER — GIVE FEEDBACK</p>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 48 }}>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 400 }}>
            Submit <em style={{ color: "#d4af37" }}>feedback.</em>
          </h1>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 600 }}>
          <label>
            Type
            <select
              value={form.type}
              onChange={e => setForm(f => ({ ...f, type: e.target.value }))}
            >
              <option value="">Select a type</option>
              <option value="BUG">Bug report</option>
              <option value="FEAT-REQ">Feature request</option>
              <option value="UI-FEED">User interface / User experience feedback</option>
              <option value="PERF-FEED">Performance feedback</option>
              <option value="CONT-FEED">Content feedback</option>
              <option value="GEN-FEED">General feedback</option>
              <option value="ACCES-FEED">Accessibility feedback</option>
            </select>
          </label>

          <label>
            Description
            <textarea
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            />
          </label>

          <label>
            Page
            <input
              value={form.page}
              onChange={e => setForm(f => ({ ...f, page: e.target.value }))}
            />
          </label>

          {error && <p className="form-error">{error}</p>}
          {success && <p className="form-success">Thanks for your feedback!</p>}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="button button-full"
              style={{ opacity: loading ? 0.6 : 1, cursor: loading ? "not-allowed" : "pointer" }}
            >
              {loading ? "Submitting..." : "Submit feedback"}
            </button>
          </div>
        </form>
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