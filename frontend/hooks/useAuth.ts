"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

export function useAuth() {
  const router = useRouter()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  async function logout() {
    setIsLoggingOut(true)
    try {
      await fetch("/api/auth/logout", { method: "POST" })
    } finally {
      router.push("/login")
      router.refresh()
      setIsLoggingOut(false)
    }
  }

  return { logout, isLoggingOut }
}
