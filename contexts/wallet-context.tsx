"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import { PeraWalletConnect } from '@perawallet/connect'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create Pera Wallet instance
let peraWallet: PeraWalletConnect | null = null
if (typeof window !== 'undefined') {
  peraWallet = new PeraWalletConnect({
    shouldShowSignTxnToast: true,
    chainId: 416002 // TestNet
  })
}

interface WalletContextType {
  isConnected: boolean
  address: string | null
  balance: number
  connectWallet: () => Promise<void>
  disconnectWallet: () => void
  isLoading: boolean
  isAuthorizedIssuer: boolean
  contracts: any
  error: string | null
  refreshWallet: () => Promise<void>
}

const WalletContext = createContext<WalletContextType | undefined>(undefined)

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [isConnected, setIsConnected] = useState(false)
  const [address, setAddress] = useState<string | null>(null)
  const [balance, setBalance] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [isAuthorizedIssuer, setIsAuthorizedIssuer] = useState(false)
  const [contracts, setContracts] = useState<any>({})
  const [error, setError] = useState<string | null>(null)

  // Check if wallet is already connected on mount
  useEffect(() => {
    const checkConnection = async () => {
      if (!peraWallet) return
      
      try {
        const accounts = await peraWallet.reconnectSession()
        if (accounts.length > 0) {
          const walletAddress = accounts[0]
          setAddress(walletAddress)
          await syncWithBackend(walletAddress)
        }
      } catch (error) {
        console.log('No existing session found')
      }
    }

    checkConnection()
  }, [])

  // Sync wallet connection with backend
  const syncWithBackend = async (walletAddress: string) => {
    // Set connected state immediately - wallet is connected to Pera
    setIsConnected(true)
    
    try {
      const response = await axios.post(`${API_BASE_URL}/wallet/connect`, {
        address: walletAddress
      })

      if (response.data.success) {
        setBalance(response.data.balance)
        setContracts(response.data.contracts)
        setError(null)
        
        // Check if authorized issuer
        try {
          const issuerResponse = await axios.get(`${API_BASE_URL}/contracts/issuer/${walletAddress}/status`)
          setIsAuthorizedIssuer(issuerResponse.data.authorized || false)
        } catch (err) {
          console.log('Could not check issuer status:', err)
          setIsAuthorizedIssuer(false)
        }
      }
    } catch (err: any) {
      console.error('Backend sync error:', err)
      // Still keep wallet connected even if backend sync fails
      setError(err.response?.data?.detail || err.message || 'Backend connection issue (wallet still connected)')
    }
  }

  const connectWallet = async () => {
    if (!peraWallet) {
      setError('Pera Wallet not initialized')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const newAccounts = await peraWallet.connect()
      
      if (newAccounts.length > 0) {
        const walletAddress = newAccounts[0]
        setAddress(walletAddress)
        await syncWithBackend(walletAddress)
      }
    } catch (err: any) {
      console.error('Wallet connection error:', err)
      setError(err.message || 'Failed to connect wallet')
      setIsConnected(false)
    } finally {
      setIsLoading(false)
    }
  }

  const disconnectWallet = async () => {
    if (!peraWallet) return

    try {
      if (address) {
        // Notify backend
        await axios.post(`${API_BASE_URL}/wallet/disconnect`, {
          address: address
        })
      }

      // Disconnect from Pera Wallet
      peraWallet.disconnect()
      
      // Reset state
      setAddress(null)
      setIsConnected(false)
      setBalance(0)
      setContracts({})
      setError(null)
      setIsAuthorizedIssuer(false)
    } catch (err: any) {
      console.error('Disconnect error:', err)
      setError('Failed to disconnect properly')
    }
  }

  const refreshWallet = async () => {
    if (!address) return

    try {
      const response = await axios.get(`${API_BASE_URL}/wallet/status/${address}`)
      
      if (response.data.connected) {
        setBalance(response.data.balance)
        setIsConnected(true)
      } else {
        setIsConnected(false)
      }
    } catch (err: any) {
      console.error('Refresh error:', err)
      setError('Failed to refresh wallet status')
    }
  }

  return (
    <WalletContext.Provider
      value={{
        isConnected,
        address,
        balance,
        connectWallet,
        disconnectWallet,
        isLoading,
        isAuthorizedIssuer,
        contracts,
        error,
        refreshWallet,
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
