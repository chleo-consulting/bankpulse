"use client"

import { useMemo, useRef, useState } from "react"
import {
  ChevronLeft,
  ChevronRight,
  Download,
  List,
  MoreHorizontal,
  RotateCcw,
  Tag,
} from "lucide-react"
import { toast } from "sonner"

import { EmptyState } from "@/components/shared/empty-state"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { formatAmount, formatDate } from "@/lib/format"
import type {
  BankAccountResponse,
  CategoryWithChildrenResponse,
  CursorTransactionListResponse,
  TagResponse,
  TransactionResponse,
} from "@/types/api"

// ─── Types ─────────────────────────────────────────────────────────────────

interface Filters {
  accountId: string
  categoryId: string
  tagId: string
  dateFrom: string
  dateTo: string
  amountMin: string
  amountMax: string
  search: string
}

const INITIAL_FILTERS: Filters = {
  accountId: "",
  categoryId: "",
  tagId: "",
  dateFrom: "",
  dateTo: "",
  amountMin: "",
  amountMax: "",
  search: "",
}

interface TransactionsListProps {
  initialTransactions: CursorTransactionListResponse
  categories: CategoryWithChildrenResponse[]
  accounts: BankAccountResponse[]
  tags: TagResponse[]
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function buildParams(filters: Filters, cursor: string | null): URLSearchParams {
  const params = new URLSearchParams()
  params.set("page_size", "50")
  if (cursor) params.set("cursor", cursor)
  if (filters.accountId) params.set("account_id", filters.accountId)
  if (filters.categoryId) params.set("category_id", filters.categoryId)
  if (filters.tagId) params.set("tag_id", filters.tagId)
  if (filters.dateFrom) params.set("date_from", filters.dateFrom)
  if (filters.dateTo) params.set("date_to", filters.dateTo)
  if (filters.amountMin) params.set("amount_min", filters.amountMin)
  if (filters.amountMax) params.set("amount_max", filters.amountMax)
  return params
}

// ─── Main Component ─────────────────────────────────────────────────────────

export function TransactionsList({
  initialTransactions,
  categories,
  accounts,
  tags,
}: TransactionsListProps) {
  const [transactions, setTransactions] = useState<TransactionResponse[]>(
    initialTransactions.items,
  )
  const [nextCursor, setNextCursor] = useState<string | null>(initialTransactions.next_cursor)
  const [cursor, setCursor] = useState<string | null>(null)
  const [prevCursors, setPrevCursors] = useState<string[]>([])
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(false)

  const [filters, setFilters] = useState<Filters>(INITIAL_FILTERS)
  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [isBulkTagOpen, setIsBulkTagOpen] = useState(false)
  const [selectedTagIds, setSelectedTagIds] = useState<Set<string>>(new Set())
  const [isBulkTagLoading, setIsBulkTagLoading] = useState(false)

  // ─── Category helpers ──────────────────────────────────────────────────

  const categoryMap = useMemo(() => {
    const map = new Map<string, { name: string; icon: string | null }>()
    for (const parent of categories) {
      map.set(parent.id, { name: parent.name, icon: parent.icon })
      for (const child of parent.children) {
        map.set(child.id, { name: child.name, icon: child.icon })
      }
    }
    return map
  }, [categories])

  const flatCategories = useMemo(() => {
    const flat: { id: string; label: string }[] = []
    for (const parent of categories) {
      flat.push({ id: parent.id, label: `${parent.icon ?? ""} ${parent.name}` })
      for (const child of parent.children) {
        flat.push({ id: child.id, label: `  ${child.icon ?? ""} ${child.name}` })
      }
    }
    return flat
  }, [categories])

  // ─── Fetch ─────────────────────────────────────────────────────────────

  async function load(currentCursor: string | null, currentFilters: Filters) {
    setIsLoading(true)
    try {
      const params = buildParams(currentFilters, currentCursor)
      const url = currentFilters.search
        ? `/api/transactions/search?q=${encodeURIComponent(currentFilters.search)}&${params.toString()}`
        : `/api/transactions?${params.toString()}`

      const res = await fetch(url)
      if (res.ok) {
        const data = (await res.json()) as CursorTransactionListResponse
        setTransactions(data.items)
        setNextCursor(data.next_cursor)
        setSelectedIds(new Set())
      } else {
        toast.error("Erreur lors du chargement des transactions")
      }
    } catch {
      toast.error("Erreur réseau")
    } finally {
      setIsLoading(false)
    }
  }

  function resetAndLoad(newFilters: Filters) {
    setCursor(null)
    setPrevCursors([])
    setPage(1)
    load(null, newFilters)
  }

  // ─── Filter handlers ───────────────────────────────────────────────────

  function applyFilter(key: keyof Filters, value: string) {
    const normalized = value === "all" ? "" : value
    const newFilters = { ...filters, [key]: normalized }
    setFilters(newFilters)
    resetAndLoad(newFilters)
  }

  function handleSearchChange(value: string) {
    const newFilters = { ...filters, search: value }
    setFilters(newFilters)
    if (searchTimer.current) clearTimeout(searchTimer.current)
    searchTimer.current = setTimeout(() => {
      resetAndLoad(newFilters)
    }, 400)
  }

  function resetFilters() {
    setFilters(INITIAL_FILTERS)
    resetAndLoad(INITIAL_FILTERS)
  }

  const hasActiveFilters = Object.values(filters).some((v) => v !== "")

  // ─── Pagination ────────────────────────────────────────────────────────

  function goNext() {
    if (!nextCursor) return
    const newPrevCursors = cursor ? [...prevCursors, cursor] : prevCursors
    setPrevCursors(newPrevCursors)
    setCursor(nextCursor)
    setPage((p) => p + 1)
    load(nextCursor, filters)
  }

  function goPrev() {
    const prevCursor = prevCursors[prevCursors.length - 1] ?? null
    const newPrevCursors = prevCursors.slice(0, -1)
    setPrevCursors(newPrevCursors)
    setCursor(prevCursor)
    setPage((p) => Math.max(1, p - 1))
    load(prevCursor, filters)
  }

  // ─── Selection ─────────────────────────────────────────────────────────

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  function toggleSelectAll() {
    if (selectedIds.size === transactions.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(transactions.map((t) => t.id)))
    }
  }

