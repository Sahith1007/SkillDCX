"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ExternalLink, Calendar, Building } from "lucide-react"

interface CertificateCardProps {
  id: string
  name: string
  issuer: string
  issueDate: string
  ipfsUrl?: string
  status?: "verified" | "pending" | "expired"
}

export function CertificateCard({ id, name, issuer, issueDate, ipfsUrl, status = "verified" }: CertificateCardProps) {
  const handleViewCertificate = () => {
    if (ipfsUrl) {
      window.open(ipfsUrl, "_blank")
    } else {
      // Mock IPFS URL for demo
      window.open(`https://ipfs.io/ipfs/mock-hash-${id}`, "_blank")
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "verified":
        return "bg-green-500/20 text-green-400 border-green-500/30"
      case "pending":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      case "expired":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30"
    }
  }

  return (
    <Card className="backdrop-blur-sm bg-white/10 border border-white/20 hover:bg-white/20 transition-all duration-300 hover:scale-105 hover:shadow-2xl group">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold line-clamp-2 group-hover:text-blue-300 transition-colors">
            {name}
          </CardTitle>
          <Badge className={getStatusColor(status)} variant="outline">
            {status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground group-hover:text-blue-200 transition-colors">
            <Building className="h-4 w-4" />
            <span>{issuer}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground group-hover:text-blue-200 transition-colors">
            <Calendar className="h-4 w-4" />
            <span>{new Date(issueDate).toLocaleDateString()}</span>
          </div>
        </div>
        <Button
          onClick={handleViewCertificate}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0"
        >
          <ExternalLink className="mr-2 h-4 w-4" />
          View Certificate
        </Button>
      </CardContent>
    </Card>
  )
}
