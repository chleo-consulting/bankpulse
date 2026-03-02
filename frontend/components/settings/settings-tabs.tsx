"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { PasswordInput } from "@/components/ui/password-input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"

type Tab = "profile" | "security" | "about"

const tabs: { id: Tab; label: string }[] = [
  { id: "profile", label: "Mon Profil" },
  { id: "security", label: "Sécurité" },
  { id: "about", label: "À propos" },
]

export function SettingsTabs() {
  const [activeTab, setActiveTab] = useState<Tab>("profile")

  return (
    <div className="space-y-6">
      {/* Tab navigation */}
      <div className="flex gap-1 border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={[
              "px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px",
              activeTab === tab.id
                ? "border-primary-600 text-primary-600"
                : "border-transparent text-gray-500 hover:text-gray-700",
            ].join(" ")}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Profile tab */}
      {activeTab === "profile" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base">Mon Profil</CardTitle>
                <CardDescription>Informations personnelles de votre compte</CardDescription>
              </div>
              <Badge variant="secondary">Bientôt disponible</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="first_name">Prénom</Label>
                <Input id="first_name" placeholder="John" disabled />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="last_name">Nom</Label>
                <Input id="last_name" placeholder="Doe" disabled />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="john@acme.com"
                disabled
                className="bg-gray-50"
              />
              <p className="text-xs text-gray-500">
                L&apos;adresse email n&apos;est pas modifiable.
              </p>
            </div>
            <Button disabled className="w-full sm:w-auto">
              Enregistrer les modifications
            </Button>
            <p className="text-xs text-gray-400">
              La mise à jour du profil sera disponible dans une prochaine version.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Security tab */}
      {activeTab === "security" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base">Sécurité</CardTitle>
                <CardDescription>Gérez votre mot de passe</CardDescription>
              </div>
              <Badge variant="secondary">Bientôt disponible</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="current_password">Mot de passe actuel</Label>
              <PasswordInput id="current_password" disabled placeholder="••••••••" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="new_password">Nouveau mot de passe</Label>
              <PasswordInput id="new_password" disabled placeholder="••••••••" />
              <p className="text-xs text-gray-500">Minimum 8 caractères.</p>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="confirm_password">Confirmer le nouveau mot de passe</Label>
              <PasswordInput id="confirm_password" disabled placeholder="••••••••" />
            </div>
            <Button disabled variant="outline" className="w-full sm:w-auto">
              Changer le mot de passe
            </Button>
            <p className="text-xs text-gray-400">
              Le changement de mot de passe sera disponible dans une prochaine version.
            </p>
          </CardContent>
        </Card>
      )}

      {/* About tab */}
      {activeTab === "about" && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">BankPulse</CardTitle>
              <CardDescription>Application d&apos;analyse financière personnelle</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Version</span>
                <span className="font-mono font-medium">v1.0.0 (Beta)</span>
              </div>
              <Separator />
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Frontend</span>
                <span className="font-mono text-xs text-gray-600">
                  Next.js 16 · shadcn/ui v3 · Tailwind v4
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Backend</span>
                <span className="font-mono text-xs text-gray-600">
                  FastAPI · SQLAlchemy 2.0 · PostgreSQL
                </span>
              </div>
              <Separator />
              <div className="text-xs text-gray-400 text-center pt-2">
                Phase 1 MVP — données 100% locales, aucun partage avec des tiers.
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
