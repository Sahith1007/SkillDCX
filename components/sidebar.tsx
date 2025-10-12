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

export function Sidebar() {
  const pathname = usePathname()
  const { isAuthorizedIssuer } = useWallet()

  return (
    <div className="w-64 bg-sidebar/95 backdrop-blur-sm border-r border-sidebar-border/50">
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center px-6 border-b border-sidebar-border/50">
          <motion.h1
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-blue-600 bg-clip-text text-transparent"
          >
            SkillDCX
          </motion.h1>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item, index) => {
            if (item.requiresIssuer && !isAuthorizedIssuer) {
              return null
            }

            const isActive = pathname === item.href
            return (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 group",
                    isActive
                      ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-400 shadow-lg border border-blue-500/30"
                      : "text-sidebar-foreground hover:bg-gradient-to-r hover:from-blue-500/10 hover:to-purple-500/10 hover:text-blue-300 hover:scale-105 hover:shadow-md",
                  )}
                >
                  <item.icon
                    className={cn(
                      "h-5 w-5 transition-all duration-300",
                      isActive
                        ? "text-blue-400"
                        : "text-sidebar-foreground group-hover:text-blue-300 group-hover:scale-110",
                    )}
                  />
                  <span className="group-hover:translate-x-1 transition-transform duration-300">{item.name}</span>
                </Link>
              </motion.div>
            )
          })}
        </nav>
      </div>
    </div>
  )
}
