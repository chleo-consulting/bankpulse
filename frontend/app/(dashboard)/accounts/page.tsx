import { cookies } from "next/headers"

import { AccountsList } from "@/components/accounts/accounts-list"
import type { BankAccountResponse } from "@/types/api"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export default async function AccountsPage() {
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value ?? ""

  let accounts: BankAccountResponse[] = []

  try {
    const res = await fetch(`${API_URL}/api/v1/accounts`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    })
    if (res.ok) {
      accounts = await res.json()
    }
  } catch {
    // silently ignore — empty state will be shown
  }

  return <AccountsList initialAccounts={accounts} />
}
