"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, Shield } from "lucide-react"
import { useWallet } from "@/contexts/wallet-context"
import { motion } from "framer-motion"

export function IssueCertificatePage() {
  const { address, isAuthorizedIssuer } = useWallet()
  const [formData, setFormData] = useState({
    recipientAddress: "",
    certificateName: "",
    unitName: "",
    file: null as File | null,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<"idle" | "success" | "error">("idle")
  const [message, setMessage] = useState("")

  if (!isAuthorizedIssuer) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="p-8"
      >
        <div className="max-w-2xl mx-auto space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-center space-y-2"
          >
            <h1 className="text-4xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
              Access Denied
            </h1>
            <p className="text-muted-foreground text-lg">You don't have permission to access this page</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card className="backdrop-blur-sm bg-red-500/10 border border-red-500/30">
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <Shield className="h-16 w-16 mx-auto text-red-400" />
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold text-red-300">Authorization Required</h3>
                    <p className="text-red-200">Only authorized institutions can issue certificates.</p>
                    <p className="text-sm text-muted-foreground">
                      If you believe you should have access, please contact your administrator.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </motion.div>
    )
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setFormData((prev) => ({ ...prev, file }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitStatus("idle")

    try {
      // Mock certificate issuance
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Simulate success/error randomly for demo
      const success = Math.random() > 0.2

      if (success) {
        setSubmitStatus("success")
        setMessage("Certificate issued successfully! Transaction hash: 0x1234...5678")
        setFormData({
          recipientAddress: "",
          certificateName: "",
          unitName: "",
          file: null,
        })
      } else {
        setSubmitStatus("error")
        setMessage("Failed to issue certificate. Please try again.")
      }
    } catch (error) {
      setSubmitStatus("error")
      setMessage("An error occurred while issuing the certificate.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const isFormValid =
    formData.recipientAddress &&
    formData.certificateName &&
    formData.unitName &&
    formData.file &&
    formData.recipientAddress.startsWith("0x")

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="p-8"
    >
      <div className="max-w-2xl mx-auto space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-center space-y-2"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Issue Certificate
          </h1>
          <p className="text-muted-foreground text-lg">Create and issue a new blockchain certificate to a recipient</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <Card className="backdrop-blur-sm bg-white/10 border border-white/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-300">
                <FileText className="h-5 w-5" />
                Certificate Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Recipient Address */}
                <div className="space-y-2">
                  <Label htmlFor="recipientAddress" className="text-blue-200">
                    Recipient Wallet Address
                  </Label>
                  <Input
                    id="recipientAddress"
                    placeholder="0x..."
                    value={formData.recipientAddress}
                    onChange={(e) => handleInputChange("recipientAddress", e.target.value)}
                    className="backdrop-blur-sm bg-white/10 border-white/20 focus:border-blue-400/50 focus:ring-blue-400/20"
                    required
                  />
                </div>

                {/* Certificate Name */}
                <div className="space-y-2">
                  <Label htmlFor="certificateName" className="text-blue-200">
                    Certificate Name
                  </Label>
                  <Input
                    id="certificateName"
                    placeholder="e.g., Advanced React Development"
                    value={formData.certificateName}
                    onChange={(e) => handleInputChange("certificateName", e.target.value)}
                    className="backdrop-blur-sm bg-white/10 border-white/20 focus:border-blue-400/50 focus:ring-blue-400/20"
                    required
                  />
                </div>

                {/* Unit Name */}
                <div className="space-y-2">
                  <Label htmlFor="unitName" className="text-blue-200">
                    Unit/Institution Name
                  </Label>
                  <Input
                    id="unitName"
                    placeholder="e.g., Tech University"
                    value={formData.unitName}
                    onChange={(e) => handleInputChange("unitName", e.target.value)}
                    className="backdrop-blur-sm bg-white/10 border-white/20 focus:border-blue-400/50 focus:ring-blue-400/20"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="certificateFile" className="text-blue-200">
                    Upload Certificate File
                  </Label>
                  <div className="border-2 border-dashed border-white/30 backdrop-blur-sm bg-white/5 rounded-lg p-6 text-center hover:border-blue-400/50 hover:bg-white/10 transition-all duration-300">
                    <input
                      id="certificateFile"
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg"
                      onChange={handleFileChange}
                      className="hidden"
                      required
                    />
                    <label htmlFor="certificateFile" className="cursor-pointer">
                      <Upload className="h-8 w-8 mx-auto mb-2 text-blue-400" />
                      <p className="text-sm text-blue-200">
                        {formData.file ? formData.file.name : "Click to upload certificate file"}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">PDF, PNG, JPG up to 10MB</p>
                    </label>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-0 py-3 text-lg font-semibold"
                  disabled={!isFormValid || isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Issuing Certificate...
                    </>
                  ) : (
                    "Issue Certificate"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>

        {/* Status Messages */}
        {submitStatus === "success" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Alert className="border-green-500/30 bg-green-500/20 backdrop-blur-sm">
              <CheckCircle className="h-4 w-4 text-green-400" />
              <AlertDescription className="text-green-300">{message}</AlertDescription>
            </Alert>
          </motion.div>
        )}

        {submitStatus === "error" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Alert className="border-red-500/30 bg-red-500/20 backdrop-blur-sm">
              <AlertCircle className="h-4 w-4 text-red-400" />
              <AlertDescription className="text-red-300">{message}</AlertDescription>
            </Alert>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <Card className="backdrop-blur-sm bg-white/5 border border-white/10">
            <CardContent className="pt-6">
              <div className="text-sm text-blue-200">
                <p>
                  <strong className="text-blue-300">Issuing from:</strong>{" "}
                  <span className="font-mono text-blue-400">{address}</span>
                </p>
                <p className="mt-1 text-muted-foreground">
                  Certificates will be permanently recorded on the blockchain and cannot be modified after issuance.
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  )
}
