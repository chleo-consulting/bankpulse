"use client"

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"

import { formatAmount } from "@/lib/format"
import type { CategoryBreakdownItem } from "@/types/api"

const CHART_COLORS = [
  "#6366F1",
  "#8B5CF6",
  "#EC4899",
  "#F59E0B",
  "#10B981",
  "#3B82F6",
  "#14B8A6",
  "#F97316",
]

const CATEGORY_ICONS: Record<string, string> = {
  Alimentation: "🍽️",
  Transport: "🚆",
  Logement: "🏠",
  "Loisirs & Culture": "📺",
  Sante: "💊",
  Shopping: "🛍️",
  "Services & Abonnements": "📱",
  Revenus: "💰",
  Supermarche: "🛒",
  Restaurant: "🍴",
  "Fast food": "🍔",
  Essence: "⛽",
  "Transports en commun": "🚇",
  "Taxi & VTC": "🚕",
  Loyer: "🏠",
  Charges: "⚡",
  "Sport & Fitness": "🏋️",
  "Streaming & Jeux": "📺",
  Cinema: "🎬",
  Medecin: "🏥",
  Pharmacie: "💊",
  Vetements: "👕",
  "High-tech": "💻",
  Telephonie: "📱",
  Assurances: "🛡️",
  "Banque & Frais": "🏦",
  Salaire: "💰",
  Remboursements: "🔄",
}

function getCategoryIcon(name: string): string {
  return CATEGORY_ICONS[name] ?? "📦"
}

type ChartItem = CategoryBreakdownItem & { color: string }

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{ payload: ChartItem }>
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null
  const item = payload[0].payload
  return (
    <div className="bg-white border border-gray-200 rounded-md px-3 py-2 shadow-sm text-sm">
      <p className="font-medium">{item.category_name}</p>
      <p className="text-gray-600 font-mono">{formatAmount(item.amount)}</p>
      <p className="text-gray-400">{item.percentage.toFixed(1)}%</p>
    </div>
  )
}

interface CategoryChartProps {
  items: CategoryBreakdownItem[]
}

export function CategoryChart({ items }: CategoryChartProps) {
  const data: ChartItem[] = items.map((item, idx) => ({
    ...item,
    color: CHART_COLORS[idx % CHART_COLORS.length],
  }))

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Donut Chart */}
      <div className="flex items-center justify-center">
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={95}
              dataKey="amount"
              strokeWidth={0}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Légende */}
      <div className="flex flex-col justify-center gap-3">
        {data.map((item) => (
          <div key={item.category_id} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full shrink-0"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm">
                {getCategoryIcon(item.category_name)} {item.category_name}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm font-mono font-semibold">{formatAmount(item.amount)}</span>
              <span className="text-sm text-gray-400 w-10 text-right">
                {item.percentage.toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
