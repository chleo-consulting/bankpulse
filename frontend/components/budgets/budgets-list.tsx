"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, ChevronRight, Plus, PiggyBank } from "lucide-react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { BudgetModal } from "@/components/budgets/budget-modal"
import { BudgetProgressCard } from "@/components/budgets/budget-progress-card"
import { formatAmount } from "@/lib/format"
import type { BudgetProgressItem, BudgetsProgress, CategoryWithChildrenResponse } from "@/types/api"

// ─── helpers ──────────────────────────────────────────────────────────────────

function getCurrentMonth(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
}

function offsetMonth(ym: string, delta: number): string {
  const [y, m] = ym.split("-").map(Number)
  const d = new Date(y, m - 1 + delta, 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
}

function formatMonthLabel(ym: string): string {
  const [y, m] = ym.split("-").map(Number)
  return new Date(y, m - 1, 1).toLocaleDateString("fr-FR", { month: "long", year: "numeric" })
}

/** Days remaining until end of period for the given month */
function getDaysRemaining(ym: string, periodType: string): number {
  const [y, m] = ym.split("-").map(Number)
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  let endDate: Date
  if (periodType === "yearly") {
    endDate = new Date(y, 11, 31)
  } else if (periodType === "quarterly") {
    const endQuarterMonth = Math.ceil(m / 3) * 3
    endDate = new Date(y, endQuarterMonth, 0) // last day of quarter
  } else {
    endDate = new Date(y, m, 0) // last day of month
  }

  return Math.max(0, Math.floor((endDate.getTime() - today.getTime()) / 86_400_000))
}

// ─── component ────────────────────────────────────────────────────────────────

interface BudgetsListProps {
  initialProgress: BudgetsProgress
  categories: CategoryWithChildrenResponse[]
  currentMonth: string | null
}

export function BudgetsList({ initialProgress, categories, currentMonth }: BudgetsListProps) {
  const router = useRouter()
  const activeMonth = currentMonth ?? getCurrentMonth()

  const [progress, setProgress] = useState<BudgetsProgress>(initialProgress)
  const [modalOpen, setModalOpen] = useState(false)
  const [editItem, setEditItem] = useState<BudgetProgressItem | null>(null)

  // category_id → icon lookup
  const iconMap = new Map<string, string | null>()
  for (const cat of categories) {
    iconMap.set(cat.id, cat.icon)
    for (const child of cat.children) {
      iconMap.set(child.id, cat.icon)
    }
  }

  const items = progress.items
  const totalBudget = items.reduce((s, i) => s + Number(i.limit), 0)
  const totalSpent = items.reduce((s, i) => s + Number(i.spent), 0)
  const globalPct = totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0

  // ── navigation ──────────────────────────────────────────────────────────────

  function navigateMonth(delta: number) {
    router.push(`/budgets?month=${offsetMonth(activeMonth, delta)}`)
  }

  // ── mutations ───────────────────────────────────────────────────────────────

  async function refreshProgress() {
    try {
      const url = `/api/budgets/progress?month=${activeMonth}`
      const res = await fetch(url)
      if (res.ok) setProgress(await res.json())
    } catch {
      // ignore — data will refresh on next navigation
    }
  }

  function handleCreate() {
    setEditItem(null)
    setModalOpen(true)
  }

  function handleEdit(item: BudgetProgressItem) {
    setEditItem(item)
    setModalOpen(true)
  }

  async function handleDelete(item: BudgetProgressItem) {
    if (!confirm(`Supprimer le budget "${item.category_name}" ?`)) return

    try {
      const res = await fetch(`/api/budgets/${item.budget_id}`, { method: "DELETE" })
      if (res.ok || res.status === 204) {
        toast.success("Budget supprimé")
        setProgress((prev) => ({
          ...prev,
          items: prev.items.filter((i) => i.budget_id !== item.budget_id),
        }))
      } else {
        toast.error("Erreur lors de la suppression")
      }
    } catch {
      toast.error("Erreur serveur")
    }
  }

  // ── render ──────────────────────────────────────────────────────────────────

  const prevMonth = offsetMonth(activeMonth, -1)
  const nextMonth = offsetMonth(activeMonth, 1)

  return (
    <div className="space-y-6 p-6">
      {/* ── Header ── */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">Vue mensuelle :</span>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => navigateMonth(-1)}>
              <ChevronLeft size={14} />
              <span className="capitalize">{formatMonthLabel(prevMonth)}</span>
            </Button>
            <span className="font-semibold capitalize px-1">{formatMonthLabel(activeMonth)}</span>
            <Button variant="outline" size="sm" onClick={() => navigateMonth(1)}>
              <span className="capitalize">{formatMonthLabel(nextMonth)}</span>
              <ChevronRight size={14} />
            </Button>
          </div>
        </div>

        <Button onClick={handleCreate}>
          <Plus size={16} className="mr-2" />
          Nouveau budget
        </Button>
      </div>

      {/* ── KPI cards ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500">Budget Total</div>
            <div className="text-3xl font-bold font-mono mt-2">{formatAmount(totalBudget)}</div>
            <div className="text-sm text-gray-500 mt-1">
              {items.length} catégorie{items.length !== 1 ? "s" : ""}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-sm text-gray-500">Dépensé</div>
            <div className="text-3xl font-bold font-mono mt-2">{formatAmount(totalSpent)}</div>
            <div className="flex items-center gap-2 mt-1">
              <Badge
                variant={
                  globalPct >= 100 ? "destructive" : globalPct >= 75 ? "secondary" : "default"
                }
              >
                {globalPct.toFixed(0)}%
              </Badge>
              <span className="text-sm text-gray-500">
                Reste : {formatAmount(totalBudget - totalSpent)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ── Budget list / empty state ── */}
      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 px-4">
          <PiggyBank size={48} className="text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun budget défini</h3>
          <p className="text-sm text-gray-500 mb-6 text-center max-w-sm">
            Créez votre premier budget pour suivre vos dépenses par catégorie.
          </p>
          <Button onClick={handleCreate}>
            <Plus size={16} className="mr-2" />
            Créer un budget
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <BudgetProgressCard
              key={item.budget_id}
              item={item}
              categoryIcon={iconMap.get(item.category_id)}
              daysRemaining={getDaysRemaining(activeMonth, item.period_type)}
              onEdit={() => handleEdit(item)}
              onDelete={() => handleDelete(item)}
            />
          ))}
        </div>
      )}

      {/* ── Modal ── */}
      <BudgetModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        onSuccess={refreshProgress}
        categories={categories}
        editItem={editItem}
      />
    </div>
  )
}
