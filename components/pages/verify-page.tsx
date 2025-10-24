"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CertificateCard } from "@/components/certificate-card"
import { Search, Shield, AlertCircle, CheckCircle } from "lucide-react"
import axios from "axios"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Mock verification data
const mockVerificationData: Record<string, any[]> = {
  "0x1234...5678": [
    {
      id: "v1",
      name: "Advanced React Development",
      issuer: "Tech University",
      issueDate: "2024-01-15",
      status: "verified" as const,
    },
    {
      id: "v2",
      name: "Blockchain Fundamentals",
      issuer: "Crypto Institute",
      issueDate: "2024-02-20",
      status: "verified" as const,
    },
  ],
  "0xabcd...efgh": [
    {
      id: "v3",
      name: "Smart Contract Development",
      issuer: "Web3 Academy",
      issueDate: "2024-03-10",
      status: "verified" as const,
    },
  ],
}

export function VerifyPage() {
  const [searchType, setSearchType] = useState<'address' | 'ipfs'>('ipfs')
  const [searchInput, setSearchInput] = useState("")
  const [verificationResult, setVerificationResult] = useState<any>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchInput.trim()) return

    setIsSearching(true)
    setHasSearched(true)
    setError(null)
    setVerificationResult(null)

    try {
      if (searchType === 'ipfs') {
        // Verify by IPFS hash
        const response = await axios.get(`${API_BASE_URL}/verify/certificate/${searchInput.trim()}`)
        setVerificationResult({
          status: 'verified',
          data: response.data.data,
          ipfsHash: searchInput.trim()
        })
      } else {
        // Search by wallet address (mock for now)
        const results = mockVerificationData[searchInput] || []
        setVerificationResult({
          status: results.length > 0 ? 'found' : 'not_found',
          certificates: results
        })
      }
    } catch (err: any) {
      console.error('Verification error:', err)
      setError(err.response?.data?.detail || 'Failed to verify certificate. Please check the IPFS hash and try again.')
    } finally {
      setIsSearching(false)
    }
  }

  const handleClearSearch = () => {
    setSearchInput("")
    setVerificationResult(null)
    setHasSearched(false)
    setError(null)
  }

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold">Verify Certificates</h1>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Enter a wallet address to verify and view all certificates associated with that address. All certificates
            are stored on the blockchain for transparent verification.
          </p>
        </div>

        {/* Search Form */}
        <Card>
          <CardHeader>
            <CardTitle>Verify Certificate</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="space-y-2">
                <Label>Verification Method</Label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={searchType === 'ipfs'}
                      onChange={() => setSearchType('ipfs')}
                      className="cursor-pointer"
                    />
                    <span>IPFS Hash</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={searchType === 'address'}
                      onChange={() => setSearchType('address')}
                      className="cursor-pointer"
                    />
                    <span>Wallet Address</span>
                  </label>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="searchInput">
                  {searchType === 'ipfs' ? 'IPFS Hash' : 'Wallet Address'}
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="searchInput"
                    placeholder={searchType === 'ipfs' ? 'Qm...' : '0x...'}
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    className="flex-1"
                  />
                  <Button type="submit" disabled={isSearching || !searchInput.trim()}>
                    {isSearching ? (
                      <>
                        <Search className="mr-2 h-4 w-4 animate-spin" />
                        Verifying...
                      </>
                    ) : (
                      <>
                        <Search className="mr-2 h-4 w-4" />
                        Verify
                      </>
                    )}
                  </Button>
                  {hasSearched && (
                    <Button type="button" variant="outline" onClick={handleClearSearch}>
                      Clear
                    </Button>
                  )}
                </div>
              </div>
              {searchType === 'address' && (
                <div className="text-sm text-muted-foreground">
                  <p>Try these sample addresses:</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    <button
                      type="button"
                      onClick={() => setSearchInput("0x1234...5678")}
                      className="text-primary hover:underline"
                    >
                      0x1234...5678
                    </button>
                    <span>•</span>
                    <button
                      type="button"
                      onClick={() => setSearchInput("0xabcd...efgh")}
                      className="text-primary hover:underline"
                    >
                      0xabcd...efgh
                    </button>
                  </div>
                </div>
              )}
            </form>
          </CardContent>
        </Card>

        {/* Error Message */}
        {error && (
          <Card className="border-red-500/50 bg-red-500/10">
            <CardContent className="flex items-start gap-3 pt-6">
              <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-500 mb-1">Verification Failed</h3>
                <p className="text-sm text-red-400">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Verification Results */}
        {hasSearched && verificationResult && !error && (
          <div className="space-y-6">
            {searchType === 'ipfs' && verificationResult.status === 'verified' ? (
              <Card className="border-green-500/50 bg-green-500/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-600 dark:text-green-400">
                    <CheckCircle className="h-6 w-6" />
                    Certificate Verified Successfully
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-sm text-muted-foreground mb-2">Certificate Details:</h3>
                    <div className="bg-background/50 rounded-lg p-4 space-y-2">
                      <div>
                        <span className="text-sm font-medium">Certificate ID:</span>
                        <p className="text-sm text-muted-foreground">{verificationResult.data.id}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Student ID:</span>
                        <p className="text-sm text-muted-foreground">{verificationResult.data.student_id}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Course:</span>
                        <p className="text-sm text-muted-foreground">{verificationResult.data.course}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">Grade:</span>
                        <p className="text-sm text-muted-foreground">{verificationResult.data.grade}</p>
                      </div>
                      <div>
                        <span className="text-sm font-medium">IPFS Hash:</span>
                        <p className="text-sm text-muted-foreground font-mono break-all">{verificationResult.ipfsHash}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button asChild variant="outline" className="flex-1">
                      <a
                        href={`https://gateway.pinata.cloud/ipfs/${verificationResult.ipfsHash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        View on IPFS
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : searchType === 'address' ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-semibold">Certificates for {searchInput}</h2>
                  <div className="text-sm text-muted-foreground">
                    {verificationResult.certificates?.length || 0} certificate{verificationResult.certificates?.length !== 1 ? "s" : ""} found
                  </div>
                </div>

                {!verificationResult.certificates || verificationResult.certificates.length === 0 ? (
                  <Card className="border-dashed">
                    <CardContent className="flex flex-col items-center justify-center py-12">
                      <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No certificates found</h3>
                      <p className="text-muted-foreground text-center max-w-md">
                        No certificates were found for this wallet address. The address may not have received any
                        certificates yet, or it may not exist.
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {verificationResult.certificates.map((certificate: any) => (
                      <CertificateCard key={certificate.id} {...certificate} />
                    ))}
                  </div>
                )}
              </div>
            ) : null}
          </div>
        )}

        {/* Info Card */}
        <Card className="bg-muted/50">
          <CardContent className="pt-6">
            <div className="text-sm text-muted-foreground space-y-2">
              <h3 className="font-semibold text-foreground">How Verification Works</h3>
              <ul className="space-y-1 list-disc list-inside">
                <li>All certificates are stored on the blockchain for immutable verification</li>
                <li>Enter any wallet address to see all certificates associated with it</li>
                <li>Certificate authenticity is guaranteed by blockchain technology</li>
                <li>Click "View Certificate" to access the original document on IPFS</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
