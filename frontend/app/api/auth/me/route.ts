import { cookies } from "next/headers"
import { NextResponse } from "next/server"

export async function GET() {
  const token = (await cookies()).get("access_token")?.value
  if (!token) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 })
  }

  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  })

  if (!res.ok) {
    return NextResponse.json({ error: "Unauthorized" }, { status: res.status })
  }

  return NextResponse.json(await res.json())
}
