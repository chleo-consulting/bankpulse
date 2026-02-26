"use client"

import { useState } from "react"

import { MobileSidebar, Sidebar } from "@/components/layout/sidebar"
import { TopBar } from "@/components/layout/top-bar"
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet"
import { VisuallyHidden } from "radix-ui"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar desktop — fixée à gauche, expand au hover */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Sidebar mobile — Sheet overlay */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent
          side="left"
          className="p-0 w-60 bg-[#1f2937] border-r border-[#374151]"
          showCloseButton={false}
        >
          <VisuallyHidden.Root>
            <SheetTitle>Navigation</SheetTitle>
          </VisuallyHidden.Root>
          <MobileSidebar />
        </SheetContent>
      </Sheet>

      {/* Contenu principal */}
      <div className="flex-1 lg:ml-16 flex flex-col min-h-screen">
        <TopBar onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}
