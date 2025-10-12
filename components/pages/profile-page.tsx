"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useWallet } from "@/contexts/wallet-context"
import { User, Wallet, Award, FileText, LogOut, Copy, Check } from "lucide-react"
import { useState } from "react"

export function ProfilePage() {
  const { address, disconnectWallet } = useWallet()
  const [copied, setCopied] = useState(false)

  const handleCopyAddress = async () => {
    if (address) {
      await navigator.clipboard.writeText(address)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDisconnect = () => {
    disconnectWallet()
  }

  // Mock user stats
  const userStats = {
    certificatesOwned: 12,
    certificatesIssued: 24,
    joinDate: "January 2024",
    lastActivity: "2 hours ago",
  }

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <User className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold">Profile</h1>
          </div>
          <p className="text-muted-foreground">Manage your wallet connection and view your certificate statistics</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Wallet Info */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wallet className="h-5 w-5" />
                  Connected Wallet
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Wallet Address</span>
                    <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">
                      Connected
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                    <code className="flex-1 text-sm font-mono">{address}</code>
                    <Button size="sm" variant="ghost" onClick={handleCopyAddress}>
                      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4">
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Member Since</p>
                    <p className="text-sm text-muted-foreground">{userStats.joinDate}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Last Activity</p>
                    <p className="text-sm text-muted-foreground">{userStats.lastActivity}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Disconnect Wallet */}
            <Card className="border-destructive/20">
              <CardHeader>
                <CardTitle className="text-destructive">Disconnect Wallet</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  Disconnecting your wallet will log you out and you'll need to reconnect to access your certificates.
                </p>
                <Button variant="destructive" onClick={handleDisconnect} className="w-full sm:w-auto">
                  <LogOut className="mr-2 h-4 w-4" />
                  Disconnect Wallet
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Stats Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Award className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Certificates Owned</span>
                  </div>
                  <span className="font-semibold">{userStats.certificatesOwned}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Certificates Issued</span>
                  </div>
                  <span className="font-semibold">{userStats.certificatesIssued}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-muted/50">
              <CardContent className="pt-6">
                <div className="text-sm text-muted-foreground space-y-2">
                  <h3 className="font-semibold text-foreground">Account Security</h3>
                  <ul className="space-y-1 text-xs">
                    <li>• Your wallet is your identity</li>
                    <li>• Keep your private keys secure</li>
                    <li>• Never share your seed phrase</li>
                    <li>• Verify all transactions</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
