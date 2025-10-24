'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { useWallet } from '@/hooks/useWallet'
import { Wallet, Copy, RefreshCw, LogOut, ExternalLink } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

export const ConnectWalletButton = () => {
  const {
    accountAddress,
    isConnected,
    isConnecting,
    balance,
    error,
    connectWallet,
    disconnectWallet,
    refreshWallet,
    getFormattedAddress,
    areContractsDeployed
  } = useWallet()

  const { toast } = useToast()

  const handleCopyAddress = async () => {
    if (accountAddress) {
      await navigator.clipboard.writeText(accountAddress)
      toast({
        title: 'Address Copied',
        description: 'Wallet address copied to clipboard',
      })
    }
  }

  const handleConnect = async () => {
    try {
      await connectWallet()
      toast({
        title: 'Wallet Connected',
        description: 'Successfully connected to Pera Wallet',
      })
    } catch (err) {
      toast({
        title: 'Connection Failed',
        description: err.message || 'Failed to connect wallet',
        variant: 'destructive'
      })
    }
  }

  const handleDisconnect = async () => {
    try {
      await disconnectWallet()
      toast({
        title: 'Wallet Disconnected',
        description: 'Successfully disconnected from wallet',
      })
    } catch (err) {
      toast({
        title: 'Disconnect Failed',
        description: err.message || 'Failed to disconnect wallet',
        variant: 'destructive'
      })
    }
  }

  const handleRefresh = async () => {
    try {
      await refreshWallet()
      toast({
        title: 'Wallet Refreshed',
        description: 'Wallet information updated',
      })
    } catch (err) {
      toast({
        title: 'Refresh Failed',
        description: err.message || 'Failed to refresh wallet',
        variant: 'destructive'
      })
    }
  }

  // Show error state
  if (error) {
    return (
      <div className="flex items-center gap-2">
        <Badge variant="destructive">Connection Error</Badge>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleConnect}
          disabled={isConnecting}
        >
          Retry
        </Button>
      </div>
    )
  }

  // Show connecting state
  if (isConnecting) {
    return (
      <Button variant="outline" disabled>
        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
        Connecting...
      </Button>
    )
  }

  // Show connected state
  if (isConnected && accountAddress) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className="flex items-center gap-2">
            <Wallet className="h-4 w-4" />
            <span className="font-mono">{getFormattedAddress()}</span>
            <Badge variant={balance > 0 ? 'success' : 'secondary'}>
              {balance.toFixed(3)} ALGO
            </Badge>
          </Button>
        </DropdownMenuTrigger>
        
        <DropdownMenuContent className="w-80" align="end">
          <DropdownMenuLabel className="flex flex-col gap-1">
            <span>Pera Wallet Connected</span>
            <span className="font-mono text-xs text-muted-foreground">
              {getFormattedAddress()}
            </span>
          </DropdownMenuLabel>
          
          <DropdownMenuSeparator />
          
          <div className="px-2 py-2">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted-foreground">Balance:</span>
              <span className="font-mono font-semibold">
                {balance.toFixed(6)} ALGO
              </span>
            </div>
            
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted-foreground">Network:</span>
              <Badge variant="outline">TestNet</Badge>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Contracts:</span>
              <Badge variant={areContractsDeployed() ? 'success' : 'secondary'}>
                {areContractsDeployed() ? 'Deployed' : 'Not Found'}
              </Badge>
            </div>
          </div>
          
          <DropdownMenuSeparator />
          
          <DropdownMenuItem onClick={handleCopyAddress}>
            <Copy className="mr-2 h-4 w-4" />
            Copy Address
          </DropdownMenuItem>
          
          <DropdownMenuItem onClick={handleRefresh}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh Balance
          </DropdownMenuItem>
          
          <DropdownMenuItem asChild>
            <a 
              href={`https://testnet.algoexplorer.io/address/${accountAddress}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center cursor-pointer"
            >
              <ExternalLink className="mr-2 h-4 w-4" />
              View on Explorer
            </a>
          </DropdownMenuItem>
          
          <DropdownMenuSeparator />
          
          <DropdownMenuItem 
            onClick={handleDisconnect}
            className="text-destructive focus:text-destructive"
          >
            <LogOut className="mr-2 h-4 w-4" />
            Disconnect
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    )
  }

  // Show connect button
  return (
    <Button onClick={handleConnect} className="flex items-center gap-2">
      <Wallet className="h-4 w-4" />
      🔗 Connect Wallet
    </Button>
  )
}