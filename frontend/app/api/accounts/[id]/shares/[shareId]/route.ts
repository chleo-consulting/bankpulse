import { cookies } from "next/headers"
import { NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function DELETE(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string; shareId: string }> },
) {
  const { id, shareId } = await params
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value
  if (!token) return NextResponse.json({ message: "Non authentifié" }, { status: 401 })

  const upstream = await fetch(`${API_URL}/api/v1/accounts/${id}/shares/${shareId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  })
  if (upstream.status === 204) return new NextResponse(null, { status: 204 })
  return NextResponse.json(await upstream.json().catch(() => ({})), { status: upstream.status })
}
