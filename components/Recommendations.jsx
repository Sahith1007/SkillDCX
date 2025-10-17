// frontend/src/components/Recommendations.jsx
"use client";
import React, { useState } from "react";
import useRecommendations from "@/hooks/useRecommendations";
import Recommendations from "@/components/Recommendations";



export default function Recommendations({ userId }) {
  // For demo, you can pass a demo skill list in opts (e.g., ["python", "data analysis"])
  const { userId, recommendations, loading, inputSkills } = useRecommendations(userId, { demoSkills: null });

  const [demoMode, setDemoMode] = useState(false);

  if (loading) return <div className="p-4">Loading recommendations…</div>;

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Skill Growth Bot — Recommendations</h2>
        <button
          className="text-sm px-3 py-1 border rounded"
          onClick={() => setDemoMode(!demoMode)}
        >
          Demo mode: {demoMode ? "ON" : "OFF"}
        </button>
      </div>

      <div className="mb-3 text-sm text-gray-500">Current Skills: {inputSkills.length ? inputSkills.join(", ") : "— none detected —"}</div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.length === 0 && <div>No recommendations available yet.</div>}
        {recommendations.map((r) => (
          <div key={r.skill} className="p-4 bg-white rounded-lg shadow">
            <div className="flex justify-between items-start">
              <div>
                <div className="text-lg font-semibold">{r.skill}</div>
                <div className="text-xs text-gray-500">score: {r.score}</div>
              </div>
              <div className="text-xs text-gray-400">{r.tags?.join(", ")}</div>
            </div>

            {r.courses && r.courses.length > 0 && (
              <div className="mt-3">
                <div className="text-sm font-medium">Suggested courses</div>
                <ul className="mt-2 space-y-2">
                  {r.courses.map((c, i) => (
                    <li key={i} className="text-sm">
                      <a href={c.link || "#"} className="text-indigo-600 hover:underline">
                        {c.title}
                      </a>
                      <div className="text-xs text-gray-500">Issuer: {c.issuer}</div>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="mt-4 flex gap-2">
              <button className="px-3 py-1 bg-indigo-600 text-white rounded">Add to Roadmap</button>
              <button className="px-3 py-1 border rounded">View Issuers</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

