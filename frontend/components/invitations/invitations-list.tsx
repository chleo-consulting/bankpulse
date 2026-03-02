"use client"

import { useState } from "react"
import { Bell, Check, X } from "lucide-react"
import { toast } from "sonner"

import { EmptyState } from "@/components/shared/empty-state"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { formatDate } from "@/lib/format"
import type { ReceivedInvitationResponse } from "@/types/api"

interface InvitationsListProps {
  initialInvitations: ReceivedInvitationResponse[]
}

const STATUS_LABELS: Record<ReceivedInvitationResponse["status"], string> = {
  pending: "En attente",
  accepted: "Accepté",
  rejected: "Refusé",
  revoked: "Révoqué",
}

const STATUS_CLASSES: Record<ReceivedInvitationResponse["status"], string> = {
  pending: "border-amber-300 text-amber-700 bg-amber-50",
  accepted: "border-green-300 text-green-700 bg-green-50",
  rejected: "border-gray-300 text-gray-500 bg-gray-50",
  revoked: "border-red-300 text-red-700 bg-red-50",
}

export function InvitationsList({ initialInvitations }: InvitationsListProps) {
  const [invitations, setInvitations] =
    useState<ReceivedInvitationResponse[]>(initialInvitations)
  const [loadingId, setLoadingId] = useState<string | null>(null)

  const pendingCount = invitations.filter((inv) => inv.status === "pending").length

  async function handleAccept(shareId: string) {
    setLoadingId(shareId)
    try {
      const res = await fetch(`/api/invitations/${shareId}/accept`, { method: "POST" })
      const data = await res.json().catch(() => ({}))
      if (res.ok) {
        setInvitations((prev) =>
          prev.map((inv) => (inv.id === shareId ? { ...inv, status: "accepted" as const } : inv)),
        )
        toast.success("Invitation acceptée ! Le compte est maintenant accessible.")
      } else {
        toast.error(data.detail ?? data.message ?? "Erreur lors de l'acceptation.")
      }
    } catch {
      toast.error("Erreur réseau.")
    } finally {
      setLoadingId(null)
    }
  }

  async function handleReject(shareId: string) {
    setLoadingId(shareId)
    try {
      const res = await fetch(`/api/invitations/${shareId}/reject`, { method: "POST" })
      const data = await res.json().catch(() => ({}))
      if (res.ok) {
        setInvitations((prev) =>
          prev.map((inv) => (inv.id === shareId ? { ...inv, status: "rejected" as const } : inv)),
        )
        toast.success("Invitation refusée.")
      } else {
        toast.error(data.detail ?? data.message ?? "Erreur lors du refus.")
      }
    } catch {
      toast.error("Erreur réseau.")
    } finally {
      setLoadingId(null)
    }
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Invitations</h1>
        {pendingCount > 0 && (
          <Badge className="bg-amber-100 text-amber-800 border border-amber-300 font-medium">
            {pendingCount} en attente
          </Badge>
        )}
      </div>

      {invitations.length === 0 ? (
        <EmptyState
          icon={<Bell size={64} />}
          title="Aucune invitation reçue"
          description="Les comptes partagés avec vous apparaîtront ici."
        />
      ) : (
        <div className="space-y-4">
          {invitations.map((invitation) => (
            <Card key={invitation.id}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h3 className="font-semibold text-gray-900">
                      {invitation.account_name ?? "Compte sans nom"}
                    </h3>
                    <p className="text-sm text-gray-500 mt-0.5">
                      Partagé par{" "}
                      {invitation.owner_name ? (
                        <>
                          {invitation.owner_name}{" "}
                          <span className="text-gray-400">({invitation.owner_email})</span>
                        </>
                      ) : (
                        invitation.owner_email
                      )}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Expire le {formatDate(invitation.expires_at)}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {invitation.status === "pending" ? (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-red-600 border-red-200 hover:bg-red-50"
                          disabled={loadingId === invitation.id}
                          onClick={() => handleReject(invitation.id)}
                        >
                          <X size={14} className="mr-1.5" />
                          Refuser
                        </Button>
                        <Button
                          size="sm"
                          disabled={loadingId === invitation.id}
                          onClick={() => handleAccept(invitation.id)}
                        >
                          <Check size={14} className="mr-1.5" />
                          Accepter
                        </Button>
                      </>
                    ) : (
                      <Badge
                        variant="outline"
                        className={STATUS_CLASSES[invitation.status]}
                      >
                        {STATUS_LABELS[invitation.status]}
                      </Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
