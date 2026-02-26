import { type NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

function getToken(req: NextRequest): string | null {
  return req.cookies.get("access_token")?.value ?? null
}

export async function GET(req: NextRequest) {
  const token = getToken(req)
  if (!token) return NextResponse.json({ message: "Non authentifié" }, { status: 401 })

  try {
    const upstream = await fetch(`${API_URL}/api/v1/accounts`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await upstream.json()
    return NextResponse.json(data, { status: upstream.status })
  } catch {
    return NextResponse.json({ message: "Erreur serveur" }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  const token = getToken(req)
  if (!token) return NextResponse.json({ message: "Non authentifié" }, { status: 401 })

  try {
    const body = await req.json()
    const upstream = await fetch(`${API_URL}/api/v1/accounts`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })
    const data = await upstream.json()
    return NextResponse.json(data, { status: upstream.status })
  } catch {
    return NextResponse.json({ message: "Erreur serveur" }, { status: 500 })
  }
}
