"use client"

import { usePathname } from "next/navigation"
import { LogOutIcon, MenuIcon, UserIcon } from "lucide-react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useAuth } from "@/hooks/useAuth"

const routeLabels: Record<string, string> = {
  dashboard: "Dashboard",
  accounts: "Mes Comptes",
  transactions: "Transactions",
  budgets: "Budgets",
  settings: "Paramètres",
  import: "Importer",
}

function Breadcrumbs() {
  const pathname = usePathname()
  const segments = pathname.split("/").filter(Boolean)
  const labels = segments.map((seg) => routeLabels[seg] ?? seg)

  return (
    <div className="flex items-center gap-2 text-sm">
      {labels.map((label, i) => (
        <span key={i} className="flex items-center gap-2">
          {i > 0 && <span className="text-gray-400">/</span>}
          <span
            className={
              i === labels.length - 1 ? "font-medium text-gray-900" : "text-gray-500"
            }
          >
            {label}
          </span>
        </span>
      ))}
    </div>
  )
}

function UserMenu() {
  const { logout, isLoggingOut } = useAuth()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-8 w-8 rounded-full p-0">
          <Avatar className="size-8">
            <AvatarFallback className="bg-primary-600 text-white text-xs font-medium">
              U
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem>
          <UserIcon className="size-4" />
          Profil
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onClick={logout} disabled={isLoggingOut}>
          <LogOutIcon className="size-4" />
          {isLoggingOut ? "Déconnexion…" : "Déconnexion"}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

interface TopBarProps {
  onMenuClick: () => void
}

export function TopBar({ onMenuClick }: TopBarProps) {
  return (
    <header className="sticky top-0 z-40 h-16 flex items-center justify-between px-6 bg-white border-b border-gray-200">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
        >
          <MenuIcon className="size-5" />
        </Button>
        <Breadcrumbs />
      </div>
      <UserMenu />
    </header>
  )
}
