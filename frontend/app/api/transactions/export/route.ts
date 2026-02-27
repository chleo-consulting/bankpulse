import { type NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function GET(req: NextRequest) {
  const token = req.cookies.get("access_token")?.value
  if (!token) return NextResponse.json({ message: "Non authentifié" }, { status: 401 })

  const { searchParams } = new URL(req.url)
  searchParams.set("format", "csv")
  const params = searchParams.toString()

  try {
    const upstream = await fetch(
      `${API_URL}/api/v1/transactions/export${params ? `?${params}` : ""}`,
      { headers: { Authorization: `Bearer ${token}` } },
    )

    const csvText = await upstream.text()
    return new NextResponse(csvText, {
      status: upstream.status,
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": "attachment; filename=transactions.csv",
      },
    })
  } catch {
    return NextResponse.json({ message: "Erreur serveur" }, { status: 500 })
  }
}
