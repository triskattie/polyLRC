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
    <main className="auth-shell">
      <nav className="auth-nav">
        <Link href="/" className="site-brand">POLYLRC</Link>
        <a href="https://triskattie.com" className="site-nav-link">← triskattie.com</a>
      </nav>

      <section className="auth-panel">
        <p className="auth-eyebrow">CS FINAL PROJECT - PREDICTION MARKET</p>
        <h1 className="auth-title">
          Login to <br /><em className="accent">your account.</em>
        </h1>
        <p className="auth-copy">
          Don't have an account yet? <Link href="/register" className="accent">Register</Link>
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
          <label className="auth-label">
            Email
            <input className="auth-input"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              required
            />
          </label>
          <label className="auth-label">
            Password
            <input className="auth-input"
              type="password"
              autoComplete="current-password"
              value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              required
            />
          </label>

          {error && (
            <p className="auth-error">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="button button-full auth-submit"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </section>
    </main>
  )
}