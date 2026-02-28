import { ImportWizard } from "@/components/import/import-wizard"

export default function ImportPage() {
  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Importer des transactions</h1>
        <p className="mt-1 text-sm text-gray-500">
          Importez vos relevés bancaires au format CSV
        </p>
      </div>
      <ImportWizard />
    </div>
  )
}
