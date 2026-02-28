import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export default function ImportLoading() {
  return (
    <div className="max-w-3xl space-y-6">
      {/* Step indicator skeleton */}
      <div className="flex items-center gap-1">
        {[0, 1, 2].map((i) => (
          <div key={i} className="flex items-center gap-1">
            <Skeleton className="h-7 w-7 rounded-full" />
            <Skeleton className="h-4 w-14" />
            {i < 2 && <Skeleton className="mx-2 h-px w-8" />}
          </div>
        ))}
      </div>

      {/* Format grid skeleton (étape 1) */}
      <div className="space-y-4">
        <div className="space-y-1">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-3 w-64" />
        </div>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
          {[0, 1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="py-4 text-center">
                <Skeleton className="mx-auto mb-3 h-12 w-12 rounded-xl" />
                <Skeleton className="mx-auto h-4 w-24" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
