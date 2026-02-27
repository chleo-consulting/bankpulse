import { cookies } from "next/headers"
import { List } from "lucide-react"

import { EmptyState } from "@/components/shared/empty-state"
import { TransactionsList } from "@/components/transactions/transactions-list"
import type {
  BankAccountResponse,
  CategoryWithChildrenResponse,
  CursorTransactionListResponse,
  TagResponse,
} from "@/types/api"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function fetchJSON<T>(path: string, token: string): Promise<T | null> {
  try {
    const res = await fetch(`${API_URL}${path}`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    })
    if (!res.ok) return null
    return res.json() as Promise<T>
  } catch {
    return null
  }
}

export default async function TransactionsPage() {
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value ?? ""

  const [txnsData, categories, accounts, tags] = await Promise.all([
    fetchJSON<CursorTransactionListResponse>("/api/v1/transactions?page_size=50", token),
    fetchJSON<CategoryWithChildrenResponse[]>("/api/v1/categories", token),
    fetchJSON<BankAccountResponse[]>("/api/v1/accounts", token),
    fetchJSON<TagResponse[]>("/api/v1/tags", token),
  ])

  if (!txnsData) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Transactions</h1>
        <EmptyState
          icon={<List size={64} />}
          title="Aucune transaction"
          description="Importez un fichier CSV depuis Mes Comptes pour voir vos transactions."
          action={{ label: "Mes Comptes", href: "/accounts" }}
        />
      </div>
    )
  }

  return (
    <TransactionsList
      initialTransactions={txnsData}
      categories={categories ?? []}
      accounts={accounts ?? []}
      tags={tags ?? []}
    />
  )
}
