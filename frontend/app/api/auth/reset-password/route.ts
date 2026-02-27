import { type NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const upstream = await fetch(`${API_URL}/api/v1/auth/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })

    const data = await upstream.json().catch(() => ({}))

    if (!upstream.ok) {
      const message =
        typeof data.detail === "string" ? data.detail : "Token invalide ou expiré."
      return NextResponse.json({ message }, { status: upstream.status })
    }

    return NextResponse.json({ ok: true })
  } catch {
    return NextResponse.json({ message: "Erreur serveur" }, { status: 500 })
  }
}
