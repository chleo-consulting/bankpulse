"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { CheckCircle2, Loader2, XCircle } from "lucide-react"

import { Button } from "@/components/ui/button"

type PageState = "loading" | "success" | "error"

export default function AcceptInvitationPage() {
  const { token } = useParams<{ token: string }>()
  const [state, setState] = useState<PageState>("loading")
  const [message, setMessage] = useState("")

  useEffect(() => {
    if (!token) {
      setState("error")
      setMessage("Token manquant.")
      return
    }

    async function accept() {
      try {
        const res = await fetch("/api/invitations/accept-by-token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        })
        const data = await res.json().catch(() => ({}))
        if (res.ok) {
          setState("success")
          setMessage(data.message ?? "Invitation acceptée avec succès.")
        } else {
          setState("error")
          setMessage(data.detail ?? data.message ?? "Lien invalide ou expiré.")
        }
      } catch {
        setState("error")
        setMessage("Erreur réseau. Veuillez réessayer.")
      }
    }

    accept()
  }, [token])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-xl border border-gray-200 shadow-sm p-8 text-center space-y-4">
        {/* Logo */}
        <div className="mb-6">
          <span className="text-2xl font-bold text-gray-900">BankPulse</span>
        </div>

        {state === "loading" && (
          <>
            <Loader2 className="mx-auto size-12 text-indigo-600 animate-spin" />
            <p className="text-sm text-gray-500">Acceptation de l'invitation en cours…</p>
          </>
        )}

        {state === "success" && (
          <>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">Invitation acceptée</h1>
            <p className="text-sm text-gray-500">{message}</p>
            <Button asChild className="w-full">
              <Link href="/accounts">Voir mes comptes</Link>
            </Button>
          </>
        )}

        {state === "error" && (
          <>
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">Lien invalide</h1>
            <p className="text-sm text-gray-500">{message}</p>
            <Button asChild variant="outline" className="w-full">
              <Link href="/login">Se connecter</Link>
            </Button>
          </>
        )}
      </div>
    </div>
  )
}
