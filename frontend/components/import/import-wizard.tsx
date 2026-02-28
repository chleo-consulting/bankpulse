"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { CheckCircle2 } from "lucide-react"
import { toast } from "sonner"

import { cn } from "@/lib/utils"
import type { ImportResult } from "@/types/api"

import { FileUploadStep, type UploadState } from "./file-upload-step"
import { FormatSelector, type ImportFormat } from "./format-selector"
import { ImportResultView } from "./import-result-view"

// ---------------------------------------------------------------------------
// Formats supportés (concept 100% frontend — flip `available` quand le
// backend expose le parser correspondant)
// ---------------------------------------------------------------------------
const IMPORT_FORMATS: ImportFormat[] = [
  { id: "boursorama", label: "Boursorama", available: true },
  { id: "bnp", label: "BNP Paribas", available: false },
  { id: "ca", label: "Crédit Agricole", available: false },
  { id: "lcl", label: "LCL", available: false },
  { id: "sg", label: "Société Générale", available: false },
]

// ---------------------------------------------------------------------------
// Types d'état du wizard
// ---------------------------------------------------------------------------
type WizardStep =
  | { step: "select-format" }
  | { step: "upload"; formatId: string }
  | { step: "result"; formatId: string; result: ImportResult }

// ---------------------------------------------------------------------------
// Indicateur d'étapes
// ---------------------------------------------------------------------------
const STEP_LABELS = ["Banque", "Fichier", "Résultats"]

function StepIndicator({ currentStep }: { currentStep: number }) {
  return (
    <div className="flex items-center gap-1">
      {STEP_LABELS.map((label, i) => (
        <div key={i} className="flex items-center gap-1">
          <div
            className={cn(
              "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold transition-colors",
              i < currentStep
                ? "bg-indigo-600 text-white"
                : i === currentStep
                  ? "bg-indigo-600 text-white ring-4 ring-indigo-100"
                  : "bg-gray-100 text-gray-400",
            )}
          >
            {i < currentStep ? <CheckCircle2 size={14} /> : i + 1}
          </div>
          <span
            className={cn(
              "text-sm font-medium",
              i <= currentStep ? "text-gray-900" : "text-gray-400",
            )}
          >
            {label}
          </span>
          {i < STEP_LABELS.length - 1 && (
            <div
              className={cn("mx-2 h-px w-8", i < currentStep ? "bg-indigo-600" : "bg-gray-200")}
            />
          )}
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Wizard principal
// ---------------------------------------------------------------------------
export function ImportWizard() {
  const router = useRouter()

  const [wizardStep, setWizardStep] = useState<WizardStep>({ step: "select-format" })
  const [uploadState, setUploadState] = useState<UploadState>({ status: "idle" })
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const currentStepIndex =
    wizardStep.step === "select-format" ? 0 : wizardStep.step === "upload" ? 1 : 2

  async function handleImport() {
    if (!selectedFile || wizardStep.step !== "upload") return
    setUploadState({ status: "loading" })

    const formData = new FormData()
    formData.append("file", selectedFile)

    try {
      const res = await fetch(`/api/import/${wizardStep.formatId}`, {
        method: "POST",
        body: formData,
      })
      const data = await res.json()

      if (!res.ok) {
        setUploadState({ status: "error", message: data.message ?? "Erreur lors de l'import" })
        return
      }

      toast.success(
        `${data.total_created} transaction${data.total_created > 1 ? "s" : ""} importée${data.total_created > 1 ? "s" : ""}`,
      )
      setWizardStep({ step: "result", formatId: wizardStep.formatId, result: data })
    } catch {
      setUploadState({ status: "error", message: "Erreur réseau" })
    }
  }

  function handleReset() {
    setWizardStep({ step: "select-format" })
    setUploadState({ status: "idle" })
    setSelectedFile(null)
  }

  function handleBack() {
    setWizardStep({ step: "select-format" })
    setUploadState({ status: "idle" })
    setSelectedFile(null)
  }

  return (
    <div className="space-y-6">
      <StepIndicator currentStep={currentStepIndex} />

      {wizardStep.step === "select-format" && (
        <FormatSelector
          formats={IMPORT_FORMATS}
          onSelect={(id) => setWizardStep({ step: "upload", formatId: id })}
        />
      )}

      {wizardStep.step === "upload" && (
        <FileUploadStep
          formatLabel={IMPORT_FORMATS.find((f) => f.id === wizardStep.formatId)?.label ?? ""}
          selectedFile={selectedFile}
          onFileChange={setSelectedFile}
          uploadState={uploadState}
          onImport={handleImport}
          onBack={handleBack}
        />
      )}

      {wizardStep.step === "result" && (
        <ImportResultView
          result={wizardStep.result}
          onReset={handleReset}
          onViewTransactions={() => router.push("/transactions")}
        />
      )}
    </div>
  )
}
