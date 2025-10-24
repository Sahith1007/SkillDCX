from typing import List, Dict, Set
from fastapi import APIRouter
from pydantic import BaseModel
import re

# Group all AI endpoints under /ai
router = APIRouter(prefix="/ai", tags=["ai"])


# ----- Models -----
class SkillInput(BaseModel):
    skills: List[str]
    top_k: int = 5


class ChatInput(BaseModel):
    message: str
    top_k: int = 5


class MentorInput(BaseModel):
    skills: List[str]
    focus_areas: List[str] = []  # Optional: specific areas to focus on


# ----- Simple knowledge graph -----
# Map: skill -> list of (next_skill, reason)
GRAPH: Dict[str, List[Dict[str, str]]] = {
    "python": [
        {
            "skill": "machine learning",
            "reason": "Leverage Python's ML ecosystem (scikit-learn, PyTorch)",
        },
        {
            "skill": "data engineering",
            "reason": "Build ETL pipelines with pandas and Airflow",
        },
        {
            "skill": "fastapi",
            "reason": "Ship production APIs quickly using Python skills",
        },
        {
            "skill": "algorand smart contracts",
            "reason": "Use PyTeal to author Algorand contracts",
        },
    ],
    "react": [
        {"skill": "next.js", "reason": "SSR/SSG improves SEO and performance"},
        {"skill": "typescript", "reason": "Type safety for scalable React apps"},
        {
            "skill": "testing-library",
            "reason": "Improve UI reliability with component tests",
        },
    ],
    "next.js": [
        {
            "skill": "react server components",
            "reason": "Adopt modern React data-fetching patterns",
        },
        {
            "skill": "vercel deployment",
            "reason": "Optimized hosting and edge functions",
        },
    ],
    "blockchain": [
        {"skill": "zero-knowledge proofs", "reason": "Privacy-preserving verification"},
        {
            "skill": "algorand smart contracts",
            "reason": "Build efficient on-chain logic",
        },
        {"skill": "solidity", "reason": "Write EVM-compatible smart contracts"},
    ],
    "sql": [
        {
            "skill": "postgresql",
            "reason": "Advanced queries, indexing, and performance",
        },
        {"skill": "dbt", "reason": "Manage analytics transformations as code"},
    ],
    "fastapi": [
        {"skill": "uvicorn", "reason": "ASGI server tuning and deployment"},
        {"skill": "pydantic", "reason": "Robust validation and settings management"},
    ],
    "javascript": [
        {"skill": "typescript", "reason": "Add type safety to JavaScript projects"},
        {"skill": "react", "reason": "Build interactive UIs with modern JavaScript"},
        {"skill": "node.js", "reason": "Server-side JavaScript development"},
    ],
    "typescript": [
        {"skill": "next.js", "reason": "Type-safe full-stack React framework"},
        {"skill": "react", "reason": "Build type-safe React applications"},
    ],
    "web3": [
        {"skill": "solidity", "reason": "Write smart contracts for Web3 apps"},
        {"skill": "blockchain", "reason": "Understand decentralized systems"},
        {"skill": "react", "reason": "Build Web3 frontends with React"},
    ],
    "data science": [
        {"skill": "machine learning", "reason": "Build predictive models from data"},
        {"skill": "python", "reason": "Primary language for data science"},
        {"skill": "sql", "reason": "Query and analyze structured data"},
    ],
}

KNOWN_SKILLS: Set[str] = set(GRAPH.keys()) | {
    n["skill"] for v in GRAPH.values() for n in v
}


