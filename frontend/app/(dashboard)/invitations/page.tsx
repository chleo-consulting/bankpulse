import { cookies } from "next/headers"

import { InvitationsList } from "@/components/invitations/invitations-list"
import type { ReceivedInvitationResponse } from "@/types/api"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export default async function InvitationsPage() {
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value ?? ""

  let invitations: ReceivedInvitationResponse[] = []

  try {
    const res = await fetch(`${API_URL}/api/v1/invitations`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    })
    if (res.ok) {
      invitations = await res.json()
    }
  } catch {
    // silently ignore — empty state will be shown
  }

  return <InvitationsList initialInvitations={invitations} />
}
