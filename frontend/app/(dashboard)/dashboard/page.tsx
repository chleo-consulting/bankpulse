import { cookies } from "next/headers"
import Link from "next/link"
import { BarChart3, RefreshCw, TrendingDown, Wallet } from "lucide-react"

import { CategoryChart } from "@/components/dashboard/category-chart"
import { EmptyState } from "@/components/shared/empty-state"
import { KPICard } from "@/components/shared/kpi-card"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatAmount, formatDate } from "@/lib/format"
import type {
  CategoriesBreakdown,
  DashboardSummary,
  RecurringSubscriptions,
  TopMerchants,
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

function formatDelta(delta: number): string {
  const abs = Math.abs(delta).toFixed(1)
  return delta >= 0 ? `+${abs}%` : `-${abs}%`
}

function frequencyLabel(freq: string): string {
  if (freq === "monthly") return "/ mois"
  if (freq === "yearly") return "/ an"
  return freq
}

export default async function DashboardPage() {
  const cookieStore = await cookies()
  const token = cookieStore.get("access_token")?.value ?? ""

  const [summary, breakdown, merchants, recurring] = await Promise.all([
    fetchJSON<DashboardSummary>("/api/v1/dashboard/summary", token),
    fetchJSON<CategoriesBreakdown>("/api/v1/dashboard/categories-breakdown", token),
    fetchJSON<TopMerchants>("/api/v1/dashboard/top-merchants", token),
    fetchJSON<RecurringSubscriptions>("/api/v1/dashboard/recurring", token),
  ])

  const currentMonth = new Date().toLocaleString("fr-FR", { month: "long", year: "numeric" })

  if (!summary) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
        <EmptyState
          icon={<BarChart3 size={64} />}
          title="Aucune donnée disponible"
          description="Importez votre premier fichier CSV pour voir votre dashboard."
          action={{ label: "Importer un fichier CSV", href: "/accounts" }}
        />
      </div>
    )
  }

  const expenseDelta = summary.expenses.delta_pct
  const deltaType = expenseDelta > 0 ? "negative" : expenseDelta < 0 ? "positive" : "neutral"

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <KPICard
          title="Solde Total"
          value={formatAmount(summary.total_balance)}
          icon={<Wallet size={20} />}
        />
        <KPICard
          title="Dépenses ce mois"
          value={formatAmount(Math.abs(summary.expenses.current))}
          delta={formatDelta(expenseDelta)}
          deltaType={deltaType}
          subtitle="vs mois dernier"
          icon={<TrendingDown size={20} />}
        />
      </div>

      {/* Breakdown Catégories */}
      <Card className="mb-6">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Dépenses par Catégorie</CardTitle>
          <span className="text-sm text-gray-500 capitalize">{currentMonth}</span>
        </CardHeader>
        <CardContent>
          {breakdown && breakdown.items.length > 0 ? (
            <CategoryChart items={breakdown.items.slice(0, 8)} />
          ) : (
            <p className="text-sm text-gray-500 py-8 text-center">
              Aucune dépense catégorisée ce mois.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Top Marchands + Abonnements */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Marchands */}
        <Card>
          <CardHeader>
            <CardTitle>Top Marchands ({merchants?.items?.length ?? 0})</CardTitle>
          </CardHeader>
          <CardContent>
            {merchants && merchants.items.length > 0 ? (
              <>
                <div className="space-y-3">
                  {merchants.items.map((merchant, idx) => (
                    <div key={merchant.merchant_id} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-400 w-5 shrink-0">{idx + 1}.</span>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {merchant.merchant_name}
                          </p>
                          <p className="text-xs text-gray-400">
                            {merchant.transaction_count} transaction
                            {merchant.transaction_count > 1 ? "s" : ""}
                          </p>
                        </div>
                      </div>
                      <span className="text-sm font-mono font-semibold text-red-500">
                        -{formatAmount(Math.abs(merchant.amount))}
                      </span>
                    </div>
                  ))}
                </div>
                <Link
                  href="/transactions"
                  className="text-sm text-indigo-500 hover:underline mt-4 inline-block"
                >
                  Voir tout →
                </Link>
              </>
            ) : (
              <p className="text-sm text-gray-500 py-8 text-center">Aucun marchand ce mois.</p>
            )}
          </CardContent>
        </Card>

        {/* Abonnements Récurrents */}
        <Card>
          <CardHeader>
            <CardTitle>Abonnements Détectés ({recurring?.items?.length ?? 0})</CardTitle>
          </CardHeader>
          <CardContent>
            {recurring && recurring.items.length > 0 ? (
              <div className="space-y-4">
                {recurring.items.map((sub) => (
                  <div key={sub.recurring_rule_id} className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{sub.merchant_name}</p>
                      {sub.next_expected && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          Prochain : {formatDate(sub.next_expected)}
                        </p>
                      )}
                    </div>
                    <div className="text-right shrink-0 ml-4">
                      {sub.expected_amount != null && (
                        <p className="text-sm font-mono font-semibold text-gray-900">
                          {formatAmount(sub.expected_amount)} {frequencyLabel(sub.frequency)}
                        </p>
                      )}
                      <Badge variant="secondary" className="text-xs mt-1">
                        {sub.frequency === "monthly" ? "mensuel" : "annuel"}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center">
                <RefreshCw size={32} className="mx-auto text-gray-300 mb-3" />
                <p className="text-sm text-gray-500">Aucun abonnement détecté.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
