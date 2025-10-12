"use client"

import { useState } from "react"
import { CertificateCard } from "@/components/certificate-card"
import { Input } from "@/components/ui/input"
import { Search, Award } from "lucide-react"
import { motion } from "framer-motion"

// Mock certificate data
const mockCertificates = [
  {
    id: "1",
    name: "Advanced React Development",
    issuer: "Tech University",
    issueDate: "2024-01-15",
    status: "verified" as const,
  },
  {
    id: "2",
    name: "Blockchain Fundamentals",
    issuer: "Crypto Institute",
    issueDate: "2024-02-20",
    status: "verified" as const,
  },
  {
    id: "3",
    name: "Smart Contract Development",
    issuer: "Web3 Academy",
    issueDate: "2024-03-10",
    status: "pending" as const,
  },
  {
    id: "4",
    name: "UI/UX Design Principles",
    issuer: "Design School",
    issueDate: "2023-12-05",
    status: "verified" as const,
  },
  {
    id: "5",
    name: "Project Management",
    issuer: "Business Institute",
    issueDate: "2024-01-30",
    status: "verified" as const,
  },
  {
    id: "6",
    name: "Data Science Basics",
    issuer: "Data University",
    issueDate: "2023-11-15",
    status: "expired" as const,
  },
]

export function CertificatesPage() {
  const [searchTerm, setSearchTerm] = useState("")

  const filteredCertificates = mockCertificates.filter(
    (cert) =>
      cert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cert.issuer.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  if (mockCertificates.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="p-8"
      >
        <div className="flex items-center justify-center h-96">
          <div className="text-center space-y-4">
            <Award className="h-16 w-16 mx-auto text-muted-foreground" />
            <div className="space-y-2">
              <h2 className="text-2xl font-semibold">No certificates yet</h2>
              <p className="text-muted-foreground max-w-md">
                You haven't received any certificates yet. Once institutions issue certificates to your wallet, they'll
                appear here.
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-8"
    >
      <div className="space-y-8">
        <div className="space-y-4">
          <div className="space-y-2">
            <motion.h1
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
            >
              My Certificates
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-muted-foreground text-lg"
            >
              View and manage your blockchain certificates. Total: {mockCertificates.length}
            </motion.p>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="relative max-w-md"
          >
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-blue-400" />
            <Input
              placeholder="Search certificates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 backdrop-blur-sm bg-white/10 border-white/20 focus:border-blue-400/50 focus:ring-blue-400/20"
            />
          </motion.div>
        </div>

        {/* Certificates Grid */}
        {filteredCertificates.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No certificates match your search.</p>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {filteredCertificates.map((certificate, index) => (
              <motion.div
                key={certificate.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * index }}
              >
                <CertificateCard {...certificate} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
