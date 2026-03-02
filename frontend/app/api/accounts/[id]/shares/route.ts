import { cookies } from "next/headers"
import { NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value
  if (!token) return NextResponse.json({ message: "Non authentifié" }, { status: 401 })

  const upstream = await fetch(`${API_URL}/api/v1/accounts/${id}/shares`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return NextResponse.json(await upstream.json(), { status: upstream.status })
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value
  if (!token) return NextResponse.json({ message: "Non authentifié" }, { status: 401 })

  const body = await req.json()
  const upstream = await fetch(`${API_URL}/api/v1/accounts/${id}/invite`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  return NextResponse.json(await upstream.json(), { status: upstream.status })
}
