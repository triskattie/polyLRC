"use client"

import Link from "next/link"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { setTokens } from "@/lib/auth"

export default function RegisterPage() {
  const router = useRouter()
  const [form, setForm] = useState({ email: "", password: "", confirm: "" })
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (form.password !== form.confirm) {
      setError("Passwords do not match.")
      return
    }

    setLoading(true)
    try {
      const res = await api.post("/auth/register", {
        email: form.email,
        password: form.password,
      })

      await setTokens(res.data.access_token, res.data.refresh_token)

      router.push("/markets")
    } catch (err: any) {
      const detail = err.response?.data?.detail

      if (Array.isArray(detail)) {
        setError(detail[0]?.msg)
      } else {
        setError(detail ?? "Registration failed.")
      }
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
          Create an <em className="accent">account.</em>
        </h1>
        <p className="auth-copy">
          Already have an account? <Link href="/login" className="accent">Sign in</Link>
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
              autoComplete="new-password"
              value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              required
            />
          </label>
          <label className="auth-label">
            Confirm password
            <input className="auth-input"
              type="password"
              autoComplete="new-password"
              value={form.confirm}
              onChange={e => setForm(f => ({ ...f, confirm: e.target.value }))}
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
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>
      </section>
    </main>
  )
}