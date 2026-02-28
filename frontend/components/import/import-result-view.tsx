"use client"

import { CheckCircle2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { ImportResult } from "@/types/api"

interface ImportResultViewProps {
  result: ImportResult
  onReset: () => void
  onViewTransactions: () => void
}

export function ImportResultView({ result, onReset, onViewTransactions }: ImportResultViewProps) {
  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100">
            <CheckCircle2 className="h-6 w-6 text-green-600" />
          </div>
          <div>
            <p className="text-lg font-semibold text-gray-900">Import réussi !</p>
            <p className="text-sm text-gray-500">
              {result.total_created} transaction(s) importée(s)
              {result.total_skipped > 0 && ` · ${result.total_skipped} doublon(s) ignoré(s)`}
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Mini-KPI row */}
        <div className="grid grid-cols-3 divide-x divide-gray-100 rounded-lg border border-gray-100 bg-gray-50">
          <div className="px-4 py-3 text-center">
            <p className="text-xl font-bold text-green-600">{result.total_created}</p>
            <p className="text-xs text-gray-500">Créées</p>
          </div>
          <div className="px-4 py-3 text-center">
            <p className="text-xl font-bold text-amber-500">{result.total_skipped}</p>
            <p className="text-xs text-gray-500">Ignorées</p>
          </div>
          <div className="px-4 py-3 text-center">
            <p className="text-xl font-bold text-red-500">{result.total_errors}</p>
            <p className="text-xs text-gray-500">Erreurs</p>
          </div>
        </div>

        {/* Tableau par compte */}
        {result.accounts.length > 0 && (
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Compte</TableHead>
                  <TableHead>Référence</TableHead>
                  <TableHead className="text-right">Créées</TableHead>
                  <TableHead className="text-right">Ignorées</TableHead>
                  <TableHead className="text-right">Erreurs</TableHead>
                  <TableHead className="text-center">Solde MàJ</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.accounts.map((account, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-medium">{account.account_label || "—"}</TableCell>
                    <TableCell className="font-mono text-xs text-gray-500">
                      {account.account_num}
                    </TableCell>
                    <TableCell className="text-right text-green-600">{account.nb_created}</TableCell>
                    <TableCell className="text-right text-amber-500">{account.nb_skipped}</TableCell>
                    <TableCell className="text-right text-red-500">{account.nb_errors}</TableCell>
                    <TableCell className="text-center">
                      {account.balance_updated ? (
                        <span className="text-green-600">✓</span>
                      ) : (
                        <span className="text-gray-300">—</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex justify-between gap-3 pt-2">
        <Button variant="outline" onClick={onReset}>
          Nouvel import
        </Button>
        <Button onClick={onViewTransactions}>Voir les transactions</Button>
      </CardFooter>
    </Card>
  )
}
