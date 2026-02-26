import { type NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const upstream = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })

    if (!upstream.ok) {
      const data = await upstream.json().catch(() => ({}))
      const message =
        typeof data.detail === "string"
          ? data.detail
          : "Identifiants incorrects"
      return NextResponse.json({ message }, { status: upstream.status })
    }

    const tokens = await upstream.json()

    const response = NextResponse.json({ ok: true })
    response.cookies.set("access_token", tokens.access_token, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      // En production, activer secure: true
      // secure: process.env.NODE_ENV === "production",
    })

    return response
  } catch {
    return NextResponse.json({ message: "Erreur serveur" }, { status: 500 })
  }
}
