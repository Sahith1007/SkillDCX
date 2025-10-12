"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Home, Award, FileText, Shield, User } from "lucide-react"
import { motion } from "framer-motion"
import { useWallet } from "@/contexts/wallet-context"

const navigation = [
  { name: "Home", href: "/", icon: Home },
  { name: "My Certificates", href: "/certificates", icon: Award },
  { name: "Issue Certificate", href: "/issue", icon: FileText, requiresIssuer: true },
  { name: "Verify", href: "/verify", icon: Shield },
  { name: "Profile", href: "/profile", icon: User },
]

export function TopNav() {
  const pathname = usePathname()
  const { isAuthorizedIssuer, address, isConnected } = useWallet()

  return (
    <div className="w-full bg-sidebar/80 backdrop-blur-sm border-b border-sidebar-border/50">
      <header className="flex h-16 items-center justify-between px-4 md:px-6">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2">
          <motion.span
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
            className="text-xl md:text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-blue-600 bg-clip-text text-transparent"
          >
            SkillDCX
          </motion.span>
        </Link>

        {/* Nav items */}
        <nav aria-label="Primary" className="hidden md:flex items-center gap-2">
          {navigation.map((item, index) => {
            if (item.requiresIssuer && !isAuthorizedIssuer) return null
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: index * 0.05 }}
              >
                <Link
                  href={item.href}
                  className={cn(
                    "group inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-all duration-300",
                    "border border-transparent",
                    isActive
                      ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 shadow-[0_0_20px_-6px_rgba(59,130,246,0.45)] border-blue-500/30"
                      : "text-sidebar-foreground hover:bg-gradient-to-r hover:from-blue-500/10 hover:to-purple-500/10 hover:text-blue-300 hover:shadow-[0_0_16px_-8px_rgba(59,130,246,0.45)] hover:scale-[1.03]",
                  )}
                >
                  <Icon
                    className={cn(
                      "h-4 w-4 transition-transform duration-300",
                      isActive
                        ? "text-blue-300"
                        : "text-sidebar-foreground group-hover:text-blue-300 group-hover:scale-110",
                    )}
                  />
                  <span className="whitespace-nowrap">{item.name}</span>
                </Link>
              </motion.div>
            )
          })}
        </nav>

        {/* Right side: wallet badge (optional visual only) */}
        <div className="flex items-center">
          {isConnected && address ? (
            <span className="text-xs md:text-sm rounded-full px-3 py-1 bg-gradient-to-r from-blue-500/15 to-purple-500/15 border border-blue-500/30 text-blue-200">
              {address}
            </span>
          ) : (
            <span className="text-xs md:text-sm text-muted-foreground">Not connected</span>
          )}
        </div>
      </header>

      {/* Mobile nav row */}
      <div className="md:hidden border-t border-sidebar-border/50">
        <nav aria-label="Mobile Primary" className="flex overflow-x-auto no-scrollbar px-3 py-2 gap-2">
          {navigation.map((item, index) => {
            if (item.requiresIssuer && !isAuthorizedIssuer) return null
            const isActive = pathname === item.href
            const Icon = item.icon
            return (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2, delay: index * 0.04 }}
              >
                <Link
                  href={item.href}
                  className={cn(
                    "group inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-all duration-300",
                    isActive
                      ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-300 border border-blue-500/30"
                      : "text-sidebar-foreground hover:bg-gradient-to-r hover:from-blue-500/10 hover:to-purple-500/10 hover:text-blue-300",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="whitespace-nowrap">{item.name}</span>
                </Link>
              </motion.div>
            )
          })}
        </nav>
      </div>
    </div>
  )
}
