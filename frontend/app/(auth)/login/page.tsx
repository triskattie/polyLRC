"use client"

import Link from "next/link"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { setTokens } from "@/lib/auth"

export default function LoginPage() {
  const router = useRouter()
  const [form, setForm] = useState({ email: "", password: "" })
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    setLoading(true)
    try {
      const res = await api.post("/auth/login", {
        email: form.email,
        password: form.password,
      })
      setTokens(res.data.access_token, res.data.refresh_token)
      router.push("/markets")
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Login failed.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ fontFamily: "'IBM Plex Mono', monospace" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Playfair+Display:ital,wght@0,400;1,400&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .button-full { background: #ffb300; color: #000000; }
        .button { display: inline-block; padding: 11px 24px; font-family: 'IBM Plex Mono', monospace; font-size: 14px; }
        input { width: 100%; padding: 10px 14px; font-family: 'IBM Plex Mono', monospace; font-size: 13px; background: transparent; border: 1px solid rgba(255,255,255,0.2); color: inherit; }
        input:focus { outline: none; border-color: #ffb300; }
        label { display: flex; flex-direction: column; gap: 8px; font-size: 11px; }
      `}</style>

      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        <Link href="/">PolyLRC</Link>
        <a href="https://triskattie.com">← triskattie.com</a>
      </nav>

      <section style={{ padding: "100px 48px", maxWidth: 480, margin: "0 auto" }}>
        <p style={{ fontSize: 13, marginBottom: 25 }}>CS FINAL PROJECT - PREDICTION MARKET</p>
        <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(32px, 5vw, 48px)", fontWeight: 400, lineHeight: 1.05, marginBottom: 25 }}>
          Login to <br /><em style={{ color: "#ffc800" }}>your account.</em>
        </h1>
        <p style={{ marginBottom: 40 }}>
          Don't have an account yet? <Link href="/register" style={{ color: "#ffb300" }}>Register</Link>
        </p>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
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
            className="button button-full"
            style={{ opacity: loading ? 0.6 : 1, cursor: loading ? "not-allowed" : "pointer", marginTop: 8 }}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </section>
    </main>
  )
}