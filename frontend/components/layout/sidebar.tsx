"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState, type ElementType } from "react"
import {
  ArrowLeftRight,
  Bell,
  CreditCard,
  LayoutDashboard,
  Settings,
  Target,
  Upload,
} from "lucide-react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import type { ReceivedInvitationResponse } from "@/types/api"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/accounts", label: "Mes Comptes", icon: CreditCard },
  { href: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { href: "/budgets", label: "Budgets", icon: Target },
  { href: "/import", label: "Importer", icon: Upload },
  { href: "/invitations", label: "Invitations", icon: Bell, showBadge: true },
]

function usePendingCount(): number {
  const [count, setCount] = useState(0)
  useEffect(() => {
    fetch("/api/invitations")
      .then((r) => (r.ok ? r.json() : []))
      .then((data: ReceivedInvitationResponse[]) => {
        setCount(data.filter((inv) => inv.status === "pending").length)
      })
      .catch(() => {})
  }, [])
  return count
}

function NavItem({
  href,
  label,
  icon: Icon,
  showLabel,
  badgeCount,
}: {
  href: string
  label: string
  icon: ElementType
  showLabel: boolean
  badgeCount?: number
}) {
  const pathname = usePathname()
  const isActive = pathname === href || pathname.startsWith(`${href}/`)

  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-3 px-3 py-2.5 rounded-lg mx-2 transition-colors",
        "text-gray-300 hover:bg-gray-700 hover:text-white",
        isActive && "bg-primary-600 text-white hover:bg-primary-600",
      )}
    >
      <div className="relative shrink-0">
        <Icon className="size-5" />
        {badgeCount !== undefined && badgeCount > 0 && (
          <span className="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {badgeCount > 9 ? "9+" : badgeCount}
          </span>
        )}
      </div>
      <span
        className={cn(
          "text-sm font-medium whitespace-nowrap transition-opacity duration-200",
          showLabel ? "opacity-100" : "opacity-0 group-hover:opacity-100",
        )}
      >
        {label}
      </span>
    </Link>
  )
}

function UserNavItem({ showLabel }: { showLabel: boolean }) {
  return (
    <div className="flex items-center gap-3 px-3 py-2.5 mx-2">
      <Avatar className="size-8 shrink-0">
        <AvatarFallback className="bg-primary-600 text-white text-xs font-medium">
          U
        </AvatarFallback>
      </Avatar>
      <span
        className={cn(
          "text-sm text-gray-300 whitespace-nowrap transition-opacity duration-200",
          showLabel ? "opacity-100" : "opacity-0 group-hover:opacity-100",
        )}
      >
        Utilisateur
      </span>
    </div>
  )
}

function SidebarContent({ showLabel = false }: { showLabel?: boolean }) {
  const pendingCount = usePendingCount()

  return (
    <>
      {/* Logo */}
      <div className="flex items-center gap-3 px-3 py-4 h-16 shrink-0">
        <div className="size-8 bg-primary-600 rounded-lg shrink-0 flex items-center justify-center">
          <span className="text-white font-bold text-xs">BP</span>
        </div>
        <span
          className={cn(
            "text-white font-semibold text-lg whitespace-nowrap transition-opacity duration-200",
            showLabel ? "opacity-100" : "opacity-0 group-hover:opacity-100",
          )}
        >
          BankPulse
        </span>
      </div>

      <Separator className="bg-[#374151]" />

      {/* Navigation principale */}
      <nav className="flex-1 py-4 space-y-1">
        {navItems.map((item) => (
          <NavItem
            key={item.href}
            href={item.href}
            label={item.label}
            icon={item.icon}
            showLabel={showLabel}
            badgeCount={item.showBadge ? pendingCount : undefined}
          />
        ))}
      </nav>

      <Separator className="bg-[#374151]" />

      {/* Paramètres + User */}
      <div className="py-4 space-y-1">
        <NavItem href="/settings" label="Paramètres" icon={Settings} showLabel={showLabel} />
        <UserNavItem showLabel={showLabel} />
      </div>
    </>
  )
}

export function Sidebar() {
  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-50 h-screen w-16 overflow-hidden",
        "transition-all duration-200 hover:w-60 group",
        "bg-[#1f2937] border-r border-[#374151] flex flex-col",
      )}
    >
      <SidebarContent />
    </aside>
  )
}

export function MobileSidebar() {
  return (
    <div className="h-full w-60 bg-[#1f2937] flex flex-col">
      <SidebarContent showLabel />
    </div>
  )
}
