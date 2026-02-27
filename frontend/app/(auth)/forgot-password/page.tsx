"use client"

import { useState } from "react"
import Link from "next/link"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const forgotPasswordSchema = z.object({
  email: z.string().email("Email invalide"),
})

type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>

export default function ForgotPasswordPage() {
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const form = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  })

  async function onSubmit(values: ForgotPasswordFormValues) {
    setError(null)
    try {
      const res = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: values.email }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.message ?? "Une erreur est survenue. Réessayez.")
        return
      }

      setSuccess(true)
    } catch {
      setError("Erreur réseau. Réessayez.")
    }
  }

  return (
    <div className="w-full max-w-md">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Mot de passe oublié</h1>
        <p className="mt-2 text-sm text-gray-500">
          Entrez votre email pour recevoir un lien de réinitialisation
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8">
        {success ? (
          <div className="text-center space-y-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <p className="text-sm text-gray-700">
              Si cet email est associé à un compte, un lien de réinitialisation a été envoyé.
              Vérifiez votre boîte de réception.
            </p>
            <p className="text-xs text-gray-500">Le lien expire dans 30 minutes.</p>
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="vous@exemple.com" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {error && (
                <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
                  {error}
                </p>
              )}

              <Button
                type="submit"
                className="w-full bg-primary-600 hover:bg-primary-700"
                disabled={form.formState.isSubmitting}
              >
                {form.formState.isSubmitting ? "Envoi en cours…" : "Envoyer le lien"}
              </Button>
            </form>
          </Form>
        )}

        <p className="mt-6 text-center text-sm text-gray-500">
          <Link href="/login" className="font-medium text-primary-600 hover:text-primary-700">
            ← Retour à la connexion
          </Link>
        </p>
      </div>
    </div>
  )
}