  const allSelected = transactions.length > 0 && selectedIds.size === transactions.length

  // ─── Category update ───────────────────────────────────────────────────

  async function handleCategoryChange(txId: string, categoryId: string) {
    const body = { category_id: categoryId || null }
    const res = await fetch(`/api/transactions/${txId}/category`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
    if (res.ok) {
      setTransactions((prev) =>
        prev.map((t) => (t.id === txId ? { ...t, category_id: categoryId || null } : t)),
      )
    } else {
      toast.error("Erreur lors de la mise à jour de la catégorie")
    }
  }

  // ─── Bulk tag ──────────────────────────────────────────────────────────

  async function handleBulkTag() {
    if (selectedTagIds.size === 0) return
    setIsBulkTagLoading(true)
    try {
      const res = await fetch("/api/transactions/bulk-tag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          transaction_ids: Array.from(selectedIds),
          tag_ids: Array.from(selectedTagIds),
        }),
      })
      if (res.ok || res.status === 204) {
        toast.success(`Tags appliqués à ${selectedIds.size} transaction(s)`)
        setIsBulkTagOpen(false)
        setSelectedTagIds(new Set())
        load(cursor, filters)
      } else {
        toast.error("Erreur lors de l'application des tags")
      }
    } catch {
      toast.error("Erreur réseau")
    } finally {
      setIsBulkTagLoading(false)
    }
  }

  // ─── Export ────────────────────────────────────────────────────────────

  async function handleExport() {
    const params = buildParams(filters, null)
    try {
      const res = await fetch(`/api/transactions/export?${params.toString()}`)
      if (res.ok) {
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = "transactions.csv"
        a.click()
        URL.revokeObjectURL(url)
        toast.success("Export CSV téléchargé")
      } else {
        toast.error("Erreur lors de l'export")
      }
    } catch {
      toast.error("Erreur réseau")
    }
  }

  // ─── Render ────────────────────────────────────────────────────────────

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
      </div>

      {/* Barre de filtres (sticky) */}
      <Card className="mb-4 sticky top-16 z-30">
        <CardContent className="py-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-700 flex items-center gap-1.5">
              <List size={14} />
              Filtres
            </span>
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={resetFilters} className="text-xs h-7">
                <RotateCcw size={12} className="mr-1" />
                Réinitialiser
              </Button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Compte */}
            <Select
              value={filters.accountId || "all"}
              onValueChange={(v) => applyFilter("accountId", v)}
            >
              <SelectTrigger className="h-9 text-sm">
                <SelectValue placeholder="Tous les comptes" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les comptes</SelectItem>
                {accounts.map((acc) => (
                  <SelectItem key={acc.id} value={acc.id}>
                    {acc.account_name ?? "Compte sans nom"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Catégorie */}
            <Select
              value={filters.categoryId || "all"}
              onValueChange={(v) => applyFilter("categoryId", v)}
            >
              <SelectTrigger className="h-9 text-sm">
                <SelectValue placeholder="Toutes catégories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes catégories</SelectItem>
                {flatCategories.map((cat) => (
                  <SelectItem key={cat.id} value={cat.id}>
                    {cat.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Tag */}
            <Select
              value={filters.tagId || "all"}
              onValueChange={(v) => applyFilter("tagId", v)}
            >
              <SelectTrigger className="h-9 text-sm">
                <SelectValue placeholder="Tous les tags" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les tags</SelectItem>
                {tags.map((tag) => (
                  <SelectItem key={tag.id} value={tag.id}>
                    {tag.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Recherche */}
            <Input
              placeholder="Rechercher..."
              value={filters.search}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="h-9 text-sm"
            />

            {/* Date de */}
            <div className="flex flex-col gap-1">
              <Label className="text-xs text-gray-500">Du</Label>
              <Input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => applyFilter("dateFrom", e.target.value)}
                className="h-9 text-sm"
              />
            </div>

            {/* Date au */}
            <div className="flex flex-col gap-1">
              <Label className="text-xs text-gray-500">Au</Label>
              <Input
                type="date"
                value={filters.dateTo}
                onChange={(e) => applyFilter("dateTo", e.target.value)}
                className="h-9 text-sm"
              />
            </div>

            {/* Montant min */}
            <Input
              type="number"
              placeholder="Montant min €"
              value={filters.amountMin}
              onChange={(e) => applyFilter("amountMin", e.target.value)}
              className="h-9 text-sm"
            />

            {/* Montant max */}
            <Input
              type="number"
              placeholder="Montant max €"
              value={filters.amountMax}
              onChange={(e) => applyFilter("amountMax", e.target.value)}
              className="h-9 text-sm"
            />
          </div>
        </CardContent>
      </Card>

      {/* Toolbar */}
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm text-gray-600">
          {transactions.length} transaction{transactions.length !== 1 ? "s" : ""}
          {selectedIds.size > 0 && (
            <span className="ml-1 font-medium text-gray-900">
              • {selectedIds.size} sélectionnée{selectedIds.size !== 1 ? "s" : ""}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {selectedIds.size > 0 && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <MoreHorizontal size={14} className="mr-1.5" />
                  Actions
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => {
                    setSelectedTagIds(new Set())
                    setIsBulkTagOpen(true)
                  }}
                >
                  <Tag size={14} className="mr-2" />
                  Tagger ({selectedIds.size})
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}

          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download size={14} className="mr-1.5" />
            Exporter CSV
          </Button>
        </div>
      </div>

      {/* Table */}
      {transactions.length === 0 ? (
        <EmptyState
          icon={<List size={64} />}
          title="Aucune transaction"
          description={
            hasActiveFilters
              ? "Aucune transaction ne correspond aux filtres sélectionnés."
              : "Importez un fichier CSV depuis Mes Comptes."
          }
          action={
            hasActiveFilters
              ? { label: "Réinitialiser les filtres", href: "#" }
              : { label: "Mes Comptes", href: "/accounts" }
          }
        />
      ) : (
        <Card>
          <div className={isLoading ? "opacity-60 pointer-events-none" : ""}>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10">
                    <Checkbox
                      checked={allSelected}
                      onCheckedChange={toggleSelectAll}
                      aria-label="Tout sélectionner"
                    />
                  </TableHead>
                  <TableHead className="w-24">Date</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead className="text-right w-32">Montant</TableHead>
                  <TableHead className="w-40">Catégorie</TableHead>
                  <TableHead className="w-32">Tags</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((tx) => (
                  <TransactionRow
                    key={tx.id}
                    transaction={tx}
                    selected={selectedIds.has(tx.id)}
                    onSelect={() => toggleSelect(tx.id)}
                    categoryMap={categoryMap}
                    flatCategories={flatCategories}
                    onCategoryChange={(catId) => handleCategoryChange(tx.id, catId)}
                  />
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center gap-3 py-4 border-t">
            <Button
              variant="outline"
              size="sm"
              onClick={goPrev}
              disabled={page === 1 || isLoading}
            >
              <ChevronLeft size={14} className="mr-1" />
              Précédent
            </Button>
            <span className="text-sm text-gray-600 min-w-[60px] text-center">
              Page {page}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={goNext}
              disabled={!nextCursor || isLoading}
            >
              Suivant
              <ChevronRight size={14} className="ml-1" />
            </Button>
          </div>
        </Card>
      )}

      {/* Modal bulk tag */}
      <BulkTagModal
        open={isBulkTagOpen}
        onOpenChange={setIsBulkTagOpen}
        tags={tags}
        count={selectedIds.size}
        selectedTagIds={selectedTagIds}
        onToggleTag={(id) =>
          setSelectedTagIds((prev) => {
            const next = new Set(prev)
            next.has(id) ? next.delete(id) : next.add(id)
            return next
          })
        }
        onApply={handleBulkTag}
        isLoading={isBulkTagLoading}
      />
    </div>
  )
}

// ─── TransactionRow ─────────────────────────────────────────────────────────

interface TransactionRowProps {
  transaction: TransactionResponse
  selected: boolean
  onSelect: () => void
  categoryMap: Map<string, { name: string; icon: string | null }>
  flatCategories: { id: string; label: string }[]
  onCategoryChange: (categoryId: string) => void
}

function TransactionRow({
  transaction: tx,
  selected,
  onSelect,
  categoryMap,
  flatCategories,
  onCategoryChange,
}: TransactionRowProps) {
  const amount = Number(tx.amount)
  const cat = tx.category_id ? categoryMap.get(tx.category_id) : null

  return (
    <TableRow className={selected ? "bg-indigo-50" : undefined}>
      <TableCell>
        <Checkbox checked={selected} onCheckedChange={onSelect} aria-label="Sélectionner" />
      </TableCell>

      <TableCell className="text-sm text-gray-600 whitespace-nowrap">
        {formatDate(tx.transaction_date)}
      </TableCell>

      <TableCell className="text-sm text-gray-900 max-w-xs">
        <span className="truncate block" title={tx.description ?? ""}>
          {tx.description ?? "—"}
        </span>
        {tx.is_pending && (
          <Badge variant="outline" className="text-xs mt-0.5">
            En attente
          </Badge>
        )}
      </TableCell>

      <TableCell className="text-right font-mono font-semibold text-sm whitespace-nowrap">
        <span className={amount < 0 ? "text-red-500" : "text-emerald-600"}>
          {formatAmount(amount)}
        </span>
      </TableCell>

      <TableCell>
        <Select
          value={tx.category_id ?? "none"}
          onValueChange={(v) => onCategoryChange(v === "none" ? "" : v)}
        >
          <SelectTrigger className="h-7 text-xs w-36 border-dashed">
            <SelectValue>
              {cat ? `${cat.icon ?? ""} ${cat.name}` : <span className="text-gray-400">—</span>}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">— Aucune —</SelectItem>
            {flatCategories.map((c) => (
              <SelectItem key={c.id} value={c.id}>
                {c.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </TableCell>

      <TableCell>
        <div className="flex flex-wrap gap-1">
          {tx.tags.map((tag) => (
            <Badge key={tag.id} variant="secondary" className="text-xs py-0">
              {tag.name}
            </Badge>
          ))}
        </div>
      </TableCell>
    </TableRow>
  )
}

// ─── BulkTagModal ───────────────────────────────────────────────────────────

interface BulkTagModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tags: TagResponse[]
  count: number
  selectedTagIds: Set<string>
  onToggleTag: (id: string) => void
  onApply: () => void
  isLoading: boolean
}

function BulkTagModal({
  open,
  onOpenChange,
  tags,
  count,
  selectedTagIds,
  onToggleTag,
  onApply,
  isLoading,
}: BulkTagModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Tagger {count} transaction{count !== 1 ? "s" : ""}</DialogTitle>
        </DialogHeader>

        {tags.length === 0 ? (
          <p className="text-sm text-gray-500 py-4 text-center">
            Aucun tag disponible. Créez des tags via l&apos;API.
          </p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto py-2">
            {tags.map((tag) => (
              <label
                key={tag.id}
                className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-50 cursor-pointer"
              >
                <Checkbox
                  checked={selectedTagIds.has(tag.id)}
                  onCheckedChange={() => onToggleTag(tag.id)}
                  id={`tag-${tag.id}`}
                />
                <span className="text-sm font-medium">{tag.name}</span>
              </label>
            ))}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Annuler
          </Button>
          <Button
            onClick={onApply}
            disabled={selectedTagIds.size === 0 || isLoading}
          >
            {isLoading ? "Application..." : "Appliquer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
