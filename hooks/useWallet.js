import { useState, useEffect, useCallback } from 'react'
import { PeraWalletConnect } from '@perawallet/connect'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create Pera Wallet instance
const peraWallet = new PeraWalletConnect({
  shouldShowSignTxnToast: true,
  chainId: 416002 // TestNet
})

export const useWallet = () => {
  const [accountAddress, setAccountAddress] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [balance, setBalance] = useState(0)
  const [error, setError] = useState(null)
  const [contracts, setContracts] = useState({})

  // Check if wallet is already connected on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const accounts = await peraWallet.reconnectSession()
        if (accounts.length > 0) {
          const address = accounts[0]
          setAccountAddress(address)
          await syncWithBackend(address)
        }
      } catch (error) {
        console.log('No existing session found')
      }
    }

    checkConnection()
  }, [])

  // Sync wallet connection with backend
  const syncWithBackend = async (address) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/wallet/connect`, {
        address: address
      })

      if (response.data.success) {
        setBalance(response.data.balance)
        setContracts(response.data.contracts)
        setIsConnected(true)
        setError(null)
      } else {
        throw new Error(response.data.message || 'Failed to sync with backend')
      }
    } catch (err) {
      console.error('Backend sync error:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to connect to backend')
    }
  }

  // Connect wallet
  const connectWallet = useCallback(async () => {
    setIsConnecting(true)
    setError(null)

    try {
      const newAccounts = await peraWallet.connect()
      
      if (newAccounts.length > 0) {
        const address = newAccounts[0]
        setAccountAddress(address)
        await syncWithBackend(address)
      }
    } catch (error) {
      console.error('Wallet connection error:', error)
      setError(error.message || 'Failed to connect wallet')
      setIsConnected(false)
    } finally {
      setIsConnecting(false)
    }
  }, [])

  // Disconnect wallet
  const disconnectWallet = useCallback(async () => {
    try {
      if (accountAddress) {
        // Notify backend
        await axios.post(`${API_BASE_URL}/wallet/disconnect`, {
          address: accountAddress
        })
      }

      // Disconnect from Pera Wallet
      peraWallet.disconnect()
      
      // Reset state
      setAccountAddress(null)
      setIsConnected(false)
      setBalance(0)
      setContracts({})
      setError(null)
    } catch (error) {
      console.error('Disconnect error:', error)
      setError('Failed to disconnect properly')
    }
  }, [accountAddress])

  // Refresh wallet status
  const refreshWallet = useCallback(async () => {
    if (!accountAddress) return

    try {
      const response = await axios.get(`${API_BASE_URL}/wallet/status/${accountAddress}`)
      
      if (response.data.connected) {
        setBalance(response.data.balance)
        setIsConnected(true)
      } else {
        setIsConnected(false)
      }
    } catch (error) {
      console.error('Refresh error:', error)
      setError('Failed to refresh wallet status')
    }
  }, [accountAddress])

  // Sign transaction (for future use)
  const signTransaction = useCallback(async (txnBytes) => {
    if (!accountAddress) {
      throw new Error('Wallet not connected')
    }

    try {
      const signedTxn = await peraWallet.signTransaction([txnBytes])
      return signedTxn
    } catch (error) {
      console.error('Transaction signing error:', error)
      throw error
    }
  }, [accountAddress])

  // Get formatted address (shortened)
  const getFormattedAddress = useCallback(() => {
    if (!accountAddress) return ''
    return `${accountAddress.slice(0, 8)}...${accountAddress.slice(-6)}`
  }, [accountAddress])

  // Check if contracts are deployed
  const areContractsDeployed = useCallback(() => {
    return contracts.certification_app_id && contracts.issuer_registry_app_id
  }, [contracts])

  return {
    // State
    accountAddress,
    isConnected,
    isConnecting,
    balance,
    error,
    contracts,

    // Actions
    connectWallet,
    disconnectWallet,
    refreshWallet,
    signTransaction,

    // Utils
    getFormattedAddress,
    areContractsDeployed,
    
    // Pera Wallet instance (for advanced usage)
    peraWallet
  }
}