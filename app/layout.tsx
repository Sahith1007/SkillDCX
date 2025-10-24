import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { WalletProvider } from "@/contexts/wallet-context"
import { Toaster } from "@/components/ui/toaster"

export const metadata: Metadata = {
  title: "SkillDCX - Blockchain Certificate Platform",
  description: "Manage and verify blockchain certificates with SkillDCX",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
  <body className="dark font-sans">
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <WalletProvider>
        {children}
        <Toaster />
      </WalletProvider>
    </ThemeProvider>
  </body>
</html>

  )
}
