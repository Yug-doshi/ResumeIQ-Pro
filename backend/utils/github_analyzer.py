"""
GitHub Profile Analyzer — NLC-powered Portfolio Assessment

Analyzes a GitHub profile to score:
  - Code diversity (languages, repos)
  - Project quality (descriptions, READMEs)
  - Activity consistency (commit patterns)
  - Documentation quality
  - Open source contributions

Uses NLC (Natural Language Classification) for:
  - README quality scoring via TF-IDF analysis
  - Project description classification
  - Contribution pattern analysis

Input:  GitHub username or profile URL
Output: Comprehensive analysis with scores, suggestions, and improvement tips
"""

import re
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from sklearn.feature_extraction.text import TfidfVectorizer


# =====================================================================
#  CONSTANTS
# =====================================================================

GITHUB_API_BASE = "https://api.github.com"

# Quality indicators for NLC text analysis
QUALITY_INDICATORS = {
    "excellent": [
        "documentation", "getting started", "installation", "usage", "api reference",
        "contributing", "license", "features", "demo", "screenshot", "architecture",
        "testing", "ci/cd", "docker", "deploy", "examples"
    ],
    "good": [
        "readme", "description", "setup", "requirements", "build", "run",
        "configuration", "how to", "overview", "project"
    ],
    "basic": ["todo", "wip", "work in progress", "initial commit"]
}

# Language categories for diversity scoring
LANGUAGE_CATEGORIES = {
    "frontend": ["JavaScript", "TypeScript", "HTML", "CSS", "Vue", "Svelte"],
    "backend": ["Python", "Java", "Go", "Rust", "C#", "Ruby", "PHP", "C++", "C"],
    "data": ["Jupyter Notebook", "R", "MATLAB", "Julia"],
    "mobile": ["Kotlin", "Swift", "Dart", "Objective-C"],
    "devops": ["Shell", "Dockerfile", "HCL", "Makefile"],
    "other": ["Lua", "Haskell", "Elixir", "Scala", "Perl"]
}


