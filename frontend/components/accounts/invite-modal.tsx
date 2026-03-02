"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import type { AccountShareResponse } from "@/types/api"

const schema = z.object({
  email: z.string().email("Adresse email invalide"),
})
type FormData = z.infer<typeof schema>

interface InviteModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  accountId: string
  accountName: string | null
  onSuccess: (share: AccountShareResponse) => void
}

export function InviteModal({
  open,
  onOpenChange,
  accountId,
  accountName,
  onSuccess,
}: InviteModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { email: "" },
  })

  async function onSubmit(data: FormData) {
    setIsSubmitting(true)
    try {
      const res = await fetch(`/api/accounts/${accountId}/shares`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: data.email }),
      })
      const json = await res.json()
      if (res.status === 409) {
        toast.error("Une invitation est déjà en attente pour cet email.")
        return
      }
      if (!res.ok) {
        toast.error(json.detail ?? json.message ?? "Erreur lors de l'envoi de l'invitation.")
        return
      }
      toast.success(`Invitation envoyée à ${data.email}`)
      form.reset()
      onOpenChange(false)
      onSuccess(json as AccountShareResponse)
    } catch {
      toast.error("Erreur réseau. Veuillez réessayer.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            Inviter un utilisateur
            {accountName && (
              <span className="font-normal text-gray-500"> — {accountName}</span>
            )}
          </DialogTitle>
          <DialogDescription>
            L'invité recevra un email avec un lien pour accéder à ce compte.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Adresse email de l'invité</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="prenom.nom@exemple.fr"
                      autoComplete="email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Annuler
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Envoi en cours…" : "Envoyer l'invitation"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
