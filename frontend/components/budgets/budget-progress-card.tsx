"use client"

import { MoreHorizontal } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Progress } from "@/components/ui/progress"
import { formatAmount } from "@/lib/format"
import type { BudgetProgressItem } from "@/types/api"

const PERIOD_LABELS: Record<string, string> = {
  monthly: "mensuel",
  quarterly: "trimestriel",
  yearly: "annuel",
}

interface BudgetProgressCardProps {
  item: BudgetProgressItem
  categoryIcon?: string | null
  daysRemaining: number
  onEdit: () => void
  onDelete: () => void
}

export function BudgetProgressCard({
  item,
  categoryIcon,
  daysRemaining,
  onEdit,
  onDelete,
}: BudgetProgressCardProps) {
  const pct = Math.min(item.pct, 100)
  const isOver = item.alert === "over_budget"
  const isNear = item.alert === "near_limit"
  const remaining = Number(item.limit) - Number(item.spent)

  const progressClass = isOver
    ? "[&>div]:bg-red-500"
    : isNear
      ? "[&>div]:bg-amber-500"
      : "[&>div]:bg-emerald-500"

  const badgeVariant: "destructive" | "secondary" | "default" = isOver
    ? "destructive"
    : isNear
      ? "secondary"
      : "default"

  return (
    <Card>
      <CardContent className="pt-6">
        {/* Header row */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{categoryIcon ?? "💰"}</span>
            <div>
              <h3 className="font-semibold">{item.category_name}</h3>
              <div className="text-sm text-gray-600 mt-0.5 font-mono">
                <span>{formatAmount(Number(item.spent))}</span>
                {" / "}
                <span>{formatAmount(Number(item.limit))}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Badge variant={badgeVariant}>{item.pct.toFixed(0)}%</Badge>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreHorizontal size={16} />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={onEdit}>✏️ Modifier</DropdownMenuItem>
                <DropdownMenuItem onClick={onDelete} className="text-red-600 focus:text-red-600">
                  🗑️ Supprimer
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Progress bar */}
        <Progress value={pct} className={`h-2 mb-3 ${progressClass}`} />

        {/* Metadata row */}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-gray-600">
          {isOver ? (
            <span className="text-red-600 font-medium">
              Dépassement : {formatAmount(Math.abs(remaining))}
            </span>
          ) : (
            <span>Reste : {formatAmount(remaining)}</span>
          )}
          <span className="text-gray-400">•</span>
          <span>{daysRemaining} jours restants</span>
          <span className="text-gray-400">•</span>
          <span className="capitalize">{PERIOD_LABELS[item.period_type] ?? item.period_type}</span>
          {isNear && !isOver && (
            <span className="text-amber-600 font-medium ml-1">⚠️ Attention</span>
          )}
          {isOver && <span className="text-red-600 font-medium ml-1">🔴 Budget dépassé</span>}
        </div>
      </CardContent>
    </Card>
  )
}
