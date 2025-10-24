"use client"

import { AppLayout } from "@/components/app-layout"
import { SkillMentorAI } from "@/components/SkillMentorAI"

export default function AIMentorPage() {
  return (
    <AppLayout>
      <div className="p-8">
        <SkillMentorAI />
      </div>
    </AppLayout>
  )
}
