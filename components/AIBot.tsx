"use client";
import { useState } from "react";

export default function AIBot() {
  const [skills, setSkills] = useState("");
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleRecommend = async () => {
    setLoading(true);
    const res = await fetch("http://127.0.0.1:8000/ai-recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skills: skills.split(",").map(s => s.trim()) })
    });
    const data = await res.json();
    setRecommendations(data.recommendations);
    setLoading(false);
  };

  return (
    <div className="p-4 bg-gray-900 rounded-xl shadow-xl">
      <h2 className="text-xl font-bold mb-2">🚀 AI Career Recommender</h2>
      <input
        type="text"
        placeholder="e.g. Python, React, Blockchain"
        className="w-full p-2 rounded bg-gray-800 text-white mb-3"
        value={skills}
        onChange={(e) => setSkills(e.target.value)}
      />
      <button
        onClick={handleRecommend}
        className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700 transition"
      >
        {loading ? "Thinking..." : "Get Recommendations"}
      </button>

      {recommendations.length > 0 && (
        <ul className="mt-4 space-y-2">
          {recommendations.map((rec, i) => (
            <li key={i} className="bg-gray-800 p-2 rounded">
              {rec}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
