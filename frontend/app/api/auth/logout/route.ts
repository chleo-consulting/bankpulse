import { type NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function POST(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value

  // Notifier le backend (best-effort — on continue même si ça échoue)
  if (token) {
    await fetch(`${API_URL}/api/v1/auth/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => null)
  }

  const response = NextResponse.json({ ok: true })
  response.cookies.delete("access_token")
  return response
}
