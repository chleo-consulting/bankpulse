"use client"

import { useState } from "react"
import { Building2, MoreVertical, Plus, Trash2, Upload, UserPlus, Users } from "lucide-react"
import { toast } from "sonner"

import { EmptyState } from "@/components/shared/empty-state"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { formatAmount, formatDate } from "@/lib/format"
import type { AccountShareResponse, BankAccountListResponse, BankAccountResponse } from "@/types/api"

import { AddAccountModal } from "./add-account-modal"
import { ImportCSVModal } from "./import-csv-modal"
import { InviteModal } from "./invite-modal"
import { SharesModal } from "./shares-modal"

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  checking: "Compte courant",
  savings: "Compte épargne",
  joint: "Compte joint",
  investment: "Investissement",
}

interface AccountsListProps {
  initialAccounts: BankAccountListResponse[]
}

export function AccountsList({ initialAccounts }: AccountsListProps) {
  const [accounts, setAccounts] = useState<BankAccountListResponse[]>(initialAccounts)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [importAccountId, setImportAccountId] = useState<string | null>(null)
  const [inviteAccountId, setInviteAccountId] = useState<string | null>(null)
  const [sharesAccountId, setSharesAccountId] = useState<string | null>(null)

  const totalBalance = accounts.reduce((sum, a) => sum + Number(a.balance), 0)
  const importAccount = importAccountId
    ? (accounts.find((a) => a.id === importAccountId) ?? null)
    : null
  const inviteAccount = inviteAccountId
    ? (accounts.find((a) => a.id === inviteAccountId) ?? null)
    : null
  const sharesAccount = sharesAccountId
    ? (accounts.find((a) => a.id === sharesAccountId) ?? null)
    : null

  // AddAccountModal retourne BankAccountResponse — on enrichit avec les champs is_shared
  function handleAccountAdded(account: BankAccountResponse) {
    const enriched: BankAccountListResponse = {
      ...account,
      is_shared: false,
      shared_by_email: null,
      shared_by_name: null,
    }
    setAccounts((prev) => [...prev, enriched])
  }

  async function handleDelete(id: string) {
    if (!confirm("Supprimer ce compte ? Cette action est irréversible.")) return

    const res = await fetch(`/api/accounts/${id}`, { method: "DELETE" })
    if (res.ok || res.status === 204) {
      setAccounts((prev) => prev.filter((a) => a.id !== id))
      toast.success("Compte supprimé")
    } else {
      toast.error("Erreur lors de la suppression")
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Mes Comptes</h1>
      </div>

      {/* Solde Consolidé */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="text-sm text-gray-500">Solde Total Consolidé</div>
          <div className="text-4xl font-bold font-mono mt-2">{formatAmount(totalBalance)}</div>
          <div className="text-sm text-gray-500 mt-1">
            {accounts.length} compte{accounts.length > 1 ? "s" : ""} actif
            {accounts.length > 1 ? "s" : ""}
          </div>
        </CardContent>
      </Card>

      {/* Actions Globales */}
      <div className="flex gap-3 mb-6">
        <Button onClick={() => setIsAddModalOpen(true)}>
          <Plus className="mr-2" size={16} />
          Ajouter un compte
        </Button>
      </div>

      {/* Liste des Comptes */}
      {accounts.length === 0 ? (
        <EmptyState
          icon={<Building2 size={64} />}
          title="Aucun compte bancaire"
          description="Ajoutez votre premier compte pour commencer à importer des transactions."
          action={{ label: "Ajouter un compte", href: "#" }}
        />
      ) : (
        <div className="space-y-4">
          {accounts.map((account) => (
            <AccountCard
              key={account.id}
              account={account}
              onImport={() => setImportAccountId(account.id)}
              onDelete={() => handleDelete(account.id)}
              onInvite={() => setInviteAccountId(account.id)}
              onManageShares={() => setSharesAccountId(account.id)}
            />
          ))}
        </div>
      )}

      <AddAccountModal
        open={isAddModalOpen}
        onOpenChange={setIsAddModalOpen}
        onSuccess={handleAccountAdded}
      />

      <ImportCSVModal
        accountId={importAccountId}
        account={importAccount}
        onOpenChange={(open) => {
          if (!open) setImportAccountId(null)
        }}
      />

      <InviteModal
        open={!!inviteAccountId}
        onOpenChange={(open) => {
          if (!open) setInviteAccountId(null)
        }}
        accountId={inviteAccountId ?? ""}
        accountName={inviteAccount?.account_name ?? null}
        onSuccess={(_share: AccountShareResponse) => {}}
      />

      <SharesModal
        open={!!sharesAccountId}
        onOpenChange={(open) => {
          if (!open) setSharesAccountId(null)
        }}
        accountId={sharesAccountId ?? ""}
        accountName={sharesAccount?.account_name ?? null}
      />
    </div>
  )
}

function AccountCard({
  account,
  onImport,
  onDelete,
  onInvite,
  onManageShares,
}: {
  account: BankAccountListResponse
  onImport: () => void
  onDelete: () => void
  onInvite: () => void
  onManageShares: () => void
}) {
  const typeLabel = account.account_type
    ? (ACCOUNT_TYPE_LABELS[account.account_type] ?? account.account_type)
    : null

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
              <Building2 size={20} className="text-indigo-600" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h3 className="font-semibold text-gray-900 truncate">
                  {account.account_name ?? "Compte sans nom"}
                </h3>
                {account.is_shared && (
                  <Badge
                    variant="outline"
                    className="text-xs border-blue-300 text-blue-700 bg-blue-50 shrink-0"
                  >
                    Partagé avec moi
                  </Badge>
                )}
              </div>
              {account.iban && (
                <p className="text-sm font-mono text-gray-500 mt-0.5 truncate">{account.iban}</p>
              )}
              {account.is_shared && account.shared_by_email && (
                <p className="text-xs text-gray-400 mt-0.5">
                  Partagé par{" "}
                  {account.shared_by_name
                    ? `${account.shared_by_name} (${account.shared_by_email})`
                    : account.shared_by_email}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Button variant="outline" size="sm" onClick={onImport}>
              <Upload size={14} className="mr-1.5" />
              Importer CSV
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <MoreVertical size={16} />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={onImport}>
                  <Upload size={14} className="mr-2" />
                  Importer CSV
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onInvite} disabled={account.is_shared}>
                  <UserPlus size={14} className="mr-2" />
                  Partager
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onManageShares} disabled={account.is_shared}>
                  <Users size={14} className="mr-2" />
                  Gérer les partages
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={onDelete}
                  className="text-red-600 focus:text-red-600"
                >
                  <Trash2 size={14} className="mr-2" />
                  Supprimer
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="mt-4 flex items-end justify-between">
          <div>
            <div className="text-2xl font-bold font-mono">
              {formatAmount(Number(account.balance))}
            </div>
            {typeLabel && <div className="text-sm text-gray-500 mt-1">{typeLabel}</div>}
          </div>
          <div className="text-xs text-gray-400 text-right">
            Créé le {formatDate(account.created_at)}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
