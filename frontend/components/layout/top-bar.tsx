"use client"

import { usePathname } from "next/navigation"
import { ChevronDownIcon, LogOutIcon, MenuIcon, UserIcon } from "lucide-react"

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
import { useUser } from "@/hooks/useUser"

const routeLabels: Record<string, string> = {
  dashboard: "Dashboard",
  accounts: "Mes Comptes",
  transactions: "Transactions",
  budgets: "Budgets",
  settings: "Paramètres",
  import: "Importer",
  invitations: "Invitations",
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
  const { user } = useUser()

  const initials = user
    ? user.first_name && user.last_name
      ? `${user.first_name[0]}${user.last_name[0]}`.toUpperCase()
      : user.email.slice(0, 2).toUpperCase()
    : "…"

  const displayName =
    user?.first_name || user?.last_name
      ? `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim()
      : user?.email ?? ""

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex items-center gap-2 h-auto px-2 py-1 rounded-lg"
        >
          <Avatar className="size-8 shrink-0">
            <AvatarFallback className="bg-primary-600 text-white text-xs font-medium">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="hidden sm:flex flex-col items-start text-left max-w-[160px]">
            <span className="text-sm font-medium text-gray-900 leading-tight truncate w-full">
              {displayName}
            </span>
            <span className="text-xs text-gray-500 leading-tight truncate w-full">
              {user?.email}
            </span>
          </div>
          <ChevronDownIcon className="size-4 text-gray-400 hidden sm:block shrink-0" />
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
