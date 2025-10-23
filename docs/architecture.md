# SkillDCX Architecture

- Backend: FastAPI (Python) exposing REST APIs.
- AI: /ai endpoints for skills recommendation (rule-based graph, LLM-pluggable).
- Other services: certificates and verification under dedicated prefixes.

Key endpoints:
- POST /ai/recommend: { skills: string[], top_k?: number }
- POST /ai/chat: { message: string, top_k?: number }

Response example:
{
  "input_skills": ["python", "react"],
  "recommendations": [
    { "skill": "next.js", "score": 1.0, "reasons": ["SSR/SSG improves SEO and performance"] }
  ]
}