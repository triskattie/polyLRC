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


	return (
		<main style={{ fontFamily: "'IBM Plex Mono', monospace", background: "#0d0f14", minHeight: "100vh"}}>
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
					ADMIN - SEED MARKET
				</p>
				<h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: "clamp(40px, 7vw, 80px)", fontWeight: 400, lineHeight: 1.05, marginBottom: 25 }}>
					Seed <em style={{ color: "#d4af37" }}>market.</em>
				</h1>
				<p style={{ marginBottom: 48, maxWidth: 500, color: "rgba(255,255,255,0.4)", lineHeight: 2, fontSize: 13 }}>
					Market will stay PRE until market state is explicitly edited.
				</p>

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
			</section>
		</main>
	)
}