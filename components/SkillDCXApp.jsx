'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Wallet, 
  Award, 
  Bot, 
  Home, 
  Shield, 
  Sparkles,
  Github,
  ExternalLink
} from 'lucide-react'

import { ConnectWalletButton } from './ConnectWalletButton'
import { MyCertificates } from './MyCertificates'
import { SkillMentorAI } from './SkillMentorAI'
import { useWallet } from '@/hooks/useWallet'

export const SkillDCXApp = () => {
  const [activeTab, setActiveTab] = useState('home')
  const { isConnected, accountAddress, balance, areContractsDeployed } = useWallet()

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Shield className="h-8 w-8 text-primary" />
                <h1 className="text-2xl font-bold">SkillDCX</h1>
                <Badge variant="outline" className="text-xs">
                  v1.0 • TestNet
                </Badge>
              </div>
              <p className="hidden md:block text-muted-foreground">
                Decentralized Skill Certification on Algorand
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              {isConnected && areContractsDeployed() && (
                <Badge variant="secondary" className="hidden sm:flex">
                  <Shield className="h-3 w-3 mr-1" />
                  Contracts Deployed
                </Badge>
              )}
              <ConnectWalletButton />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          {/* Navigation */}
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="home" className="flex items-center gap-2">
              <Home className="h-4 w-4" />
              <span className="hidden sm:inline">Home</span>
            </TabsTrigger>
            <TabsTrigger value="certificates" className="flex items-center gap-2">
              <Award className="h-4 w-4" />
              <span className="hidden sm:inline">My Certificates</span>
            </TabsTrigger>
            <TabsTrigger value="mentor" className="flex items-center gap-2">
              <Bot className="h-4 w-4" />
              <span className="hidden sm:inline">AI Mentor</span>
            </TabsTrigger>
            <TabsTrigger value="about" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              <span className="hidden sm:inline">About</span>
            </TabsTrigger>
          </TabsList>

          {/* Home Tab */}
          <TabsContent value="home" className="space-y-6">
            {/* Hero Section */}
            <Card className="relative overflow-hidden border-dashed">
              <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-primary/5 to-transparent" />
              <CardHeader className="relative">
                <CardTitle className="text-3xl font-bold flex items-center gap-3">
                  <Shield className="h-8 w-8 text-primary" />
                  Welcome to SkillDCX
                  <Sparkles className="h-6 w-6 text-yellow-500" />
                </CardTitle>
                <CardDescription className="text-lg">
                  A decentralized platform for blockchain-verified skill certificates and AI-powered learning recommendations
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wallet className="h-5 w-5 text-blue-500" />
                    Wallet Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Connected:</span>
                      <Badge variant={isConnected ? 'default' : 'secondary'}>
                        {isConnected ? 'Yes' : 'No'}
                      </Badge>
                    </div>
                    {isConnected && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-sm">Balance:</span>
                          <span className="text-sm font-mono">{balance.toFixed(3)} ALGO</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Address:</span>
                          <span className="text-xs font-mono">
                            {accountAddress ? `${accountAddress.slice(0, 6)}...${accountAddress.slice(-4)}` : ''}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-green-500" />
                    Smart Contracts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Status:</span>
                      <Badge variant={areContractsDeployed() ? 'default' : 'secondary'}>
                        {areContractsDeployed() ? 'Deployed' : 'Not Found'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Network:</span>
                      <span className="text-sm">Algorand TestNet</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-purple-500" />
                    AI Features
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Course Recommendations:</span>
                      <Badge variant="default">Active</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Skill Analysis:</span>
                      <Badge variant="default">Available</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Get started with SkillDCX features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Button
                    variant="outline"
                    className="h-24 flex flex-col gap-2"
                    onClick={() => setActiveTab('certificates')}
                    disabled={!isConnected}
                  >
                    <Award className="h-6 w-6" />
                    <span className="text-sm">View Certificates</span>
                  </Button>
                  
                  <Button
                    variant="outline"
                    className="h-24 flex flex-col gap-2"
                    onClick={() => setActiveTab('mentor')}
                  >
                    <Bot className="h-6 w-6" />
                    <span className="text-sm">AI Mentor</span>
                  </Button>
                  
                  <Button
                    variant="outline"
                    className="h-24 flex flex-col gap-2"
                    asChild
                  >
                    <a href="https://testnet.algoexplorer.io/" target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-6 w-6" />
                      <span className="text-sm">Algo Explorer</span>
                    </a>
                  </Button>
                  
                  <Button
                    variant="outline"
                    className="h-24 flex flex-col gap-2"
                    asChild
                  >
                    <a href="https://github.com/yourusername/SkillDCX" target="_blank" rel="noopener noreferrer">
                      <Github className="h-6 w-6" />
                      <span className="text-sm">GitHub</span>
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Getting Started */}
            {!isConnected && (
              <Card className="border-dashed border-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wallet className="h-5 w-5" />
                    Getting Started
                  </CardTitle>
                  <CardDescription>
                    Connect your wallet to start using SkillDCX
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-sm text-muted-foreground space-y-2">
                    <p><strong>Step 1:</strong> Install Pera Wallet browser extension</p>
                    <p><strong>Step 2:</strong> Create or import your Algorand account</p>
                    <p><strong>Step 3:</strong> Get TestNet Algos from the faucet</p>
                    <p><strong>Step 4:</strong> Click "Connect Wallet" above</p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" asChild>
                      <a href="https://perawallet.app/" target="_blank" rel="noopener noreferrer">
                        Download Pera Wallet
                      </a>
                    </Button>
                    <Button variant="outline" asChild>
                      <a href="https://testnet.algoexplorer.io/dispenser" target="_blank" rel="noopener noreferrer">
                        Get TestNet Algos
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Certificates Tab */}
          <TabsContent value="certificates">
            <MyCertificates />
          </TabsContent>

          {/* AI Mentor Tab */}
          <TabsContent value="mentor">
            <SkillMentorAI />
          </TabsContent>

          {/* About Tab */}
          <TabsContent value="about" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5" />
                  About SkillDCX
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  SkillDCX is a decentralized platform built on Algorand that combines blockchain-verified 
                  skill certificates with AI-powered learning recommendations.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold mb-2">🔐 Blockchain Features</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Tamper-proof certificates</li>
                      <li>• IPFS content storage</li>
                      <li>• Smart contract verification</li>
                      <li>• Soulbound tokens (non-transferable)</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">🤖 AI Features</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Personalized course recommendations</li>
                      <li>• Skill progression analysis</li>
                      <li>• Career path suggestions</li>
                      <li>• Focus area matching</li>
                    </ul>
                  </div>
                </div>
                
                <div className="flex gap-2 pt-4">
                  <Button variant="outline" asChild>
                    <a href="https://github.com/yourusername/SkillDCX" target="_blank" rel="noopener noreferrer">
                      <Github className="mr-2 h-4 w-4" />
                      View Source
                    </a>
                  </Button>
                  <Button variant="outline" asChild>
                    <a href="/docs" target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Documentation
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">
                SkillDCX © 2024 - Built on Algorand
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <a href="https://algorand.org" target="_blank" rel="noopener noreferrer" 
                 className="hover:text-foreground transition-colors">
                Algorand
              </a>
              <a href="https://ipfs.io" target="_blank" rel="noopener noreferrer" 
                 className="hover:text-foreground transition-colors">
                IPFS
              </a>
              <a href="https://perawallet.app" target="_blank" rel="noopener noreferrer" 
                 className="hover:text-foreground transition-colors">
                Pera Wallet
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}