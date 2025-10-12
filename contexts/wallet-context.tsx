"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"

interface WalletContextType {
  isConnected: boolean
  address: string | null
  connectWallet: () => Promise<void>
  disconnectWallet: () => void
  isLoading: boolean
  isAuthorizedIssuer: boolean
}

const WalletContext = createContext<WalletContextType | undefined>(undefined)

const AUTHORIZED_ISSUERS = [
  "0x12345678...abcd", // Example authorized issuer
  "0x87654321...efgh", // Another authorized issuer
  "0xabcdef12...ijkl", // Third authorized issuer
]

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false)
  const [address, setAddress] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isAuthorizedIssuer, setIsAuthorizedIssuer] = useState(false)

  useEffect(() => {
    const savedAddress = localStorage.getItem("wallet_address")
    if (savedAddress) {
      setIsConnected(true)
      setAddress(savedAddress)
      setIsAuthorizedIssuer(AUTHORIZED_ISSUERS.includes(savedAddress))
    }
  }, [])

  const connectWallet = async () => {
    setIsLoading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))

      const isIssuerDemo = Math.random() < 0.3
      const mockAddress = isIssuerDemo
        ? AUTHORIZED_ISSUERS[0]
        : "0x" + Math.random().toString(16).substr(2, 8) + "..." + Math.random().toString(16).substr(2, 4)

      setIsConnected(true)
      setAddress(mockAddress)
      setIsAuthorizedIssuer(AUTHORIZED_ISSUERS.includes(mockAddress))
      localStorage.setItem("wallet_address", mockAddress)
    } catch (error) {
      console.error("Failed to connect wallet:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const disconnectWallet = () => {
    setIsConnected(false)
    setAddress(null)
    setIsAuthorizedIssuer(false)
    localStorage.removeItem("wallet_address")
  }

  return (
    <WalletContext.Provider
      value={{
        isConnected,
        address,
        connectWallet,
        disconnectWallet,
        isLoading,
        isAuthorizedIssuer,
      }}
    >
      {children}
    </WalletContext.Provider>
  )
}

export function useWallet() {
  const context = useContext(WalletContext)
  if (context === undefined) {
    throw new Error("useWallet must be used within a WalletProvider")
  }
  return context
}