# ----- Course recommendations database -----
COURSE_RECOMMENDATIONS: Dict[str, List[Dict[str, str]]] = {
    "python": [
        {
            "title": "Python for Everybody Specialization",
            "provider": "Coursera",
            "instructor": "University of Michigan",
            "level": "Beginner",
            "description": "Complete Python programming from basics to data structures and web scraping",
            "url": "https://www.coursera.org/specializations/python"
        },
        {
            "title": "Complete Python Bootcamp From Zero to Hero",
            "provider": "Udemy",
            "instructor": "Jose Marcial Portilla",
            "level": "Beginner to Advanced",
            "description": "Learn Python like a Professional with projects, games, and algorithms",
            "url": "https://www.udemy.com/course/complete-python-bootcamp/"
        },
        {
            "title": "Python 3 Programming Specialization",
            "provider": "Coursera",
            "instructor": "University of Michigan",
            "level": "Intermediate",
            "description": "Advanced Python concepts including data collection, processing, and visualization",
            "url": "https://www.coursera.org/specializations/python-3-programming"
        }
    ],
    "web3": [
        {
            "title": "Blockchain Specialization",
            "provider": "Coursera",
            "instructor": "University at Buffalo",
            "level": "Intermediate",
            "description": "Complete blockchain technology fundamentals and smart contract development",
            "url": "https://www.coursera.org/specializations/blockchain"
        },
        {
            "title": "Ethereum and Solidity: The Complete Developer's Guide",
            "provider": "Udemy",
            "instructor": "Stephen Grider",
            "level": "Intermediate",
            "description": "Build blockchain applications with Ethereum, Solidity, and Web3",
            "url": "https://www.udemy.com/course/ethereum-and-solidity-the-complete-developers-guide/"
        },
        {
            "title": "The Complete Web3 and DeFi Development Bootcamp",
            "provider": "Udemy",
            "instructor": "Dapp University",
            "level": "Advanced",
            "description": "Build decentralized applications with React, Solidity, and Web3.js",
            "url": "https://www.udemy.com/course/the-complete-web3-development-bootcamp/"
        }
    ],
    "solidity": [
        {
            "title": "Blockchain Basics",
            "provider": "Coursera",
            "instructor": "University at Buffalo",
            "level": "Beginner",
            "description": "Introduction to blockchain technology and smart contract fundamentals",
            "url": "https://www.coursera.org/learn/blockchain-basics"
        },
        {
            "title": "Solidity & Ethereum in React (Next JS): The Complete Guide",
            "provider": "Udemy",
            "instructor": "Filip Jerga",
            "level": "Intermediate",
            "description": "Master Solidity smart contracts and integrate with React applications",
            "url": "https://www.udemy.com/course/solidity-ethereum-in-react-next-js-the-complete-guide/"
        },
        {
            "title": "Advanced Smart Contract Development",
            "provider": "Udemy",
            "instructor": "EatTheBlocks",
            "level": "Advanced",
            "description": "Advanced Solidity patterns, security, and DeFi protocols",
            "url": "https://www.udemy.com/course/advanced-smart-contract-development/"
        }
    ],
    "react": [
        {
            "title": "React Specialization",
            "provider": "Coursera",
            "instructor": "Meta",
            "level": "Beginner to Advanced",
            "description": "Complete React development from basics to advanced patterns",
            "url": "https://www.coursera.org/specializations/meta-react-native"
        },
        {
            "title": "React - The Complete Guide (incl Hooks, React Router, Redux)",
            "provider": "Udemy",
            "instructor": "Maximilian Schwarzmüller",
            "level": "Beginner to Advanced",
            "description": "Master React with hooks, routing, state management, and testing",
            "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"
        },
        {
            "title": "Modern React with Redux",
            "provider": "Udemy",
            "instructor": "Stephen Grider",
            "level": "Intermediate",
            "description": "Build modern React applications with Redux, React Router, and more",
            "url": "https://www.udemy.com/course/react-redux/"
        }
    ],
    "machine learning": [
        {
            "title": "Machine Learning Specialization",
            "provider": "Coursera",
            "instructor": "DeepLearning.AI",
            "level": "Beginner to Intermediate",
            "description": "Complete machine learning fundamentals with Python and TensorFlow",
            "url": "https://www.coursera.org/specializations/machine-learning-introduction"
        },
        {
            "title": "Python for Data Science and Machine Learning Bootcamp",
            "provider": "Udemy",
            "instructor": "Jose Marcial Portilla",
            "level": "Intermediate",
            "description": "Learn ML with NumPy, Pandas, Seaborn, Matplotlib, Plotly, Scikit-Learn",
            "url": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/"
        },
        {
            "title": "Deep Learning Specialization",
            "provider": "Coursera",
            "instructor": "DeepLearning.AI",
            "level": "Advanced",
            "description": "Master deep learning with neural networks, CNNs, RNNs, and more",
            "url": "https://www.coursera.org/specializations/deep-learning"
        }
    ],
    "data engineering": [
        {
            "title": "Data Engineering Foundations Specialization",
            "provider": "Coursera",
            "instructor": "IBM",
            "level": "Beginner to Intermediate",
            "description": "Learn data pipeline design, ETL processes, and big data tools",
            "url": "https://www.coursera.org/specializations/data-engineering-foundations"
        },
        {
            "title": "The Complete Hands-On Introduction to Apache Airflow",
            "provider": "Udemy",
            "instructor": "Marc Lamberti",
            "level": "Intermediate",
            "description": "Master Apache Airflow for data pipeline orchestration and workflow management",
            "url": "https://www.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/"
        },
        {
            "title": "Spark and Python for Big Data with PySpark",
            "provider": "Udemy",
            "instructor": "Jose Marcial Portilla",
            "level": "Intermediate to Advanced",
            "description": "Learn Apache Spark and PySpark for big data processing and analytics",
            "url": "https://www.udemy.com/course/spark-and-python-for-big-data-with-pyspark/"
        }
    ],
    "javascript": [
        {
            "title": "The Complete JavaScript Course",
            "provider": "Udemy",
            "instructor": "Jonas Schmedtmann",
            "level": "Beginner to Advanced",
            "description": "Modern JavaScript from scratch to advanced ES6+ features",
            "url": "https://www.udemy.com/course/the-complete-javascript-course/"
        },
        {
            "title": "JavaScript Algorithms and Data Structures",
            "provider": "Coursera",
            "instructor": "University of California San Diego",
            "level": "Intermediate",
            "description": "Master algorithms and data structures using JavaScript",
            "url": "https://www.coursera.org/specializations/data-structures-algorithms"
        }
    ],
    "typescript": [
        {
            "title": "Understanding TypeScript",
            "provider": "Udemy",
            "instructor": "Maximilian Schwarzmüller",
            "level": "Beginner to Advanced",
            "description": "Master TypeScript and build better JavaScript applications",
            "url": "https://www.udemy.com/course/understanding-typescript/"
        },
        {
            "title": "TypeScript for Professionals",
            "provider": "Udemy",
            "instructor": "Basarat Ali Syed",
            "level": "Intermediate to Advanced",
            "description": "Advanced TypeScript patterns and best practices",
            "url": "https://www.udemy.com/course/typescript-for-professionals/"
        }
    ],
    "next.js": [
        {
            "title": "Next.js & React - The Complete Guide",
            "provider": "Udemy",
            "instructor": "Maximilian Schwarzmüller",
            "level": "Intermediate",
            "description": "Build fullstack React apps with Next.js 14+ including App Router",
            "url": "https://www.udemy.com/course/nextjs-react-the-complete-guide/"
        },
        {
            "title": "Complete Next.js Developer",
            "provider": "Udemy",
            "instructor": "Andrei Neagoie",
            "level": "Intermediate to Advanced",
            "description": "Master Next.js with SSR, SSG, and API routes",
            "url": "https://www.udemy.com/course/complete-nextjs-developer/"
        }
    ],
    "blockchain": [
        {
            "title": "Blockchain Fundamentals",
            "provider": "Coursera",
            "instructor": "University at Buffalo",
            "level": "Beginner",
            "description": "Introduction to blockchain technology and cryptocurrencies",
            "url": "https://www.coursera.org/learn/blockchain-basics"
        },
        {
            "title": "Blockchain A-Z: Build a Blockchain",
            "provider": "Udemy",
            "instructor": "Hadelin de Ponteves",
            "level": "Intermediate",
            "description": "Build your own blockchain and cryptocurrency from scratch",
            "url": "https://www.udemy.com/course/build-your-blockchain-az/"
        }
    ],
    "fastapi": [
        {
            "title": "FastAPI - The Complete Course",
            "provider": "Udemy",
            "instructor": "Sanjeev Thiyagarajan",
            "level": "Beginner to Intermediate",
            "description": "Build modern APIs with FastAPI and Python",
            "url": "https://www.udemy.com/course/fastapi-the-complete-course/"
        },
        {
            "title": "Complete FastAPI Masterclass",
            "provider": "Udemy",
            "instructor": "Jose Salvatierra",
            "level": "Intermediate to Advanced",
            "description": "Advanced FastAPI patterns with async, testing, and deployment",
            "url": "https://www.udemy.com/course/fastapi-masterclass/"
        }
    ],
    "sql": [
        {
            "title": "The Complete SQL Bootcamp",
            "provider": "Udemy",
            "instructor": "Jose Marcial Portilla",
            "level": "Beginner to Intermediate",
            "description": "Master SQL queries, database design, and PostgreSQL",
            "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/"
        },
        {
            "title": "Advanced SQL for Data Scientists",
            "provider": "Coursera",
            "instructor": "University of Colorado",
            "level": "Advanced",
            "description": "Complex queries, window functions, and query optimization",
            "url": "https://www.coursera.org/learn/sql-data-science"
        }
    ]
}


