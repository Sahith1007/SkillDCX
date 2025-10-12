"use client"

import type React from "react"

import { useWallet } from "@/contexts/wallet-context"
import { Button } from "@/components/ui/button"
import { Wallet, Loader2 } from "lucide-react"

interface WalletGuardProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export function WalletGuard({ children, fallback }: WalletGuardProps) {
  const { isConnected, connectWallet, isLoading } = useWallet()

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
            Connect your wallet to access your blockchain certificates and start managing your credentials.
          </p>
        </div>
        <Button onClick={connectWallet} size="lg" className="px-8" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Connecting...
            </>
          ) : (
            "Connect Wallet"
          )}
        </Button>
      </div>
    </div>
  )
}
