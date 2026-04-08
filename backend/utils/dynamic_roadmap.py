"""
Dynamic AI Roadmap — Adaptive Learning Path Generator

Not just a static roadmap — a dynamic AI-powered learning path that adapts based on:
  - Resume gaps (detected via NLC analysis)
  - Target job requirements
  - Current skill level (junior/mid/senior)
  - Skill priority scoring based on market demand

Uses NLC (TF-IDF + cosine similarity) to analyze resume text and determine:
  1. Current proficiency levels per skill
  2. Gap severity
  3. Optimal learning order
  4. Personalized difficulty progression
"""

import re
import numpy as np
from typing import Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =====================================================================
#  SKILL DATABASE — detailed info for dynamic roadmaps
# =====================================================================

SKILL_DATABASE = {
    "python": {
        "category": "Programming",
        "market_demand": 0.95,
        "difficulty": "medium",
        "prerequisites": [],
        "related_skills": ["django", "flask", "fastapi", "data analysis"],
        "levels": {
            "beginner": {"topics": ["Syntax basics", "Data types & structures", "Functions & loops", "File I/O"], "hours": 20, "projects": ["CLI Calculator", "File Organizer Script"]},
            "intermediate": {"topics": ["OOP & classes", "Decorators & generators", "Error handling", "Virtual environments", "pip & packages"], "hours": 25, "projects": ["Web Scraper", "REST API with Flask"]},
            "advanced": {"topics": ["Async programming", "Metaclasses", "Memory management", "Design patterns", "Testing (pytest)"], "hours": 30, "projects": ["Full Production API", "Package published to PyPI"]}
        }
    },
    "javascript": {
        "category": "Programming",
        "market_demand": 0.93,
        "difficulty": "medium",
        "prerequisites": [],
        "related_skills": ["typescript", "react", "node.js", "vue"],
        "levels": {
            "beginner": {"topics": ["Variables & types", "DOM manipulation", "Events", "ES6+ features"], "hours": 18, "projects": ["Interactive to-do app", "Quiz game"]},
            "intermediate": {"topics": ["Promises & async/await", "Modules & bundlers", "Closures & prototypes", "Error handling"], "hours": 22, "projects": ["Weather app with API", "Chat application"]},
            "advanced": {"topics": ["Design patterns", "Performance optimization", "Web Workers", "Service Workers"], "hours": 28, "projects": ["Full SPA framework", "Browser extension"]}
        }
    },
    "react": {
        "category": "Frontend",
        "market_demand": 0.92,
        "difficulty": "medium",
        "prerequisites": ["javascript", "html", "css"],
        "related_skills": ["next.js", "redux", "typescript"],
        "levels": {
            "beginner": {"topics": ["JSX & components", "Props & state", "Event handling", "Conditional rendering"], "hours": 15, "projects": ["Todo app", "Counter app"]},
            "intermediate": {"topics": ["Hooks (useState, useEffect, useContext)", "React Router", "API integration", "Form handling"], "hours": 20, "projects": ["Blog platform", "E-commerce UI"]},
            "advanced": {"topics": ["Performance (memo, useMemo)", "Custom hooks", "Context API patterns", "Testing with Jest/RTL"], "hours": 25, "projects": ["Full dashboard app", "Component library"]}
        }
    },
    "machine learning": {
        "category": "AI/ML",
        "market_demand": 0.90,
        "difficulty": "hard",
        "prerequisites": ["python", "statistics"],
        "related_skills": ["deep learning", "nlp", "computer vision"],
        "levels": {
            "beginner": {"topics": ["Supervised vs unsupervised", "Linear/logistic regression", "Decision trees", "scikit-learn basics"], "hours": 25, "projects": ["House price predictor", "Iris classifier"]},
            "intermediate": {"topics": ["Random forests", "SVM", "Cross-validation", "Feature engineering", "Pipelines"], "hours": 30, "projects": ["Customer churn model", "Recommendation engine"]},
            "advanced": {"topics": ["Ensemble methods", "Dimensionality reduction", "Model interpretability", "ML system design"], "hours": 35, "projects": ["End-to-end ML pipeline", "AutoML system"]}
        }
    },
    "docker": {
        "category": "DevOps",
        "market_demand": 0.88,
        "difficulty": "medium",
        "prerequisites": ["linux basics"],
        "related_skills": ["kubernetes", "ci/cd", "terraform"],
        "levels": {
            "beginner": {"topics": ["Containers vs VMs", "Dockerfile basics", "Docker CLI", "Images & registries"], "hours": 10, "projects": ["Containerized Python app", "Multi-stage build"]},
            "intermediate": {"topics": ["Docker Compose", "Networking", "Volumes", "Environment variables"], "hours": 12, "projects": ["Multi-container web app", "Dev environment setup"]},
            "advanced": {"topics": ["Docker Swarm", "Security best practices", "Optimization", "CI/CD integration"], "hours": 15, "projects": ["Production deployment", "Zero-downtime deploy"]}
        }
    },
    "sql": {
        "category": "Data",
        "market_demand": 0.91,
        "difficulty": "easy",
        "prerequisites": [],
        "related_skills": ["postgresql", "mongodb", "data analysis"],
        "levels": {
            "beginner": {"topics": ["SELECT, WHERE, ORDER BY", "JOINs (INNER, LEFT, RIGHT)", "GROUP BY & aggregates", "Subqueries"], "hours": 12, "projects": ["Employee database queries", "Sales analysis"]},
            "intermediate": {"topics": ["Window functions", "CTEs", "Indexes", "Transactions", "Views"], "hours": 15, "projects": ["Analytics dashboard queries", "Data warehouse design"]},
            "advanced": {"topics": ["Query optimization", "Partitioning", "Stored procedures", "Database design"], "hours": 18, "projects": ["High-performance query system", "Database migration tool"]}
        }
    },
    "aws": {
        "category": "Cloud",
        "market_demand": 0.89,
        "difficulty": "hard",
        "prerequisites": ["linux basics", "networking"],
        "related_skills": ["terraform", "kubernetes", "ci/cd"],
        "levels": {
            "beginner": {"topics": ["EC2 & S3 basics", "IAM & security", "RDS databases", "Free tier hands-on"], "hours": 15, "projects": ["Static website on S3", "EC2 web server"]},
            "intermediate": {"topics": ["Lambda & serverless", "API Gateway", "CloudFormation", "VPC & networking"], "hours": 20, "projects": ["Serverless REST API", "Auto-scaling app"]},
            "advanced": {"topics": ["ECS/EKS", "CI/CD with CodePipeline", "CloudWatch monitoring", "Cost optimization", "Well-Architected"], "hours": 25, "projects": ["Full cloud architecture", "Multi-region deployment"]}
        }
    },
    "typescript": {
        "category": "Programming",
        "market_demand": 0.87,
        "difficulty": "medium",
        "prerequisites": ["javascript"],
        "related_skills": ["react", "node.js", "angular"],
        "levels": {
            "beginner": {"topics": ["Types & interfaces", "Type annotations", "Enums", "Generics basics"], "hours": 10, "projects": ["Type-safe utility library", "Typed REST client"]},
            "intermediate": {"topics": ["Advanced generics", "Mapped types", "Conditional types", "Declaration files"], "hours": 15, "projects": ["Full-stack typed app", "npm package with types"]},
            "advanced": {"topics": ["Advanced patterns", "Type gymnastics", "Compiler API", "Custom transformers"], "hours": 18, "projects": ["Type-safe ORM", "Custom TS plugin"]}
        }
    },
    "git": {
        "category": "Tools",
        "market_demand": 0.95,
        "difficulty": "easy",
        "prerequisites": [],
        "related_skills": ["github", "ci/cd"],
        "levels": {
            "beginner": {"topics": ["Add, commit, push", "Branching & merging", "Pull requests", "Resolving conflicts"], "hours": 6, "projects": ["Open source contribution", "Git-based blog"]},
            "intermediate": {"topics": ["Rebasing", "Cherry-pick", "Git hooks", "Bisect"], "hours": 8, "projects": ["Team workflow setup", "Automated releases"]},
            "advanced": {"topics": ["Git internals", "Custom hooks", "Monorepo management", "Git LFS"], "hours": 10, "projects": ["CI/CD pipeline", "Git automation tools"]}
        }
    },
    "kubernetes": {
        "category": "DevOps",
        "market_demand": 0.85,
        "difficulty": "hard",
        "prerequisites": ["docker", "linux basics"],
        "related_skills": ["docker", "terraform", "helm"],
        "levels": {
            "beginner": {"topics": ["Pods & Services", "Deployments", "kubectl basics", "YAML manifests"], "hours": 15, "projects": ["Deploy app to minikube", "Multi-pod setup"]},
            "intermediate": {"topics": ["Ingress", "ConfigMaps & Secrets", "Persistent volumes", "Namespaces"], "hours": 20, "projects": ["Production-ready cluster", "Microservices deployment"]},
            "advanced": {"topics": ["Helm charts", "Operators", "RBAC", "Monitoring stack", "Auto-scaling"], "hours": 25, "projects": ["Custom operator", "GitOps pipeline"]}
        }
    },
    "deep learning": {
        "category": "AI/ML",
        "market_demand": 0.88,
        "difficulty": "hard",
        "prerequisites": ["python", "machine learning", "linear algebra"],
        "related_skills": ["tensorflow", "pytorch", "nlp", "computer vision"],
        "levels": {
            "beginner": {"topics": ["Neural network basics", "Backpropagation", "Activation functions", "Keras basics"], "hours": 20, "projects": ["MNIST classifier", "Binary classifier"]},
            "intermediate": {"topics": ["CNNs", "RNNs/LSTMs", "Transfer learning", "Regularization", "Hyperparameter tuning"], "hours": 30, "projects": ["Image classifier", "Text generator"]},
            "advanced": {"topics": ["Transformers", "GANs", "Attention mechanisms", "Model deployment", "Distributed training"], "hours": 40, "projects": ["Custom transformer", "Production ML system"]}
        }
    },
    "ci/cd": {
        "category": "DevOps",
        "market_demand": 0.86,
        "difficulty": "medium",
        "prerequisites": ["git"],
        "related_skills": ["docker", "kubernetes", "terraform"],
        "levels": {
            "beginner": {"topics": ["CI/CD concepts", "GitHub Actions basics", "Automated testing", "Build pipelines"], "hours": 8, "projects": ["Auto-test pipeline", "Simple deploy flow"]},
            "intermediate": {"topics": ["Multi-stage pipelines", "Environments", "Secrets management", "Artifact management"], "hours": 12, "projects": ["Full CI/CD pipeline", "Blue-green deployment"]},
            "advanced": {"topics": ["Custom runners", "GitOps", "Canary deployments", "Pipeline optimization"], "hours": 15, "projects": ["Enterprise CI/CD", "Self-service platform"]}
        }
    },
    "system design": {
        "category": "Architecture",
        "market_demand": 0.90,
        "difficulty": "hard",
        "prerequisites": ["databases", "networking", "apis"],
        "related_skills": ["microservices", "cloud", "databases"],
        "levels": {
            "beginner": {"topics": ["Client-server architecture", "REST APIs", "Caching basics", "Load balancing intro"], "hours": 15, "projects": ["Design a URL shortener", "Design a chat app"]},
            "intermediate": {"topics": ["Microservices", "Database sharding", "Message queues", "CAP theorem"], "hours": 20, "projects": ["Design Twitter feed", "Design e-commerce"]},
            "advanced": {"topics": ["Distributed systems", "Consensus algorithms", "Event sourcing", "Global scale design"], "hours": 25, "projects": ["Design YouTube", "Design distributed cache"]}
        }
    },
    "testing": {
        "category": "Quality",
        "market_demand": 0.84,
        "difficulty": "medium",
        "prerequisites": [],
        "related_skills": ["ci/cd", "tdd"],
        "levels": {
            "beginner": {"topics": ["Unit tests", "Test frameworks (Jest/pytest)", "Assertions", "Test structure"], "hours": 10, "projects": ["Test suite for utility library", "API endpoint tests"]},
            "intermediate": {"topics": ["Integration tests", "Mocking", "Code coverage", "TDD workflow"], "hours": 15, "projects": ["Full test coverage project", "E2E testing setup"]},
            "advanced": {"topics": ["Performance testing", "Security testing", "Test architecture", "Property-based testing"], "hours": 18, "projects": ["Testing framework", "Automated QA pipeline"]}
        }
    },
}

