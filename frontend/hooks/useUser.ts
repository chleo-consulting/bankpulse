"use client"

import { useEffect, useState } from "react"

interface User {
  id: string
  email: string
  first_name: string | null
  last_name: string | null
}

export function useUser() {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    fetch("/api/auth/me")
      .then((r) => (r.ok ? r.json() : null))
      .then(setUser)
      .catch(() => setUser(null))
  }, [])

  return { user }
}
