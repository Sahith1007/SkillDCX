"use client"

import type React from "react"

import { useWallet } from "@/contexts/wallet-context"
import { ConnectWalletButton } from "@/components/ConnectWalletButton"
import { Wallet } from "lucide-react"

interface WalletGuardProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function WalletGuard({ children, fallback }: WalletGuardProps) {
  const { isConnected } = useWallet()

  if (isConnected) {
    return <>{children}</>
  }

  if (fallback) {
    return <>{fallback}</>
  }

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center space-y-6">
        <div className="space-y-2">
          <Wallet className="h-16 w-16 mx-auto text-muted-foreground" />
          <h1 className="text-3xl font-bold">Welcome to SkillDCX</h1>
          <p className="text-muted-foreground max-w-md">
            Connect your Pera Wallet to access your blockchain certificates and start managing your credentials.
          </p>
        </div>
        <ConnectWalletButton />
      </div>
    </div>
  )
}
