import { type NextRequest, NextResponse } from "next/server"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Étape 1 : créer le compte
    const registerRes = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })

    if (!registerRes.ok) {
      const data = await registerRes.json().catch(() => ({}))
      const message =
        typeof data.detail === "string"
          ? data.detail
          : Array.isArray(data.detail)
            ? data.detail.map((e: { msg: string }) => e.msg).join(", ")
            : "Erreur lors de la création du compte"
      return NextResponse.json({ message }, { status: registerRes.status })
    }

    // Étape 2 : auto-login pour récupérer le token
    const loginRes = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: body.email, password: body.password }),
    })

    if (!loginRes.ok) {
      // Le compte est créé mais la connexion auto a échoué → rediriger vers /login
      return NextResponse.json({ ok: true, redirect: "/login" }, { status: 200 })
    }

    const tokens = await loginRes.json()

    const response = NextResponse.json({ ok: true })
    response.cookies.set("access_token", tokens.access_token, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
    })

    return response
  } catch {
    return NextResponse.json({ message: "Erreur serveur" }, { status: 500 })
  }
}
