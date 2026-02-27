import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export default function AccountsLoading() {
  return (
    <div className="space-y-6">
      {/* KPI Solde consolidé */}
      <Card>
        <CardContent className="pt-6">
          <Skeleton className="h-4 w-40 mb-2" />
          <Skeleton className="h-10 w-48 mb-2" />
          <Skeleton className="h-4 w-24" />
        </CardContent>
      </Card>

      {/* Boutons d'action */}
      <div className="flex gap-4">
        <Skeleton className="h-9 w-40 rounded-md" />
        <Skeleton className="h-9 w-52 rounded-md" />
      </div>

      {/* Liste des comptes */}
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <Skeleton className="h-10 w-10 rounded-full shrink-0" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-5 w-48" />
                    <Skeleton className="h-4 w-56" />
                    <Skeleton className="h-8 w-32" />
                    <Skeleton className="h-3 w-64" />
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Skeleton className="h-8 w-28 rounded-md" />
                  <Skeleton className="h-8 w-8 rounded-md" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
