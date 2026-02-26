"use client"

import { useState } from "react"
import { Building2, MoreVertical, Plus, Trash2, Upload } from "lucide-react"
import { toast } from "sonner"

import { EmptyState } from "@/components/shared/empty-state"
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
import type { BankAccountResponse } from "@/types/api"

import { AddAccountModal } from "./add-account-modal"
import { ImportCSVModal } from "./import-csv-modal"

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  checking: "Compte courant",
  savings: "Compte épargne",
  joint: "Compte joint",
  investment: "Investissement",
}

interface AccountsListProps {
  initialAccounts: BankAccountResponse[]
}

export function AccountsList({ initialAccounts }: AccountsListProps) {
  const [accounts, setAccounts] = useState<BankAccountResponse[]>(initialAccounts)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [importAccountId, setImportAccountId] = useState<string | null>(null)

  const totalBalance = accounts.reduce((sum, a) => sum + Number(a.balance), 0)
  const importAccount = importAccountId
    ? (accounts.find((a) => a.id === importAccountId) ?? null)
    : null

  function handleAccountAdded(account: BankAccountResponse) {
    setAccounts((prev) => [...prev, account])
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
    </div>
  )
}

function AccountCard({
  account,
  onImport,
  onDelete,
}: {
  account: BankAccountResponse
  onImport: () => void
  onDelete: () => void
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
              <h3 className="font-semibold text-gray-900 truncate">
                {account.account_name ?? "Compte sans nom"}
              </h3>
              {account.iban && (
                <p className="text-sm font-mono text-gray-500 mt-0.5 truncate">{account.iban}</p>
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
