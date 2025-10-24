'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { 
  Award, 
  Shield, 
  ExternalLink, 
  Download, 
  Eye, 
  Clock, 
  User, 
  Hash,
  RefreshCw,
  AlertCircle,
  CheckCircle2
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useWallet } from '@/hooks/useWallet'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const MyCertificates = () => {
  const [certificates, setCertificates] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasLoaded, setHasLoaded] = useState(false)
  const { accountAddress, isConnected } = useWallet()
  const { toast } = useToast()

  // Load certificates when wallet connects
  useEffect(() => {
    if (isConnected && accountAddress && !hasLoaded) {
      loadCertificates()
    }
  }, [isConnected, accountAddress, hasLoaded])

  const loadCertificates = async () => {
    if (!accountAddress) return

    setIsLoading(true)
    try {
      const response = await axios.get(`${API_BASE_URL}/contracts/certificates/${accountAddress}`)
      
      if (response.data.success) {
        setCertificates(response.data.certificates || [])
        setHasLoaded(true)
        
        toast({
          title: 'Certificates Loaded',
          description: `Found ${response.data.certificates?.length || 0} certificates`,
        })
      } else {
        throw new Error(response.data.message || 'Failed to load certificates')
      }
    } catch (error) {
      console.error('Error loading certificates:', error)
      
      let errorMessage = 'Failed to load certificates'
      
      if (error.response?.status === 503) {
        errorMessage = 'Smart contracts not deployed yet. Please deploy the contracts first.'
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.message) {
        errorMessage = error.message
      }
      
      toast({
        title: 'Loading Failed',
        description: errorMessage,
        variant: 'destructive'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const verifyCertificate = async (certificate) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/contracts/verify`, {
        certificate_holder: accountAddress,
        expected_ipfs_hash: certificate.certificate_data.ipfs_hash
      })

      if (response.data.success) {
        toast({
          title: 'Certificate Verified ✓',
          description: 'Certificate is authentic and valid',
        })
      } else {
        toast({
          title: 'Verification Failed',
          description: response.data.message || 'Certificate could not be verified',
          variant: 'destructive'
        })
      }
    } catch (error) {
      console.error('Verification error:', error)
      toast({
        title: 'Verification Error',
        description: error.response?.data?.detail || 'Failed to verify certificate',
        variant: 'destructive'
      })
    }
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown'
    const date = new Date(timestamp * 1000) // Convert Unix timestamp to JS Date
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  const formatAddress = (address) => {
    if (!address) return ''
    return `${address.slice(0, 8)}...${address.slice(-6)}`
  }

  // Show wallet connection prompt
  if (!isConnected) {
    return (
      <div className="min-h-[400px] flex flex-col items-center justify-center">
        <div className="text-center space-y-4">
          <Award className="h-16 w-16 mx-auto text-muted-foreground" />
          <h3 className="text-xl font-semibold">Connect Your Wallet</h3>
          <p className="text-muted-foreground max-w-md">
            Connect your Pera Wallet to view your blockchain certificates and credentials.
          </p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            Refresh Page
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-dashed">
        <CardHeader className="text-center">
          <CardTitle className="flex items-center justify-center gap-2">
            <Award className="h-6 w-6 text-primary" />
            My Certificates
            <Shield className="h-5 w-5 text-green-600" />
          </CardTitle>
          <CardDescription>
            View and verify your blockchain-secured certificates stored on Algorand
          </CardDescription>
          {accountAddress && (
            <div className="mt-2">
              <Badge variant="outline" className="font-mono">
                {formatAddress(accountAddress)}
              </Badge>
            </div>
          )}
        </CardHeader>
      </Card>

      {/* Actions */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <Button 
              onClick={loadCertificates} 
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  Refresh Certificates
                </>
              )}
            </Button>
            
            <Button variant="outline" asChild>
              <a 
                href={`https://testnet.algoexplorer.io/address/${accountAddress}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2"
              >
                <ExternalLink className="h-4 w-4" />
                View on Explorer
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Certificates List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Certificates
            {certificates.length > 0 && (
              <Badge variant="secondary">{certificates.length} found</Badge>
            )}
          </CardTitle>
          <CardDescription>
            Blockchain-verified credentials and achievements
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!hasLoaded ? (
            <div className="text-center py-8">
              <RefreshCw className="h-8 w-8 mx-auto text-muted-foreground animate-spin mb-4" />
              <p className="text-muted-foreground">Loading certificates...</p>
            </div>
          ) : certificates.length === 0 ? (
            <div className="text-center py-12">
              <Award className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
              <h4 className="text-lg font-semibold mb-2">No Certificates Found</h4>
              <p className="text-muted-foreground max-w-md mx-auto mb-4">
                You don't have any blockchain certificates yet. Complete courses or achievements 
                from authorized issuers to receive your first certificate.
              </p>
              <div className="flex gap-2 justify-center">
                <Button variant="outline" onClick={loadCertificates}>
                  Check Again
                </Button>
                <Button variant="outline">
                  Learn More
                </Button>
              </div>
            </div>
          ) : (
            <ScrollArea className="h-[600px] pr-4">
              <div className="space-y-4">
                {certificates.map((cert, index) => (
                  <Card key={index} className="hover:shadow-md transition-shadow">
                    <CardContent className="pt-6">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold text-lg">Certificate #{cert.id}</h4>
                            <Badge 
                              variant={cert.certificate_data.active === 1 ? 'default' : 'destructive'}
                            >
                              {cert.certificate_data.active === 1 ? 'Active' : 'Revoked'}
                            </Badge>
                          </div>
                          
                          {cert.certificate_data.metadata && (
                            <p className="text-sm text-muted-foreground mb-2">
                              {cert.certificate_data.metadata}
                            </p>
                          )}
                        </div>
                        
                        <div className="flex flex-col gap-2">
                          <Badge variant="outline">
                            App ID: {cert.contract_app_id}
                          </Badge>
                        </div>
                      </div>

                      <Separator className="my-4" />

                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm font-medium">Issuer</span>
                          </div>
                          <p className="text-sm font-mono text-muted-foreground">
                            {formatAddress(cert.certificate_data.issuer)}
                          </p>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm font-medium">Issued</span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {formatTimestamp(cert.certificate_data.timestamp)}
                          </p>
                        </div>
                        
                        <div className="space-y-2 col-span-2">
                          <div className="flex items-center gap-2">
                            <Hash className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm font-medium">IPFS Hash</span>
                          </div>
                          <p className="text-sm font-mono text-muted-foreground break-all">
                            {cert.certificate_data.ipfs_hash}
                          </p>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => verifyCertificate(cert)}
                          className="flex items-center gap-2"
                        >
                          <CheckCircle2 className="h-4 w-4" />
                          Verify
                        </Button>
                        
                        <Button 
                          variant="outline" 
                          size="sm" 
                          asChild
                        >
                          <a 
                            href={`https://ipfs.io/ipfs/${cert.certificate_data.ipfs_hash}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2"
                          >
                            <Eye className="h-4 w-4" />
                            View Content
                          </a>
                        </Button>
                        
                        <Button 
                          variant="outline" 
                          size="sm" 
                          asChild
                        >
                          <a 
                            href={`https://testnet.algoexplorer.io/application/${cert.contract_app_id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2"
                          >
                            <ExternalLink className="h-4 w-4" />
                            Contract
                          </a>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>
    </div>
  )
}