def _normalize(skills: List[str]) -> List[str]:
    return [s.strip().lower() for s in skills if s and s.strip()]


def _extract_skills_from_text(message: str) -> List[str]:
    tokens = re.findall(r"[a-zA-Z0-9+.#]+", message.lower())
    present = {t for t in tokens if t in KNOWN_SKILLS}
    return list(present)


def _recommend(skills: List[str], top_k: int) -> List[Dict]:
    have = set(_normalize(skills))
    candidate_scores: Dict[str, float] = {}
    candidate_reasons: Dict[str, Set[str]] = {}

    for s in have:
        for rec in GRAPH.get(s, []):
            target = rec["skill"].lower()
            if target in have:
                continue
            candidate_scores[target] = candidate_scores.get(target, 0.0) + 1.0
            candidate_reasons.setdefault(target, set()).add(rec["reason"])

    # Simple normalization by max score
    if candidate_scores:
        max_score = max(candidate_scores.values()) or 1.0
    else:
        max_score = 1.0

    ranked = sorted(
        (
            {
                "skill": skill,
                "score": round(score / max_score, 3),
                "reasons": sorted(list(candidate_reasons.get(skill, set())))
                or ["Related progression based on your current skills"],
            }
            for skill, score in candidate_scores.items()
        ),
        key=lambda x: x["score"],
        reverse=True,
    )

    # Fallback when graph yields nothing
    if not ranked:
        ranked = [
            {
                "skill": "python",
                "score": 0.5,
                "reasons": [
                    "Great general-purpose foundation to unlock ML, APIs, and scripting"
                ],
            },
            {
                "skill": "react",
                "score": 0.45,
                "reasons": ["Popular UI framework to build web apps end-to-end"],
            },
        ]

    return ranked[: max(1, top_k)]


