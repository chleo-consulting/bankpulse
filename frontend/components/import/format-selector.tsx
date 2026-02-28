"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export interface ImportFormat {
  id: string
  label: string
  available: boolean
}

interface FormatSelectorProps {
  formats: ImportFormat[]
  onSelect: (id: string) => void
}

function FormatInitials({ label }: { label: string }) {
  const initials = label
    .split(/[\s-]+/)
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase()

  return (
    <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100 text-sm font-bold text-indigo-700">
      {initials}
    </div>
  )
}

export function FormatSelector({ formats, onSelect }: FormatSelectorProps) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-medium text-gray-700">Choisissez votre banque</p>
        <p className="text-xs text-gray-500 mt-0.5">
          D&apos;autres banques seront disponibles prochainement
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
        {formats.map((format) =>
          format.available ? (
            <button
              key={format.id}
              type="button"
              onClick={() => onSelect(format.id)}
              className={cn(
                "group rounded-xl border-2 bg-white p-4 text-center transition-all duration-150",
                "border-gray-200 hover:border-indigo-400 hover:bg-indigo-50 hover:shadow-sm",
                "focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2",
              )}
            >
              <FormatInitials label={format.label} />
              <p className="text-sm font-semibold text-gray-900 group-hover:text-indigo-700">
                {format.label}
              </p>
            </button>
          ) : (
            <div
              key={format.id}
              aria-disabled="true"
              className="rounded-xl border-2 border-gray-100 bg-gray-50 p-4 text-center opacity-60"
            >
              <FormatInitials label={format.label} />
              <p className="text-sm font-semibold text-gray-500">{format.label}</p>
              <Badge variant="secondary" className="mt-2 text-xs">
                Bientôt disponible
              </Badge>
            </div>
          ),
        )}
      </div>
    </div>
  )
}
