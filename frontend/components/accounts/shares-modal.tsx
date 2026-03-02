"use client"

import { useEffect, useState } from "react"
import { Trash2 } from "lucide-react"
import { toast } from "sonner"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDate } from "@/lib/format"
import type { AccountShareResponse } from "@/types/api"

const STATUS_LABELS: Record<AccountShareResponse["status"], string> = {
  pending: "En attente",
  accepted: "Accepté",
  rejected: "Refusé",
  revoked: "Révoqué",
}

const STATUS_CLASSES: Record<AccountShareResponse["status"], string> = {
  pending: "border-amber-300 text-amber-700 bg-amber-50",
  accepted: "border-green-300 text-green-700 bg-green-50",
  rejected: "border-gray-300 text-gray-500 bg-gray-50",
  revoked: "border-red-300 text-red-700 bg-red-50",
}

interface SharesModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  accountId: string
  accountName: string | null
}

export function SharesModal({ open, onOpenChange, accountId, accountName }: SharesModalProps) {
  const [shares, setShares] = useState<AccountShareResponse[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [revokingId, setRevokingId] = useState<string | null>(null)

  useEffect(() => {
    if (!open || !accountId) return
    setIsLoading(true)
    fetch(`/api/accounts/${accountId}/shares`)
      .then((r) => (r.ok ? r.json() : []))
      .then((data: AccountShareResponse[]) => setShares(data))
      .catch(() => setShares([]))
      .finally(() => setIsLoading(false))
  }, [open, accountId])

  async function handleRevoke(shareId: string) {
    setRevokingId(shareId)
    try {
      const res = await fetch(`/api/accounts/${accountId}/shares/${shareId}`, {
        method: "DELETE",
      })
      if (res.ok || res.status === 204) {
        setShares((prev) =>
          prev.map((s) => (s.id === shareId ? { ...s, status: "revoked" as const } : s)),
        )
        toast.success("Partage révoqué.")
      } else {
        const data = await res.json().catch(() => ({}))
        toast.error(data.detail ?? data.message ?? "Erreur lors de la révocation.")
      }
    } catch {
      toast.error("Erreur réseau.")
    } finally {
      setRevokingId(null)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>
            Partages
            {accountName && (
              <span className="font-normal text-gray-500"> — {accountName}</span>
            )}
          </DialogTitle>
          <DialogDescription>
            Gérez les utilisateurs ayant accès à ce compte.
          </DialogDescription>
        </DialogHeader>

        <div className="mt-2 space-y-3">
          {isLoading ? (
            <>
              {[1, 2].map((i) => (
                <div key={i} className="flex items-center justify-between py-2">
                  <div className="space-y-1.5">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-32" />
                  </div>
                  <Skeleton className="h-6 w-20 rounded-full" />
                </div>
              ))}
            </>
          ) : shares.length === 0 ? (
            <p className="py-6 text-center text-sm text-gray-500">
              Aucun partage actif pour ce compte.
            </p>
          ) : (
            shares.map((share) => (
              <div
                key={share.id}
                className="flex items-center justify-between gap-4 rounded-lg border border-gray-100 px-4 py-3"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-gray-900">
                    {share.invitee_email}
                  </p>
                  <p className="text-xs text-gray-400">
                    Expire le {formatDate(share.expires_at)}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Badge variant="outline" className={STATUS_CLASSES[share.status]}>
                    {STATUS_LABELS[share.status]}
                  </Badge>
                  {(share.status === "pending" || share.status === "accepted") && (
                    <Button
                      size="icon"
                      variant="ghost"
                      className="size-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                      disabled={revokingId === share.id}
                      onClick={() => handleRevoke(share.id)}
                      aria-label="Révoquer"
                    >
                      <Trash2 size={14} />
                    </Button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