@router.post("/recommend")
def recommend(payload: SkillInput):
    skills = _normalize(payload.skills)
    recs = _recommend(skills, payload.top_k)
    return {"input_skills": skills, "recommendations": recs}


@router.post("/chat")
def chat(payload: ChatInput):
    extracted = _extract_skills_from_text(payload.message)
    recs = _recommend(extracted, payload.top_k)
    return {"input_skills": extracted, "recommendations": recs, "message_mode": True}


def _get_course_recommendations(skills: List[str]) -> List[Dict]:
    """Get course recommendations based on user skills."""
    skills_normalized = _normalize(skills)
    all_courses = []
    
    # Get courses for existing skills (to level up)
    for skill in skills_normalized:
        if skill in COURSE_RECOMMENDATIONS:
            courses = COURSE_RECOMMENDATIONS[skill]
            for course in courses:
                all_courses.append({
                    **course,
                    "skill_match": skill,
                    "recommendation_type": "skill_advancement"
                })
    
    # Get courses for recommended next skills
    next_skills = _recommend(skills_normalized, 5)
    for skill_rec in next_skills:
        skill = skill_rec["skill"]
        if skill in COURSE_RECOMMENDATIONS:
            courses = COURSE_RECOMMENDATIONS[skill]
            # Take top 2 courses for each recommended skill
            for course in courses[:2]:
                all_courses.append({
                    **course,
                    "skill_match": skill,
                    "recommendation_type": "next_skill",
                    "skill_score": skill_rec["score"],
                    "reasons": skill_rec["reasons"]
                })
    
    # Remove duplicates and sort by relevance
    seen = set()
    unique_courses = []
    for course in all_courses:
        course_id = f"{course['title']}_{course['provider']}"
        if course_id not in seen:
            seen.add(course_id)
            unique_courses.append(course)
    
    # Prioritize skill advancement first, then next skills by score
    unique_courses.sort(key=lambda x: (
        0 if x["recommendation_type"] == "skill_advancement" else 1,
        -x.get("skill_score", 0)
    ))
    
    return unique_courses[:10]  # Return top 10 recommendations


@router.post("/mentor")
def mentor(payload: MentorInput):
    """Get personalized course recommendations based on current skills."""
    if not payload.skills:
        return {
            "error": "Please provide at least one skill",
            "recommendations": []
        }
    
    courses = _get_course_recommendations(payload.skills)
    
    # If focus areas are provided, filter or prioritize accordingly
    if payload.focus_areas:
        focus_normalized = _normalize(payload.focus_areas)
        # Boost courses that match focus areas
        for course in courses:
            if any(focus in course["skill_match"].lower() or 
                   focus in course["title"].lower() or
                   focus in course["description"].lower() 
                   for focus in focus_normalized):
                course["focus_match"] = True
        
        # Sort to prioritize focus matches
        courses.sort(key=lambda x: (not x.get("focus_match", False)))
    
    return {
        "input_skills": _normalize(payload.skills),
        "focus_areas": _normalize(payload.focus_areas) if payload.focus_areas else [],
        "recommendations": courses,
        "total_found": len(courses)
    }
