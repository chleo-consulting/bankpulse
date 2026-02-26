import { cn } from "@/lib/utils"
import { Card, CardContent } from "@/components/ui/card"

interface KPICardProps {
  title: string
  value: string
  delta?: string
  deltaType?: "positive" | "negative" | "neutral"
  subtitle?: string
  icon?: React.ReactNode
}

export function KPICard({ title, value, delta, deltaType, subtitle, icon }: KPICardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-500">{title}</span>
          {icon && <div className="text-gray-400">{icon}</div>}
        </div>
        <div className="text-3xl font-bold font-mono text-gray-900">{value}</div>
        {delta && (
          <div
            className={cn(
              "text-sm mt-1",
              deltaType === "positive" && "text-emerald-500",
              deltaType === "negative" && "text-red-500",
              deltaType === "neutral" && "text-gray-500",
            )}
          >
            {delta} {subtitle}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
