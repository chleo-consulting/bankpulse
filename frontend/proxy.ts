import { type NextRequest, NextResponse } from "next/server"

const PUBLIC_PATHS = ["/login", "/register"]
const IGNORED_PREFIXES = ["/api", "/_next", "/favicon.ico"]

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Ignorer les assets et les routes API internes
  if (IGNORED_PREFIXES.some((prefix) => pathname.startsWith(prefix))) {
    return NextResponse.next()
  }

  const token = request.cookies.get("access_token")?.value
  const isPublicPath = PUBLIC_PATHS.some((p) => pathname.startsWith(p))

  // Pas de token + route protégée → /login
  if (!token && !isPublicPath) {
    const loginUrl = new URL("/login", request.url)
    return NextResponse.redirect(loginUrl)
  }

  // Token présent + page auth → /dashboard
  if (token && isPublicPath) {
    const dashboardUrl = new URL("/dashboard", request.url)
    return NextResponse.redirect(dashboardUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}
