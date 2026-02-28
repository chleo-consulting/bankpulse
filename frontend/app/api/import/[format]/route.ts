import { type NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ format: string }> },
) {
  const { format } = await params
  const token = req.cookies.get("access_token")?.value
  if (!token) return NextResponse.json({ message: "Non authentifié" }, { status: 401 })

  try {
    const formData = await req.formData()
    const upstream = await fetch(`${API_URL}/api/v1/import/${format}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    })
    const data = await upstream.json()
    return NextResponse.json(data, { status: upstream.status })
  } catch {
    return NextResponse.json({ message: "Erreur serveur" }, { status: 500 })
  }
}