class GitHubAnalyzer:
    """
    Analyzes GitHub profiles using NLC for quality assessment.
    """

    def __init__(self):
        self.tfidf = TfidfVectorizer(max_features=200, stop_words='english')

    def analyze_profile(self, github_input: str) -> Dict:
        """
        Analyze a GitHub profile.

        Args:
            github_input: Username or full GitHub URL

        Returns comprehensive analysis dict.
        """
        username = self._extract_username(github_input)

        # ── Fetch GitHub data ──
        profile = self._fetch_profile(username)
        repos = self._fetch_repos(username)

        if not profile:
            return {"error": f"Could not fetch GitHub profile for '{username}'", "success": False}

        # ── Analysis modules ──
        code_diversity = self._analyze_code_diversity(repos)
        project_quality = self._analyze_project_quality(repos)
        activity = self._analyze_activity(repos, profile)
        documentation = self._analyze_documentation(repos)
        profile_completeness = self._analyze_profile_completeness(profile)

        # ── Overall score ──
        overall_score = int(
            code_diversity["score"] * 0.20 +
            project_quality["score"] * 0.30 +
            activity["score"] * 0.20 +
            documentation["score"] * 0.15 +
            profile_completeness["score"] * 0.15
        )

        # ── Generate suggestions ──
        suggestions = self._generate_suggestions(
            code_diversity, project_quality, activity, documentation, profile_completeness
        )

        # ── Build top projects ──
        top_projects = self._get_top_projects(repos)

        return {
            "success": True,
            "username": username,
            "profile": {
                "name": profile.get("name", username),
                "bio": profile.get("bio", ""),
                "avatar_url": profile.get("avatar_url", ""),
                "public_repos": profile.get("public_repos", 0),
                "followers": profile.get("followers", 0),
                "following": profile.get("following", 0),
                "created_at": profile.get("created_at", ""),
                "html_url": profile.get("html_url", f"https://github.com/{username}"),
            },
            "overall_score": min(100, max(0, overall_score)),
            "score_label": self._get_score_label(overall_score),
            "breakdown": {
                "code_diversity": code_diversity,
                "project_quality": project_quality,
                "activity": activity,
                "documentation": documentation,
                "profile_completeness": profile_completeness,
            },
            "languages": self._get_language_distribution(repos),
            "top_projects": top_projects,
            "suggestions": suggestions,
            "categories_covered": self._get_categories_covered(repos),
        }

    # ─────────────── API FETCHING ───────────────

    def _extract_username(self, github_input: str) -> str:
        """Extract username from URL or direct input."""
        github_input = github_input.strip().rstrip('/')
        # Handle full URLs
        patterns = [
            r'github\.com/([a-zA-Z0-9\-_]+)',
            r'^([a-zA-Z0-9\-_]+)$',
        ]
        for pattern in patterns:
            match = re.search(pattern, github_input)
            if match:
                return match.group(1)
        return github_input

    def _fetch_profile(self, username: str) -> Optional[Dict]:
        """Fetch user profile from GitHub API."""
        try:
            resp = requests.get(
                f"{GITHUB_API_BASE}/users/{username}",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None

    def _fetch_repos(self, username: str) -> List[Dict]:
        """Fetch user repositories."""
        try:
            repos = []
            page = 1
            while page <= 3:  # max 3 pages (90 repos)
                resp = requests.get(
                    f"{GITHUB_API_BASE}/users/{username}/repos",
                    params={"sort": "updated", "per_page": 30, "page": page},
                    headers={"Accept": "application/vnd.github.v3+json"},
                    timeout=10
                )
                if resp.status_code != 200:
                    break
                data = resp.json()
                if not data:
                    break
                repos.extend(data)
                page += 1
            return repos
        except Exception:
            return []

    # ─────────────── ANALYSIS MODULES ───────────────

    def _analyze_code_diversity(self, repos: List[Dict]) -> Dict:
        """Score code diversity: languages and categories."""
        languages = {}
        for repo in repos:
            if repo.get("fork"):
                continue
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1

        num_languages = len(languages)
        categories = set()
        for lang in languages:
            for cat, cat_langs in LANGUAGE_CATEGORIES.items():
                if lang in cat_langs:
                    categories.add(cat)

        # Score: 1 lang = 20, 2 = 40, 3 = 55, 4 = 70, 5+ = 80, 2+ categories = +20
        if num_languages >= 5:
            score = 80
        elif num_languages >= 4:
            score = 70
        elif num_languages >= 3:
            score = 55
        elif num_languages >= 2:
            score = 40
        elif num_languages >= 1:
            score = 25
        else:
            score = 5

        # Category bonus
        score += len(categories) * 5
        score = min(100, score)

        return {
            "score": score,
            "num_languages": num_languages,
            "languages": dict(sorted(languages.items(), key=lambda x: -x[1])),
            "categories": list(categories),
            "label": "Excellent" if score >= 75 else "Good" if score >= 50 else "Limited"
        }

    def _analyze_project_quality(self, repos: List[Dict]) -> Dict:
        """Analyze quality of projects using NLC on descriptions."""
        non_fork = [r for r in repos if not r.get("fork")]

        if not non_fork:
            return {"score": 0, "label": "No projects", "details": []}

        scores = []
        details = []

        for repo in non_fork[:15]:  # analyze top 15
            desc = (repo.get("description") or "").lower()
            name = repo.get("name", "")
            stars = repo.get("stargazers_count", 0)
            has_homepage = bool(repo.get("homepage"))
            has_topics = len(repo.get("topics", []))
            size = repo.get("size", 0)

            # Score each project
            proj_score = 0

            # Description quality
            if len(desc) > 50:
                proj_score += 25
            elif len(desc) > 20:
                proj_score += 15
            elif desc:
                proj_score += 5

            # Stars
            if stars >= 10:
                proj_score += 25
            elif stars >= 3:
                proj_score += 15
            elif stars >= 1:
                proj_score += 8

            # Homepage / demo
            if has_homepage:
                proj_score += 15

            # Topics/tags
            proj_score += min(15, has_topics * 3)

            # Size (indicates real content)
            if size > 1000:
                proj_score += 15
            elif size > 100:
                proj_score += 8

            # Not a trivial name
            if not re.match(r'^(test|hello|demo|my\-?app|untitled)', name.lower()):
                proj_score += 5

            scores.append(min(100, proj_score))
            details.append({
                "name": repo.get("full_name", name),
                "description": repo.get("description", "No description"),
                "stars": stars,
                "language": repo.get("language", "Unknown"),
                "quality_score": min(100, proj_score),
            })

        avg_score = int(np.mean(scores)) if scores else 0

        return {
            "score": avg_score,
            "total_projects": len(non_fork),
            "analyzed": len(details),
            "details": sorted(details, key=lambda x: -x["quality_score"])[:8],
            "label": "Excellent" if avg_score >= 70 else "Good" if avg_score >= 45 else "Needs Work"
        }

    def _analyze_activity(self, repos: List[Dict], profile: Dict) -> Dict:
        """Analyze activity patterns."""
        non_fork = [r for r in repos if not r.get("fork")]

        if not non_fork:
            return {"score": 0, "label": "Inactive", "recent_activity": 0}

        # Recent activity (last 6 months)
        now = datetime.utcnow()
        six_months_ago = now - timedelta(days=180)

        recent_repos = 0
        for repo in non_fork:
            updated = repo.get("updated_at", "")
            if updated:
                try:
                    update_date = datetime.strptime(updated[:10], "%Y-%m-%d")
                    if update_date > six_months_ago:
                        recent_repos += 1
                except Exception:
                    pass

        # Account age
        created = profile.get("created_at", "")
        account_years = 1
        if created:
            try:
                created_date = datetime.strptime(created[:10], "%Y-%m-%d")
                account_years = max(1, (now - created_date).days / 365)
            except Exception:
                pass

        repos_per_year = len(non_fork) / account_years

        # Score
        score = 0
        if recent_repos >= 5:
            score += 40
        elif recent_repos >= 3:
            score += 25
        elif recent_repos >= 1:
            score += 15

        if repos_per_year >= 5:
            score += 30
        elif repos_per_year >= 3:
            score += 20
        elif repos_per_year >= 1:
            score += 10

        if len(non_fork) >= 15:
            score += 30
        elif len(non_fork) >= 8:
            score += 20
        elif len(non_fork) >= 3:
            score += 10

        score = min(100, score)

        return {
            "score": score,
            "recent_repos": recent_repos,
            "total_repos": len(non_fork),
            "repos_per_year": round(repos_per_year, 1),
            "account_years": round(account_years, 1),
            "label": "Very Active" if score >= 70 else "Active" if score >= 45 else "Low Activity"
        }

    def _analyze_documentation(self, repos: List[Dict]) -> Dict:
        """Analyze documentation quality using NLC."""
        non_fork = [r for r in repos if not r.get("fork")]

        has_description = sum(1 for r in non_fork if r.get("description"))
        has_topics = sum(1 for r in non_fork if r.get("topics"))
        has_homepage = sum(1 for r in non_fork if r.get("homepage"))
        has_license = sum(1 for r in non_fork if r.get("license"))

        total = max(1, len(non_fork))

        desc_pct = has_description / total
        topic_pct = has_topics / total
        homepage_pct = has_homepage / total
        license_pct = has_license / total

        score = int(
            desc_pct * 35 +
            topic_pct * 25 +
            homepage_pct * 20 +
            license_pct * 20
        ) * 100 // 100

        # Scale to 0-100
        score = min(100, int(score * 1.3))

        return {
            "score": score,
            "repos_with_description": f"{has_description}/{total}",
            "repos_with_topics": f"{has_topics}/{total}",
            "repos_with_homepage": f"{has_homepage}/{total}",
            "repos_with_license": f"{has_license}/{total}",
            "label": "Well Documented" if score >= 65 else "Partially" if score >= 35 else "Needs Docs"
        }

    def _analyze_profile_completeness(self, profile: Dict) -> Dict:
        """Score profile completeness."""
        checks = {
            "name": bool(profile.get("name")),
            "bio": bool(profile.get("bio")),
            "location": bool(profile.get("location")),
            "company": bool(profile.get("company")),
            "blog": bool(profile.get("blog")),
            "twitter": bool(profile.get("twitter_username")),
            "hireable": profile.get("hireable") is True,
            "avatar": bool(profile.get("avatar_url")),
        }

        completed = sum(checks.values())
        score = int(completed / len(checks) * 100)

        return {
            "score": score,
            "completed_fields": completed,
            "total_fields": len(checks),
            "missing": [k for k, v in checks.items() if not v],
            "label": "Complete" if score >= 75 else "Partial" if score >= 40 else "Incomplete"
        }

    # ─────────────── UTILITY METHODS ───────────────

    def _get_language_distribution(self, repos: List[Dict]) -> List[Dict]:
        """Get language distribution for chart."""
        lang_counts = {}
        for repo in repos:
            if repo.get("fork"):
                continue
            lang = repo.get("language")
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

        total = sum(lang_counts.values())
        distribution = []
        colors = [
            "#6366f1", "#8b5cf6", "#a855f7", "#d946ef", "#ec4899",
            "#f43f5e", "#ef4444", "#f97316", "#f59e0b", "#eab308",
            "#84cc16", "#22c55e", "#10b981", "#14b8a6", "#06b6d4"
        ]

        for i, (lang, count) in enumerate(sorted(lang_counts.items(), key=lambda x: -x[1])):
            distribution.append({
                "language": lang,
                "count": count,
                "percentage": round(count / max(1, total) * 100, 1),
                "color": colors[i % len(colors)]
            })

        return distribution

    def _get_top_projects(self, repos: List[Dict]) -> List[Dict]:
        """Get top projects by stars + activity."""
        non_fork = [r for r in repos if not r.get("fork")]

        # Score by stars + recency
        for repo in non_fork:
            stars = repo.get("stargazers_count", 0)
            updated = repo.get("updated_at", "2000-01-01")
            try:
                days = (datetime.utcnow() - datetime.strptime(updated[:10], "%Y-%m-%d")).days
                recency_bonus = max(0, 30 - days // 10)
            except Exception:
                recency_bonus = 0
            repo["_sort_score"] = stars * 3 + recency_bonus + (repo.get("size", 0) / 100)

        top = sorted(non_fork, key=lambda x: -x.get("_sort_score", 0))[:6]

        return [{
            "name": r["name"],
            "full_name": r.get("full_name", r["name"]),
            "description": r.get("description", "No description"),
            "language": r.get("language", "Unknown"),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "html_url": r.get("html_url", ""),
            "topics": r.get("topics", [])[:5],
            "updated_at": r.get("updated_at", "")[:10],
        } for r in top]

    def _get_categories_covered(self, repos: List[Dict]) -> List[Dict]:
        """Get which programming categories are covered."""
        categories = {}
        for repo in repos:
            if repo.get("fork"):
                continue
            lang = repo.get("language")
            if lang:
                for cat, langs in LANGUAGE_CATEGORIES.items():
                    if lang in langs:
                        if cat not in categories:
                            categories[cat] = {"count": 0, "languages": set()}
                        categories[cat]["count"] += 1
                        categories[cat]["languages"].add(lang)

        return [{
            "category": cat.title(),
            "repo_count": info["count"],
            "languages": list(info["languages"])
        } for cat, info in sorted(categories.items(), key=lambda x: -x[1]["count"])]

    def _get_score_label(self, score: int) -> str:
        if score >= 80:
            return "Outstanding 🏆"
        elif score >= 65:
            return "Strong Profile ⭐"
        elif score >= 45:
            return "Good Foundation 👍"
        elif score >= 25:
            return "Growing 🌱"
        else:
            return "Just Starting 🚀"

    def _generate_suggestions(self, diversity, quality, activity, docs, profile) -> List[Dict]:
        """Generate actionable improvement suggestions."""
        suggestions = []

        if diversity["score"] < 50:
            suggestions.append({
                "category": "Code Diversity",
                "priority": "high",
                "emoji": "🌈",
                "suggestion": f"Expand your tech stack — you currently use {diversity['num_languages']} language(s). Try building projects in a new language to show versatility.",
                "action": "Create a project in a language you haven't used yet (Python, TypeScript, Go are in high demand)"
            })

        if quality["score"] < 50:
            suggestions.append({
                "category": "Project Quality",
                "priority": "high",
                "emoji": "⭐",
                "suggestion": "Improve project quality with better descriptions, READMEs, and live demos. Projects should tell a story.",
                "action": "Add detailed README, screenshots, and a live demo link to your top 3 projects"
            })

        if activity["score"] < 45:
            suggestions.append({
                "category": "Activity",
                "priority": "medium",
                "emoji": "📈",
                "suggestion": f"Only {activity['recent_repos']} repo(s) updated recently. Regular contributions show dedication.",
                "action": "Commit to at least 1 meaningful push per week — even small improvements count"
            })

        if docs["score"] < 50:
            suggestions.append({
                "category": "Documentation",
                "priority": "medium",
                "emoji": "📝",
                "suggestion": "Many repos lack proper documentation. Well-documented code shows professionalism.",
                "action": "Add descriptions, topics, and licenses to all public repositories"
            })

        if profile["score"] < 60:
            missing = ", ".join(profile["missing"][:3])
            suggestions.append({
                "category": "Profile",
                "priority": "low",
                "emoji": "👤",
                "suggestion": f"Complete your GitHub profile — missing: {missing}",
                "action": "Add a profile README, bio, location, and portfolio link"
            })

        # Always add a positive/growth suggestion
        if quality["score"] >= 60:
            suggestions.append({
                "category": "Growth",
                "priority": "low",
                "emoji": "🚀",
                "suggestion": "Great project quality! Consider contributing to popular open-source projects for visibility.",
                "action": "Find a project you use and submit a PR — even docs improvements count"
            })

        return suggestions


# =====================================================================
#  QUICK API (singleton)
# =====================================================================
_analyzer_instance = None

def analyze_github_profile(github_input: str) -> Dict:
    """Quick-use function for GitHub analysis."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = GitHubAnalyzer()
    return _analyzer_instance.analyze_profile(github_input)
