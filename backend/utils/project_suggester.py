"""
Project Suggester — Maps missing skills to concrete portfolio projects

Each project includes:
  - Name, description, difficulty
  - Tech stack
  - Skills addressed
  - Estimated time
  - Key features to implement
"""

from typing import List, Dict
import random


# =====================================================================
#  PROJECT DATABASE — organized by skill
# =====================================================================

PROJECTS_BY_SKILL = {
    "python": [
        {"name": "Expense Tracker CLI", "description": "Build a command-line expense tracker with SQLite storage, CSV export, and monthly reports. Demonstrates file I/O, database operations, and clean code.", "tech_stack": ["Python", "SQLite", "argparse", "matplotlib"], "difficulty": "Beginner", "estimated_time": "1 week", "skills_addressed": ["python", "sql", "data visualization"]},
        {"name": "Web Scraper Dashboard", "description": "Automated web scraper that collects data from specified websites, stores in a database, and displays trends on a dashboard.", "tech_stack": ["Python", "BeautifulSoup", "Flask", "PostgreSQL", "Chart.js"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["python", "web scraping", "api", "databases"]},
    ],
    "javascript": [
        {"name": "Real-time Chat Application", "description": "Full-featured chat app with rooms, typing indicators, and message history using WebSocket.", "tech_stack": ["Node.js", "Socket.io", "Express", "MongoDB", "React"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["javascript", "node.js", "react", "mongodb"]},
        {"name": "Quiz Game Platform", "description": "Interactive quiz platform with categories, scoring, leaderboards, and timer functionality.", "tech_stack": ["JavaScript", "React", "Firebase", "TailwindCSS"], "difficulty": "Beginner", "estimated_time": "1 week", "skills_addressed": ["javascript", "react", "firebase"]},
    ],
    "react": [
        {"name": "Project Management Board", "description": "Kanban-style project board (like Trello) with drag-and-drop, task assignments, and real-time updates.", "tech_stack": ["React", "TypeScript", "TailwindCSS", "Supabase"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["react", "typescript", "state management"]},
        {"name": "E-commerce Storefront", "description": "Complete online store with product catalog, cart, checkout, and payment integration.", "tech_stack": ["React", "Next.js", "Stripe", "PostgreSQL", "TailwindCSS"], "difficulty": "Advanced", "estimated_time": "3 weeks", "skills_addressed": ["react", "next.js", "api", "databases"]},
    ],
    "machine learning": [
        {"name": "Sentiment Analysis API", "description": "ML-powered API that analyzes text sentiment (positive/negative/neutral) with confidence scores. Train on real review datasets.", "tech_stack": ["Python", "scikit-learn", "FastAPI", "NLTK", "Docker"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["machine learning", "nlp", "python", "api"]},
        {"name": "Movie Recommendation Engine", "description": "Collaborative filtering recommendation system that suggests movies based on user preferences and viewing history.", "tech_stack": ["Python", "pandas", "scikit-learn", "Flask", "React"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["machine learning", "python", "data analysis"]},
    ],
    "nlp": [
        {"name": "AI Chatbot with Intent Detection", "description": "Smart chatbot that classifies user intents and provides contextual responses. Uses TF-IDF and neural networks.", "tech_stack": ["Python", "TensorFlow", "spaCy", "FastAPI", "React"], "difficulty": "Advanced", "estimated_time": "3 weeks", "skills_addressed": ["nlp", "deep learning", "python", "api"]},
    ],
    "docker": [
        {"name": "Containerized Microservices App", "description": "Multi-service application with Docker Compose: API gateway, auth service, data service, and frontend.", "tech_stack": ["Docker", "Docker Compose", "Node.js", "PostgreSQL", "Nginx"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["docker", "microservices", "devops"]},
    ],
    "aws": [
        {"name": "Serverless URL Shortener", "description": "URL shortening service using AWS Lambda, API Gateway, and DynamoDB with analytics tracking.", "tech_stack": ["AWS Lambda", "API Gateway", "DynamoDB", "CloudFront", "Python"], "difficulty": "Intermediate", "estimated_time": "1 week", "skills_addressed": ["aws", "serverless", "python", "api"]},
    ],
    "sql": [
        {"name": "Analytics Dashboard with Complex Queries", "description": "Business analytics dashboard backed by complex SQL queries: CTEs, window functions, aggregations on a sample e-commerce dataset.", "tech_stack": ["PostgreSQL", "Python", "Flask/FastAPI", "React", "Recharts"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["sql", "data analysis", "api", "data visualization"]},
    ],
    "git": [
        {"name": "Open Source Contribution Portfolio", "description": "Contribute to 3 open source projects, fix issues, submit PRs, and document the process.", "tech_stack": ["Git", "GitHub", "Various"], "difficulty": "Beginner", "estimated_time": "2 weeks", "skills_addressed": ["git", "collaboration", "code review"]},
    ],
    "tensorflow": [
        {"name": "Image Classification Web App", "description": "Train a CNN model to classify images, deploy with TensorFlow.js for in-browser inference.", "tech_stack": ["TensorFlow", "Keras", "TensorFlow.js", "React", "Python"], "difficulty": "Advanced", "estimated_time": "3 weeks", "skills_addressed": ["tensorflow", "deep learning", "computer vision", "deployment"]},
    ],
    "api": [
        {"name": "RESTful Social Media API", "description": "Full REST API with authentication, CRUD operations, pagination, rate limiting, and documentation.", "tech_stack": ["FastAPI", "PostgreSQL", "JWT", "Docker", "Swagger"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["api", "python", "databases", "authentication"]},
    ],
}

# Generic fallback projects
GENERIC_PROJECTS = [
    {"name": "Personal Portfolio Website", "description": "Professional portfolio with project showcase, blog, and contact form. Responsive design with dark mode.", "tech_stack": ["React", "TailwindCSS", "Vercel"], "difficulty": "Beginner", "estimated_time": "1 week", "skills_addressed": ["web development", "react", "css"]},
    {"name": "Task Automation Tool", "description": "Automate repetitive tasks: data processing, report generation, email notifications.", "tech_stack": ["Python", "Schedule", "SMTP", "pandas"], "difficulty": "Beginner", "estimated_time": "1 week", "skills_addressed": ["python", "automation"]},
    {"name": "Full-Stack Blog Platform", "description": "Complete blog with user auth, markdown editor, comments, and SEO optimization.", "tech_stack": ["Next.js", "PostgreSQL", "TailwindCSS", "Prisma"], "difficulty": "Intermediate", "estimated_time": "2 weeks", "skills_addressed": ["react", "api", "databases", "authentication"]},
]


def suggest_projects(job_role: str, missing_skills: List[str], num_projects: int = 5) -> List[Dict]:
    """
    Suggest portfolio projects based on missing skills.

    Returns list of project dicts with name, description, tech_stack, etc.
    """
    projects = []
    seen_names = set()

    # Map each missing skill to project ideas
    for skill in missing_skills:
        skill_lower = skill.lower().strip()
        skill_projects = PROJECTS_BY_SKILL.get(skill_lower, [])

        for project in skill_projects:
            if project["name"] not in seen_names:
                projects.append(project)
                seen_names.add(project["name"])

    # If not enough projects, add generic ones
    for project in GENERIC_PROJECTS:
        if len(projects) >= num_projects:
            break
        if project["name"] not in seen_names:
            projects.append(project)
            seen_names.add(project["name"])

    # Shuffle and limit
    random.shuffle(projects)
    return projects[:num_projects]
