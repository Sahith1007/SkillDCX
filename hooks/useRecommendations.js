// frontend/src/hooks/useRecommendations.js
import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export default function useRecommendations(userId, opts = { demoSkills: null }) {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inputSkills, setInputSkills] = useState([]);

  useEffect(() => {
    async function fetchRecs() {
      setLoading(true);
      try {
        const body = {
          current_skills: opts.demoSkills || null,
          top_n: 6
        };
        const res = await fetch(`${API_BASE}/api/recommendations/for_user/${encodeURIComponent(userId)}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        });
        const json = await res.json();
        setInputSkills(json.input_skills || []);
        setRecommendations(json.recommendations || []);
      } catch (e) {
        console.error("Recommendation fetch error", e);
        setRecommendations([]);
      } finally {
        setLoading(false);
      }
    }

    if (!userId) {
      setRecommendations([]);
      setLoading(false);
      return;
    }

    fetchRecs();
  }, [userId, opts.demoSkills]);

  return { recommendations, loading, inputSkills };
}
