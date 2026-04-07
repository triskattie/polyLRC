"use client"

import { use, useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { Market, User } from "@/lib/types"
import { useRouter } from "next/navigation"
import Link from "next/link"

export default function SeedMarketPage({ params }: { params: Promise<{ id: string }> }) {
	const { id } = use(params)
	const router = useRouter()

	const [form, setForm] = useState({
		amount: ""
	})
	const [error, setError] = useState<string | null>(null)
	const [loading, setLoading] = useState(false)

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setError(null)
		setLoading(true)
		try {
			const res = await api.post(`/markets/${id}/seed`, {
				amount: form.amount
			})
		} catch (err: any) {
			setError(err.response?.data?.detail ?? "Failed to seed market.")
		} finally {
			setLoading(false)
		}
	}

	const { data: market, isLoading, isError } = useQuery<Market>({
		queryKey: ["market", id],
		queryFn: async () => (await api.get(`/markets/${id}`)).data,
	})
	const { data: user } = useQuery<User>({
		queryKey: ["me"],
		queryFn: async () => (await api.get("/users/me")).data,
	})

	useEffect(() => {
		if (user && user.role !== "admin") {
			router.push("/markets")
		}
	}, [user])
	if (isLoading) return <p style={{ padding: 40, fontFamily: "monospace" }}>Loading...</p>
	if (isError) return <p style={{ padding: 40, fontFamily: "monospace" }}>Market not found.</p>
	if (!market) return null

	return (
		<main className="app-shell">

			<nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "22px 48px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
				<Link href="/dashboard" style={{ color: "#d4af37", fontSize: 13, fontWeight: 500, letterSpacing: "0.08em" }}>POLYLRC</Link>
				<div style={{ display: "flex", gap: 24, alignItems: "center" }}>
					<Link href={`/markets/${id}`} style={{ color: "rgba(255, 255, 255, 0.4", fontSize: 12 }}>← Market</Link>
					<Link href="/markets" className="button button-full" style={{ fontSize: 11 }}>Markets</Link>
				</div>
			</nav>

      <section style={{ padding: "60px 48px", maxWidth: 800, margin: "0 auto" }}>
        <p style={{ fontSize: 12, marginBottom: 16, color: "#d4af37", letterSpacing: "0.08em" }}>ADMIN — SEED MARKET</p>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 48 }}>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 400 }}>
            Seed <em style={{ color: "#d4af37" }}>market.</em>
          </h1>
          <Link href={`/markets/${id}`} className="button button-outline" style={{ fontSize: 11 }}>
            View market
          </Link>
        </div>

				<form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 600 }}>
					<label>
						Amount
						<input
							type="number"
							value={form.amount}
							onChange={e => setForm(f => ({ ...f, amount: e.target.value }))}
							required
						/>
					</label>

					{error && (
						<p>
							{error}
						</p>
					)}

					<div>
						<button
							type="submit"
							disabled={loading}
							className="button button-full"
						>
							{loading ? "Seeding..." : "Seed market"}
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
					<Link href="/feedback">Feedback</Link>
					<Link href="/docs">Docs</Link>
					<Link href="/markets">Markets</Link>
				</div>
			</footer>
		</main>
	)
}