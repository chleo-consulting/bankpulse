import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export default function TransactionsLoading() {
  return (
    <div className="space-y-4">
      {/* Filtres */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between mb-3">
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-8 w-28 rounded-md" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-9 w-full rounded-md" />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-44" />
        <Skeleton className="h-9 w-32 rounded-md" />
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {/* Header */}
          <div className="px-4 py-3 border-b flex items-center gap-4">
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-40 flex-1" />
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-24" />
          </div>
          {/* Rows */}
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="px-4 py-3 border-b last:border-0 flex items-center gap-4">
              <Skeleton className="h-4 w-4 shrink-0" />
              <Skeleton className="h-4 w-16 shrink-0" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-24 shrink-0" />
              <Skeleton className="h-4 w-20 shrink-0 ml-auto" />
              <Skeleton className="h-8 w-28 shrink-0 rounded-md" />
            </div>
          ))}
          {/* Pagination */}
          <div className="flex items-center justify-center gap-2 py-4 border-t">
            <Skeleton className="h-8 w-24 rounded-md" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-8 w-24 rounded-md" />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
