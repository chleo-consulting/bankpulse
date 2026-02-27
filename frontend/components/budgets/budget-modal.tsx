"use client"

import { useEffect, useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { BudgetProgressItem, CategoryWithChildrenResponse } from "@/types/api"

const createSchema = z.object({
  category_id: z.string().min(1, "La catégorie est requise"),
  amount_limit: z.number().positive("Le montant doit être positif"),
  period_type: z.string().min(1, "La période est requise"),
})

const editSchema = z.object({
  amount_limit: z.number().positive("Le montant doit être positif"),
  period_type: z.string().min(1, "La période est requise"),
})

type CreateFormData = z.infer<typeof createSchema>
type EditFormData = z.infer<typeof editSchema>

const PERIOD_LABELS: Record<string, string> = {
  monthly: "Mensuel",
  quarterly: "Trimestriel",
  yearly: "Annuel",
}

interface BudgetModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
  categories: CategoryWithChildrenResponse[]
  editItem?: BudgetProgressItem | null
}

export function BudgetModal({
  open,
  onOpenChange,
  onSuccess,
  categories,
  editItem,
}: BudgetModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const isEdit = !!editItem

  const createForm = useForm<CreateFormData>({
    resolver: zodResolver(createSchema),
    defaultValues: { category_id: "", amount_limit: 0, period_type: "monthly" },
  })

  const editForm = useForm<EditFormData>({
    resolver: zodResolver(editSchema),
    defaultValues: { amount_limit: 0, period_type: "monthly" },
  })

  useEffect(() => {
    if (open) {
      if (editItem) {
        editForm.reset({
          amount_limit: Number(editItem.limit),
          period_type: editItem.period_type,
        })
      } else {
        createForm.reset({ category_id: "", amount_limit: 0, period_type: "monthly" })
      }
    }
  }, [open, editItem]) // eslint-disable-line react-hooks/exhaustive-deps

  // Flatten categories: parents without children + all children with "Parent > Child" label
  const allCategories = categories.flatMap((cat) =>
    cat.children.length > 0
      ? cat.children.map((child) => ({
          id: child.id,
          label: `${cat.icon ?? ""} ${cat.name} › ${child.name}`.trim(),
        }))
      : [{ id: cat.id, label: `${cat.icon ?? ""} ${cat.name}`.trim() }]
  )

  async function onCreateSubmit(data: CreateFormData) {
    setIsLoading(true)
    try {
      const res = await fetch("/api/budgets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        toast.error(err.detail ?? err.message ?? "Erreur lors de la création")
        return
      }
      toast.success("Budget créé avec succès")
      onSuccess()
      onOpenChange(false)
    } catch {
      toast.error("Erreur serveur")
    } finally {
      setIsLoading(false)
    }
  }

  async function onEditSubmit(data: EditFormData) {
    if (!editItem) return
    setIsLoading(true)
    try {
      const res = await fetch(`/api/budgets/${editItem.budget_id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        toast.error(err.detail ?? err.message ?? "Erreur lors de la modification")
        return
      }
      toast.success("Budget modifié avec succès")
      onSuccess()
      onOpenChange(false)
    } catch {
      toast.error("Erreur serveur")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Modifier le budget" : "Créer un budget"}</DialogTitle>
        </DialogHeader>

        {isEdit ? (
          <Form {...editForm}>
            <form onSubmit={editForm.handleSubmit(onEditSubmit)} className="space-y-4">
              <div className="rounded-md bg-gray-50 px-3 py-2 text-sm text-gray-700">
                <span className="font-medium">Catégorie :</span> {editItem?.category_name}
              </div>

              <FormField
                control={editForm.control}
                name="amount_limit"
                render={({ field: { onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>Montant limite * (€)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="500,00"
                        {...field}
                        onChange={(e) => onChange(e.target.valueAsNumber || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={editForm.control}
                name="period_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Période *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionner une période" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {Object.entries(PERIOD_LABELS).map(([value, label]) => (
                          <SelectItem key={value} value={value}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex gap-3 justify-end pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => onOpenChange(false)}
                  disabled={isLoading}
                >
                  Annuler
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Enregistrement..." : "Enregistrer"}
                </Button>
              </div>
            </form>
          </Form>
        ) : (
          <Form {...createForm}>
            <form onSubmit={createForm.handleSubmit(onCreateSubmit)} className="space-y-4">
              <FormField
                control={createForm.control}
                name="category_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Catégorie *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionner une catégorie" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {allCategories.map((cat) => (
                          <SelectItem key={cat.id} value={cat.id}>
                            {cat.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={createForm.control}
                name="amount_limit"
                render={({ field: { onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>Montant limite * (€)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="500,00"
                        {...field}
                        onChange={(e) => onChange(e.target.valueAsNumber || 0)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={createForm.control}
                name="period_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Période *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionner une période" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {Object.entries(PERIOD_LABELS).map(([value, label]) => (
                          <SelectItem key={value} value={value}>
                            {label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex gap-3 justify-end pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => onOpenChange(false)}
                  disabled={isLoading}
                >
                  Annuler
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Création..." : "Créer"}
                </Button>
              </div>
            </form>
          </Form>
        )}
      </DialogContent>
    </Dialog>
  )
}
