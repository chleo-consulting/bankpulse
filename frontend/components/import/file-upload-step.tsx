"use client"

import { useRef, useState } from "react"
import { CloudUpload, FileText, XCircle } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export type UploadState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; message: string }

interface FileUploadStepProps {
  formatLabel: string
  selectedFile: File | null
  onFileChange: (file: File | null) => void
  uploadState: UploadState
  onImport: () => void
  onBack: () => void
}

export function FileUploadStep({
  formatLabel,
  selectedFile,
  onFileChange,
  uploadState,
  onImport,
  onBack,
}: FileUploadStepProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragOver, setIsDragOver] = useState(false)

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null
    onFileChange(file)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file?.name.endsWith(".csv")) {
      onFileChange(file)
    }
  }

  function handleBack() {
    // Reset le file input pour que la même sélection soit détectable ensuite
    if (fileInputRef.current) fileInputRef.current.value = ""
    onBack()
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
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-semibold">Importer votre fichier CSV</CardTitle>
        <p className="text-sm text-gray-500">Format : {formatLabel}</p>
      </CardHeader>

      <CardContent className="space-y-4">
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
              <p className="text-sm font-medium text-gray-700">Glissez votre fichier CSV ici</p>
              <p className="text-xs text-gray-500 mt-1">ou cliquez pour parcourir</p>
              <p className="text-xs text-gray-400 mt-3">Formats acceptés : .csv (max 10 Mo)</p>
            </>
          )}
        </div>

        {/* Erreur */}
        {uploadState.status === "error" && (
          <div className="flex items-center gap-2 rounded-md bg-red-50 p-3 text-sm text-red-600">
            <XCircle size={16} className="shrink-0" />
            {uploadState.message}
          </div>
        )}

        {/* Loading */}
        {uploadState.status === "loading" && (
          <div className="space-y-2">
            <p className="text-sm text-gray-600">Import en cours...</p>
            <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
              <div className="h-full w-3/4 animate-pulse rounded-full bg-indigo-500" />
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex justify-between gap-3">
        <Button variant="outline" onClick={handleBack} disabled={uploadState.status === "loading"}>
          Retour
        </Button>
        <Button
          onClick={onImport}
          disabled={!selectedFile || uploadState.status === "loading"}
        >
          {uploadState.status === "loading" ? "Import en cours..." : "Importer"}
        </Button>
      </CardFooter>
    </Card>
  )
}
