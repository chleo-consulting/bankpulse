import { NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

// Endpoint public — pas de cookie requis (le backend n'exige pas d'auth)
export async function POST(req: NextRequest) {
  const { token } = await req.json()
  const upstream = await fetch(`${API_URL}/api/v1/invitations/accept/${token}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
  return NextResponse.json(await upstream.json().catch(() => ({})), { status: upstream.status })
}
