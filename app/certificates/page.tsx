"use client"

import { useState, useEffect, Key } from "react"
import { CertificateCard } from "@/components/certificate-card"
import { Input } from "@/components/ui/input"
import { Search, Award } from "lucide-react"
import { motion } from "framer-motion"
import { useCertificates } from "@/hooks/usecertificates" // your current hook

export default function CertificatesPage() {
  const { certificates, loading } = useCertificates() // fetches real data
  const [search, setSearch] = useState("")

  if (loading) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        Loading certificates...
      </div>
    )
  }

  if (!certificates || certificates.length === 0) {
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
            <h2 className="text-2xl font-semibold">No certificates yet</h2>
            <p className="text-muted-foreground max-w-md">
              You haven't received any certificates yet. Once institutions issue certificates to your wallet, they'll
              appear here.
            </p>
          </div>
        </div>
      </motion.div>
    )
  }

  // Filter certificates based on search input
  const filtered = certificates.filter(
    (cert: { title: string; issuer: string; date: string; status?: string }) =>
      cert.title.toLowerCase().includes(search.toLowerCase()) ||
      cert.issuer.toLowerCase().includes(search.toLowerCase()) ||
      cert.date.toLowerCase().includes(search.toLowerCase()) ||
      (cert.status ? cert.status.toLowerCase().includes(search.toLowerCase()) : false)
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-8"
    >
      <div className="space-y-8">
        <div className="space-y-4">
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
            View and manage your blockchain certificates. Total: {certificates.length}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="relative max-w-md"
          >
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-blue-400" />
            <Input
              placeholder="Search certificates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 backdrop-blur-sm bg-white/10 border-white/20 focus:border-blue-400/50 focus:ring-blue-400/20"
              aria-label="Search certificates"
            />
          </motion.div>
        </div>

        {filtered.length === 0 ? (
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
            {filtered.map((cert: { id: Key | null | undefined; title: string; issuer: string; date: string; status: string | undefined }, i: number) => (
              <motion.div
                key={cert.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * i }}
                whileHover={{ scale: 1.03 }}
              >
                <CertificateCard
                  name={cert.title}
                  issuer={cert.issuer}
                  issueDate={cert.date}
                  status={cert.status === "verified" ||
                    cert.status === "pending" ||
                    cert.status === "expired"
                    ? cert.status
                    : undefined} id={""}                />
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