# Experience level detection patterns
EXPERIENCE_PATTERNS = {
    "senior": [
        r'\b(8|9|10|\d{2})\+?\s*years', r'\bsenior\b', r'\blead\b', r'\bprincipal\b',
        r'\bstaff\b', r'\barchitect\b', r'\bmanager\b', r'\bdirector\b'
    ],
    "mid": [
        r'\b[3-7]\+?\s*years', r'\bintermediate\b', r'\bexperienced\b'
    ],
    "junior": [
        r'\b[0-2]\+?\s*years?', r'\bjunior\b', r'\bintern\b', r'\bfresher\b',
        r'\bentry[\s-]level\b', r'\bgraduate\b', r'\bstudent\b'
    ]
}


class DynamicRoadmapGenerator:
    """
    AI-powered dynamic roadmap generator that adapts based on
    resume analysis, target job, and current skill levels.
    """

    def __init__(self):
        self.tfidf = TfidfVectorizer(max_features=500, stop_words='english')

    def generate_dynamic_roadmap(
        self,
        resume_text: str,
        job_role: str,
        target_skills: List[str],
        job_description: str = "",
        weeks: int = 8
    ) -> Dict:
        """
        Generate an AI-adaptive learning roadmap.

        Returns:
        {
            "experience_level": str,
            "total_weeks": int,
            "skill_priorities": [...],
            "roadmap": [{week, title, focus, tasks, hours, resources, difficulty, ...}],
            "milestones": [...],
            "adaptive_insights": [...]
        }
        """
        resume_clean = self._clean_text(resume_text)

        # ── Step 1: Detect experience level ──
        experience_level = self._detect_experience_level(resume_clean)

        # ── Step 2: Assess current skill levels ──
        skill_assessments = self._assess_skill_levels(resume_clean, target_skills)

        # ── Step 3: Prioritize skills ──
        prioritized = self._prioritize_skills(skill_assessments, job_role, job_description)

        # ── Step 4: Generate adaptive roadmap ──
        roadmap = self._build_adaptive_roadmap(prioritized, experience_level, weeks)

        # ── Step 5: Generate milestones ──
        milestones = self._generate_milestones(roadmap, weeks)

        # ── Step 6: Adaptive insights ──
        insights = self._generate_insights(experience_level, prioritized, job_role)

        return {
            "experience_level": experience_level,
            "total_weeks": weeks,
            "skill_priorities": prioritized,
            "roadmap": roadmap,
            "milestones": milestones,
            "adaptive_insights": insights,
            "is_dynamic": True,
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s/\-\+\.\#]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _detect_experience_level(self, resume: str) -> str:
        """Detect experience level from resume text using NLC patterns."""
        for level, patterns in EXPERIENCE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, resume, re.IGNORECASE):
                    return level
        # Default guess based on content density
        word_count = len(resume.split())
        if word_count > 500:
            return "mid"
        elif word_count > 300:
            return "mid"
        else:
            return "junior"

    def _assess_skill_levels(self, resume: str, skills: List[str]) -> List[Dict]:
        """Assess current proficiency for each skill using NLC."""
        assessments = []
        for skill in skills:
            skill_lower = skill.lower().strip()
            info = SKILL_DATABASE.get(skill_lower, None)

            # Count mentions and context
            mentions = len(re.findall(re.escape(skill_lower), resume))
            context_words = self._get_context_words(resume, skill_lower)

            # Determine proficiency
            proficiency = "beginner"
            if mentions >= 4 and any(w in context_words for w in ["advanced", "expert", "led", "architected", "designed"]):
                proficiency = "advanced"
            elif mentions >= 2 and any(w in context_words for w in ["developed", "built", "implemented", "created"]):
                proficiency = "intermediate"
            elif mentions >= 1:
                proficiency = "beginner"
            else:
                proficiency = "none"

            # Gap severity (0 = no gap, 1 = critical gap)
            gap_severity = {"none": 1.0, "beginner": 0.7, "intermediate": 0.4, "advanced": 0.1}
            gap = gap_severity.get(proficiency, 0.8)

            # Market demand
            demand = info["market_demand"] if info else 0.7

            assessments.append({
                "skill": skill,
                "current_level": proficiency,
                "gap_severity": gap,
                "market_demand": demand,
                "mentions_in_resume": mentions,
                "category": info["category"] if info else "Other",
                "difficulty": info["difficulty"] if info else "medium",
            })

        return assessments

    def _get_context_words(self, resume: str, skill: str) -> List[str]:
        """Extract words near a skill mention for NLC context analysis."""
        words = resume.split()
        context = []
        for i, word in enumerate(words):
            if skill in word:
                start = max(0, i - 5)
                end = min(len(words), i + 6)
                context.extend(words[start:end])
        return context

    def _prioritize_skills(self, assessments: List[Dict], job_role: str, jd: str) -> List[Dict]:
        """Prioritize skills based on gap severity × market demand × role relevance."""
        for item in assessments:
            # Priority score = gap × demand × difficulty_weight
            difficulty_weight = {"easy": 0.8, "medium": 1.0, "hard": 1.2}.get(item["difficulty"], 1.0)
            item["priority_score"] = round(
                item["gap_severity"] * item["market_demand"] * difficulty_weight, 3
            )

            # Priority label
            if item["priority_score"] > 0.7:
                item["priority"] = "🔴 Critical"
            elif item["priority_score"] > 0.4:
                item["priority"] = "🟡 Important"
            else:
                item["priority"] = "🟢 Nice to Have"

        # Sort by priority score (highest first)
        assessments.sort(key=lambda x: x["priority_score"], reverse=True)
        return assessments

    def _build_adaptive_roadmap(
        self, prioritized_skills: List[Dict], experience_level: str, total_weeks: int
    ) -> List[Dict]:
        """Build week-by-week roadmap with adaptive difficulty."""
        roadmap = []
        current_week = 1

        for skill_info in prioritized_skills:
            if current_week > total_weeks:
                break

            skill_name = skill_info["skill"].lower().strip()
            skill_data = SKILL_DATABASE.get(skill_name, None)
            current_level = skill_info["current_level"]

            # Determine which levels to learn
            levels_to_learn = self._get_levels_to_learn(current_level, experience_level)

            for level in levels_to_learn:
                if current_week > total_weeks:
                    break

                if skill_data and level in skill_data.get("levels", {}):
                    level_info = skill_data["levels"][level]
                    topics = level_info["topics"]
                    hours = level_info["hours"]
                    projects = level_info["projects"]
                else:
                    topics = [f"Learn {level} {skill_info['skill']} concepts", f"Practice with {level} exercises", f"Build a {level} project"]
                    hours = 12
                    projects = [f"{level.title()} {skill_info['skill']} project"]

                # Adaptive adjustment based on experience
                if experience_level == "senior":
                    hours = int(hours * 0.7)  # faster for seniors
                elif experience_level == "junior":
                    hours = int(hours * 1.2)  # more time for juniors

                roadmap.append({
                    "week": current_week,
                    "title": f"Week {current_week}: {skill_info['skill']} — {level.title()}",
                    "skill": skill_info["skill"],
                    "focus": f"{level.title()} {skill_info['skill']}: {', '.join(topics[:2])}",
                    "tasks": topics + [f"Build: {p}" for p in projects[:1]],
                    "hours": f"{hours}-{hours+4}",
                    "difficulty": level,
                    "priority": skill_info["priority"],
                    "gap_severity": skill_info["gap_severity"],
                    "resources": self._get_resources(skill_name, level),
                    "skills_covered": [skill_info["skill"]],
                    "adaptive_note": self._get_adaptive_note(experience_level, level, skill_info),
                })
                current_week += 1

        # Fill remaining weeks with review/capstone
        while current_week <= total_weeks:
            roadmap.append({
                "week": current_week,
                "title": f"Week {current_week}: Capstone & Portfolio",
                "skill": "Review",
                "focus": "Apply all learned skills in a capstone project",
                "tasks": [
                    "Build a comprehensive portfolio project combining learned skills",
                    "Update resume with new skills and certifications",
                    "Practice mock interviews for new skills",
                    "Contribute to an open-source project",
                ],
                "hours": "10-15",
                "difficulty": "advanced",
                "priority": "🟢 Nice to Have",
                "gap_severity": 0,
                "resources": ["GitHub portfolio guide", "Resume tips", "Interview prep"],
                "skills_covered": [s["skill"] for s in prioritized_skills[:3]],
                "adaptive_note": "Consolidation phase — demonstrate your new skills through projects",
            })
            current_week += 1

        return roadmap

    def _get_levels_to_learn(self, current: str, experience: str) -> List[str]:
        """Determine which levels a user needs to learn."""
        all_levels = ["beginner", "intermediate", "advanced"]
        level_idx = {"none": -1, "beginner": 0, "intermediate": 1, "advanced": 2}
        start = level_idx.get(current, -1) + 1

        # Seniors can skip beginner level if they have some exposure
        if experience == "senior" and start == 0:
            start = 1  # jump to intermediate

        return all_levels[start:]

    def _get_resources(self, skill: str, level: str) -> List[str]:
        """Get relevant resources for a skill level."""
        resource_map = {
            "python": ["Python.org docs", "Real Python", "Automate the Boring Stuff"],
            "javascript": ["MDN Web Docs", "JavaScript.info", "freeCodeCamp"],
            "react": ["react.dev", "React Router docs", "Kent C. Dodds blog"],
            "docker": ["Docker docs", "Docker Curriculum", "Play with Docker"],
            "aws": ["AWS Skill Builder", "AWS Free Tier", "Stephane Maarek"],
            "sql": ["SQLBolt", "Mode Analytics SQL", "LeetCode SQL"],
            "machine learning": ["Andrew Ng Coursera", "Kaggle Learn", "scikit-learn docs"],
            "kubernetes": ["K8s docs", "Katacoda", "KodeKloud"],
            "git": ["Git-SCM book", "GitHub Skills", "Oh My Git"],
            "typescript": ["TS Handbook", "Total TypeScript", "Type Challenges"],
        }
        return resource_map.get(skill, ["Official documentation", "YouTube tutorials", "Hands-on exercises"])

    def _get_adaptive_note(self, experience: str, level: str, skill_info: Dict) -> str:
        if experience == "senior" and level == "beginner":
            return "Accelerated path — you can review basics quickly given your experience"
        elif experience == "junior" and level == "advanced":
            return "Stretch goal — take extra time if needed, focus on understanding over speed"
        elif skill_info["gap_severity"] > 0.8:
            return f"Critical gap — this skill is essential for your target role"
        elif skill_info["gap_severity"] < 0.3:
            return "Minor refresh — you already have a good foundation"
        return "Standard progression — follow the tasks and build the project"

    def _generate_milestones(self, roadmap: List[Dict], total_weeks: int) -> List[Dict]:
        """Generate progress milestones."""
        milestones = []
        quarter = max(1, total_weeks // 4)

        milestone_labels = [
            ("🏁 Foundation Complete", "Core skills basics covered"),
            ("🔧 Building Proficiency", "Intermediate skills developing"),
            ("⚡ Advanced Progress", "Advanced concepts in progress"),
            ("🏆 Career Ready", "All skills at target level"),
        ]

        for i, (label, desc) in enumerate(milestone_labels):
            week_target = min(total_weeks, (i + 1) * quarter)
            skills_by_then = list(set(
                s for w in roadmap[:week_target] for s in w.get("skills_covered", [])
            ))
            milestones.append({
                "week": week_target,
                "label": label,
                "description": desc,
                "skills_completed": skills_by_then[:5],
            })

        return milestones

    def _generate_insights(self, experience: str, priorities: List[Dict], job_role: str) -> List[str]:
        """Generate adaptive insights about the learning path."""
        insights = []

        critical = [p for p in priorities if p["gap_severity"] > 0.7]
        if critical:
            skills = ", ".join([p["skill"] for p in critical[:3]])
            insights.append(f"🔴 Critical skills gap detected: {skills} — these should be your top priority")

        if experience == "junior":
            insights.append("📚 As a junior, focus on building strong fundamentals before diving into advanced topics")
            insights.append("🎯 Target entry-level positions while building skills — experience accelerates learning")
        elif experience == "senior":
            insights.append("⚡ With your experience, you can accelerate through basics — focus on advanced concepts")
            insights.append("🏗️ Leverage your existing knowledge to learn by building larger, complex projects")

        total_demand = np.mean([p["market_demand"] for p in priorities]) if priorities else 0
        if total_demand > 0.85:
            insights.append(f"📈 The skills for {job_role} are in very high market demand — great career move!")

        insights.append("💡 Consistency beats intensity — 1-2 hours daily is more effective than weekend cramming")

        return insights


# =====================================================================
#  QUICK API (singleton)
# =====================================================================
_roadmap_instance = None

def generate_dynamic_roadmap(
    resume_text: str,
    job_role: str,
    target_skills: List[str],
    job_description: str = "",
    weeks: int = 8
) -> Dict:
    """Quick-use function for dynamic roadmap generation."""
    global _roadmap_instance
    if _roadmap_instance is None:
        _roadmap_instance = DynamicRoadmapGenerator()
    return _roadmap_instance.generate_dynamic_roadmap(
        resume_text, job_role, target_skills, job_description, weeks
    )
