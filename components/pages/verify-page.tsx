"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CertificateCard } from "@/components/certificate-card"
import { Search, Shield, AlertCircle } from "lucide-react"

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
  const [searchAddress, setSearchAddress] = useState("")
  const [searchResults, setSearchResults] = useState<any[] | null>(null)
  const [isSearching, setIsSearching] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchAddress.trim()) return

    setIsSearching(true)
    setHasSearched(true)

    // Mock search delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Check if address exists in mock data
    const results = mockVerificationData[searchAddress] || []
    setSearchResults(results)
    setIsSearching(false)
  }

  const handleClearSearch = () => {
    setSearchAddress("")
    setSearchResults(null)
    setHasSearched(false)
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
            <CardTitle>Search by Wallet Address</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="searchAddress">Wallet Address</Label>
                <div className="flex gap-2">
                  <Input
                    id="searchAddress"
                    placeholder="0x..."
                    value={searchAddress}
                    onChange={(e) => setSearchAddress(e.target.value)}
                    className="flex-1"
                  />
                  <Button type="submit" disabled={isSearching || !searchAddress.trim()}>
                    {isSearching ? (
                      <>
                        <Search className="mr-2 h-4 w-4 animate-spin" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <Search className="mr-2 h-4 w-4" />
                        Search
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
              <div className="text-sm text-muted-foreground">
                <p>Try these sample addresses:</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  <button
                    type="button"
                    onClick={() => setSearchAddress("0x1234...5678")}
                    className="text-primary hover:underline"
                  >
                    0x1234...5678
                  </button>
                  <span>•</span>
                  <button
                    type="button"
                    onClick={() => setSearchAddress("0xabcd...efgh")}
                    className="text-primary hover:underline"
                  >
                    0xabcd...efgh
                  </button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Search Results */}
        {hasSearched && searchResults !== null && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold">Certificates for {searchAddress}</h2>
              <div className="text-sm text-muted-foreground">
                {searchResults.length} certificate{searchResults.length !== 1 ? "s" : ""} found
              </div>
            </div>

            {searchResults.length === 0 ? (
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
                {searchResults.map((certificate) => (
                  <CertificateCard key={certificate.id} {...certificate} />
                ))}
              </div>
            )}
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
