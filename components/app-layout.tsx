"use client"

import type React from "react"

import { TopNav } from "@/components/top-nav"
import { WalletGuard } from "@/components/wallet-guard"

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="flex h-screen flex-col bg-background">
      <TopNav />
      <main className="flex-1 overflow-auto">
        <WalletGuard>{children}</WalletGuard>
      </main>
    </div>
  )
}
