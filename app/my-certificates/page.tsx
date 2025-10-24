"use client"

import { AppLayout } from "@/components/app-layout"
import { MyCertificates } from "@/components/MyCertificates"

export default function MyCertificatesPage() {
  return (
    <AppLayout>
      <div className="p-8">
        <MyCertificates />
      </div>
    </AppLayout>
  )
}
