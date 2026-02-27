import { type NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

function getToken(req: NextRequest): string | null {
  return req.cookies.get("access_token")?.value ?? null
}

export async function GET(req: NextRequest) {
  const token = getToken(req)
  if (!token) return NextResponse.json({ message: "Non authentifié" }, { status: 401 })

  const { searchParams } = new URL(req.url)
  const params = searchParams.toString()

  try {
    const upstream = await fetch(
      `${API_URL}/api/v1/transactions${params ? `?${params}` : ""}`,
      { headers: { Authorization: `Bearer ${token}` } },
    )
    const data = await upstream.json()
    return NextResponse.json(data, { status: upstream.status })
  } catch {
    return NextResponse.json({ message: "Erreur serveur" }, { status: 500 })
  }
}
