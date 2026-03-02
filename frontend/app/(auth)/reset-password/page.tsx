"use client"

import { Suspense, useEffect, useState } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { PasswordInput } from "@/components/ui/password-input"

const resetPasswordSchema = z
  .object({
    new_password: z.string().min(8, "Le mot de passe doit contenir au moins 8 caractères"),
    confirm_password: z.string().min(1, "Confirmation requise"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Les mots de passe ne correspondent pas",
    path: ["confirm_password"],
  })

type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>

function ResetPasswordForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get("token")

  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) {
      router.replace("/forgot-password")
    }
  }, [token, router])

  const form = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { new_password: "", confirm_password: "" },
  })

  async function onSubmit(values: ResetPasswordFormValues) {
    if (!token) return
    setError(null)
    try {
      const res = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: values.new_password }),
      })

      const data = await res.json().catch(() => ({}))

      if (!res.ok) {
        setError(data.message ?? "Token invalide ou expiré.")
        return
      }

      toast.success("Mot de passe réinitialisé avec succès !")
      router.push("/login")
    } catch {
      setError("Erreur réseau. Réessayez.")
    }
  }

  if (!token) return null

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="new_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nouveau mot de passe</FormLabel>
              <FormControl>
                <PasswordInput placeholder="8 caractères minimum" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="confirm_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirmer le mot de passe</FormLabel>
              <FormControl>
                <PasswordInput placeholder="••••••••" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {error && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
            <p>{error}</p>
            {(error.includes("invalide") || error.includes("expiré")) && (
              <p className="mt-1">
                <Link
                  href="/forgot-password"
                  className="underline font-medium hover:text-red-800"
                >
                  Demander un nouveau lien
                </Link>
              </p>
            )}
          </div>
        )}

        <Button
          type="submit"
          className="w-full bg-primary-600 hover:bg-primary-700"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? "Réinitialisation…" : "Réinitialiser le mot de passe"}
        </Button>
      </form>
    </Form>
  )
}

export default function ResetPasswordPage() {
  return (
    <div className="w-full max-w-md">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Nouveau mot de passe</h1>
        <p className="mt-2 text-sm text-gray-500">Choisissez un mot de passe sécurisé</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
        <Suspense fallback={<div className="text-sm text-gray-500">Chargement…</div>}>
          <ResetPasswordForm />
        </Suspense>

        <p className="mt-6 text-center text-sm text-gray-500">
          <Link href="/login" className="font-medium text-primary-600 hover:text-primary-700">
            ← Retour à la connexion
          </Link>
        </p>
      </div>
    </div>
  )
}
