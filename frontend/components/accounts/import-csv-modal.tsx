"use client"

import { useRef, useState } from "react"
import { CheckCircle2, CloudUpload, FileText, XCircle } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import type { BankAccountResponse, ImportResult } from "@/types/api"

type ImportState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; result: ImportResult }
  | { status: "error"; message: string }

interface ImportCSVModalProps {
  accountId: string | null
  account: BankAccountResponse | null
  onOpenChange: (open: boolean) => void
}

export function ImportCSVModal({ accountId, account, onOpenChange }: ImportCSVModalProps) {
  const open = !!accountId
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [state, setState] = useState<ImportState>({ status: "idle" })
  const [isDragOver, setIsDragOver] = useState(false)

  function handleClose() {
    onOpenChange(false)
    setSelectedFile(null)
    setState({ status: "idle" })
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null
    setSelectedFile(file)
    setState({ status: "idle" })
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file?.name.endsWith(".csv")) {
      setSelectedFile(file)
      setState({ status: "idle" })
    }
  }

  async function handleImport() {
    if (!selectedFile || !accountId) return

    setState({ status: "loading" })

    const formData = new FormData()
    formData.append("file", selectedFile)

    try {
      const res = await fetch(`/api/accounts/${accountId}/import`, {
        method: "POST",
        body: formData,
      })

      const data = await res.json()

      if (!res.ok) {
        setState({ status: "error", message: data.message ?? "Erreur lors de l'import" })
        return
      }

      setState({ status: "success", result: data })
      toast.success(`${data.total_created} transaction${data.total_created > 1 ? "s" : ""} importée${data.total_created > 1 ? "s" : ""}`)
    } catch {
      setState({ status: "error", message: "Erreur réseau" })
    }
  }

  const dropzoneClass = [
    "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
    isDragOver
      ? "border-indigo-400 bg-indigo-50"
      : selectedFile
        ? "border-green-400 bg-green-50"
        : "border-gray-200 hover:border-indigo-300 hover:bg-gray-50",
  ].join(" ")

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Importer des transactions</DialogTitle>
        </DialogHeader>

        {account && (
          <p className="text-sm text-gray-500 -mt-2">
            Compte cible :{" "}
            <span className="font-medium text-gray-900">{account.account_name}</span>
          </p>
        )}

        {state.status === "success" ? (
          <SuccessView result={state.result} onClose={handleClose} />
        ) : (
          <div className="space-y-4">
            {/* Dropzone */}
            <div
              className={dropzoneClass}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault()
                setIsDragOver(true)
              }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={handleFileChange}
              />
              {selectedFile ? (
                <>
                  <FileText size={32} className="mx-auto text-green-500 mb-3" />
                  <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {(selectedFile.size / 1024).toFixed(1)} Ko — cliquer pour changer
                  </p>
                </>
              ) : (
                <>
                  <CloudUpload size={32} className="mx-auto text-gray-400 mb-3" />
                  <p className="text-sm font-medium text-gray-700">
                    Glissez votre fichier CSV ici
                  </p>
                  <p className="text-xs text-gray-500 mt-1">ou cliquez pour parcourir</p>
                  <p className="text-xs text-gray-400 mt-3">
                    Formats acceptés : .csv (max 10 Mo) · Banques supportées : Boursorama
                  </p>
                </>
              )}
            </div>

            {/* Error */}
            {state.status === "error" && (
              <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 rounded-md p-3">
                <XCircle size={16} className="shrink-0" />
                {state.message}
              </div>
            )}

            {/* Loading */}
            {state.status === "loading" && (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">Import en cours...</p>
                <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full animate-pulse w-3/4" />
                </div>
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={handleClose}
                disabled={state.status === "loading"}
              >
                Annuler
              </Button>
              <Button
                onClick={handleImport}
                disabled={!selectedFile || state.status === "loading"}
              >
                {state.status === "loading" ? "Import en cours..." : "Importer"}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

function SuccessView({ result, onClose }: { result: ImportResult; onClose: () => void }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 text-green-600">
        <CheckCircle2 size={32} className="shrink-0" />
        <div>
          <p className="font-semibold text-lg">Import réussi !</p>
          <p className="text-sm text-gray-500">
            {result.total_created} transaction{result.total_created > 1 ? "s" : ""} importée
            {result.total_created > 1 ? "s" : ""}
            {result.total_skipped > 0 &&
              ` · ${result.total_skipped} doublon${result.total_skipped > 1 ? "s" : ""} ignoré${result.total_skipped > 1 ? "s" : ""}`}
          </p>
        </div>
      </div>

      {result.accounts.map((acc) => (
        <div key={acc.account_num} className="bg-gray-50 rounded-md p-3 text-sm">
          <p className="font-medium text-gray-900">{acc.account_label}</p>
          <p className="text-xs text-gray-500 font-mono mt-0.5">{acc.account_num}</p>
          <div className="flex gap-4 mt-2 text-xs">
            <span className="text-green-600">+{acc.nb_created} créées</span>
            {acc.nb_skipped > 0 && (
              <span className="text-amber-600">{acc.nb_skipped} ignorée{acc.nb_skipped > 1 ? "s" : ""}</span>
            )}
            {acc.nb_errors > 0 && (
              <span className="text-red-600">{acc.nb_errors} erreur{acc.nb_errors > 1 ? "s" : ""}</span>
            )}
            {acc.balance_updated && <span className="text-indigo-600">Solde mis à jour</span>}
          </div>
        </div>
      ))}

      <div className="flex gap-3 justify-end">
        <Button variant="outline" onClick={onClose}>
          Fermer
        </Button>
        <Button asChild>
          <a href="/transactions">Voir les transactions</a>
        </Button>
      </div>
    </div>
  )
}
