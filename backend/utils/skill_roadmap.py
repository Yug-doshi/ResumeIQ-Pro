"""
Skill Roadmap Generator — Week-by-week learning plan

Creates personalized learning roadmaps based on missing skills and job role.
Each week includes: title, focus area, tasks, estimated hours, and resources.
"""

from typing import List, Dict
import random


# =====================================================================
#  SKILL LEARNING PATHS — detailed curriculum per skill
# =====================================================================

SKILL_CURRICULUM = {
    "python": {
        "weeks_needed": 3,
        "path": [
            {"title": "Python Foundations", "focus": "Master core syntax, data structures, and functions", "tasks": ["Complete Python basics tutorial", "Practice 20 coding problems on LeetCode", "Build a CLI calculator program"], "hours": "10-12", "resources": ["Python Official Docs", "Automate the Boring Stuff (free book)", "HackerRank Python Track"]},
            {"title": "Python Intermediate", "focus": "OOP, file handling, and libraries", "tasks": ["Learn classes, inheritance, decorators", "Work with JSON, CSV, and API calls", "Build a web scraper with requests + BeautifulSoup"], "hours": "10-12", "resources": ["Real Python tutorials", "Python Crash Course book", "Corey Schafer YouTube"]},
            {"title": "Python Advanced", "focus": "Advanced patterns and project work", "tasks": ["Learn generators, context managers, async", "Write unit tests with pytest", "Build a complete REST API with FastAPI"], "hours": "12-15", "resources": ["Fluent Python book", "FastAPI documentation", "pytest docs"]},
        ],
    },
    "javascript": {
        "weeks_needed": 3,
        "path": [
            {"title": "JavaScript Basics", "focus": "Core JS: variables, functions, DOM manipulation", "tasks": ["Complete JS fundamentals course", "Build 5 mini DOM projects", "Learn ES6+ features: arrow functions, destructuring, promises"], "hours": "10-12", "resources": ["MDN Web Docs", "JavaScript.info", "freeCodeCamp JS curriculum"]},
            {"title": "Async JS & APIs", "focus": "Promises, async/await, fetch, APIs", "tasks": ["Build a weather app with API calls", "Learn error handling patterns", "Practice with public APIs (GitHub, News, etc.)"], "hours": "10-12", "resources": ["JavaScript30 (Wes Bos)", "You Don't Know JS (free book)", "MDN Async Guide"]},
            {"title": "Modern JS & Tooling", "focus": "Modules, bundlers, testing", "tasks": ["Set up a project with Vite", "Learn npm package management", "Write tests with Jest"], "hours": "8-10", "resources": ["Vite docs", "Jest docs", "Modern JS Tutorial"]},
        ],
    },
    "react": {
        "weeks_needed": 2,
        "path": [
            {"title": "React Fundamentals", "focus": "Components, props, state, hooks", "tasks": ["Build a todo app with useState, useEffect", "Learn component composition patterns", "Practice with forms and conditional rendering"], "hours": "12-15", "resources": ["React official docs (react.dev)", "Scrimba React course", "Kent C. Dodds blog"]},
            {"title": "React Advanced & Ecosystem", "focus": "Routing, state management, API integration", "tasks": ["Add React Router to your project", "Build a full-stack app with API calls", "Learn performance optimization: memo, useMemo, useCallback"], "hours": "12-15", "resources": ["React Router docs", "TanStack Query docs", "React Patterns (reactpatterns.com)"]},
        ],
    },
    "machine learning": {
        "weeks_needed": 3,
        "path": [
            {"title": "ML Foundations", "focus": "Statistics, math, and ML concepts", "tasks": ["Learn supervised vs unsupervised learning", "Implement linear regression from scratch", "Practice with scikit-learn basics"], "hours": "12-15", "resources": ["Andrew Ng ML Course (Coursera)", "StatQuest YouTube", "scikit-learn docs"]},
            {"title": "ML Algorithms", "focus": "Classification, clustering, ensembles", "tasks": ["Implement decision trees and random forests", "Build a classification project (Titanic/Iris)", "Learn cross-validation and hyperparameter tuning"], "hours": "12-15", "resources": ["Hands-On ML book (Geron)", "Kaggle Learn courses", "Google ML Crash Course"]},
            {"title": "Deep Learning Intro", "focus": "Neural networks with TensorFlow/Keras", "tasks": ["Build a simple neural network", "Train a CNN for image classification", "Learn about overfitting and regularization"], "hours": "15-18", "resources": ["TensorFlow official tutorials", "fast.ai course", "Deep Learning book (Goodfellow)"]},
        ],
    },
    "docker": {
        "weeks_needed": 1,
        "path": [
            {"title": "Docker Essentials", "focus": "Containers, images, Docker Compose", "tasks": ["Install Docker and run first container", "Write Dockerfile for a Python app", "Create multi-container setup with Docker Compose", "Push image to Docker Hub"], "hours": "8-10", "resources": ["Docker official getting-started", "Docker Curriculum (docker-curriculum.com)", "TechWorld with Nana YouTube"]},
        ],
    },
    "aws": {
        "weeks_needed": 2,
        "path": [
            {"title": "AWS Core Services", "focus": "EC2, S3, IAM, RDS fundamentals", "tasks": ["Set up AWS free tier account", "Launch an EC2 instance and SSH into it", "Create S3 buckets and upload files", "Set up IAM users and policies"], "hours": "10-12", "resources": ["AWS Free Tier", "AWS Skill Builder", "Stephane Maarek Udemy"]},
            {"title": "AWS for Developers", "focus": "Lambda, API Gateway, deployment", "tasks": ["Deploy a serverless function with Lambda", "Set up API Gateway + Lambda integration", "Deploy a full app using Elastic Beanstalk or ECS"], "hours": "10-12", "resources": ["AWS Lambda docs", "Serverless Framework", "AWS Well-Architected"]},
        ],
    },
    "sql": {
        "weeks_needed": 1,
        "path": [
            {"title": "SQL Mastery", "focus": "Queries, joins, aggregations, optimization", "tasks": ["Complete SQL basics: SELECT, WHERE, JOIN", "Practice complex queries with subqueries and CTEs", "Learn database design and normalization", "Optimize slow queries with indexes and EXPLAIN"], "hours": "8-10", "resources": ["SQLBolt (interactive)", "Mode Analytics SQL Tutorial", "LeetCode SQL problems"]},
        ],
    },
    "git": {
        "weeks_needed": 1,
        "path": [
            {"title": "Git & GitHub Mastery", "focus": "Version control, branching, collaboration", "tasks": ["Learn git add, commit, push, pull", "Master branching: feature branches, merge, rebase", "Create PRs and practice code reviews", "Set up a GitHub profile with pinned projects"], "hours": "6-8", "resources": ["Git official docs", "GitHub Skills (skills.github.com)", "Oh My Git (interactive game)"]},
        ],
    },
}

# Default path for skills not in the curriculum
DEFAULT_SKILL_PATH = [
    {"title": "Foundation & Theory", "focus": "Learn core concepts and fundamentals", "tasks": ["Complete an introduction course/tutorial", "Read documentation and official guides", "Practice with 3-5 hands-on exercises"], "hours": "8-10", "resources": ["Official documentation", "YouTube tutorials", "freeCodeCamp/Coursera"]},
    {"title": "Practical Application", "focus": "Build a project using this skill", "tasks": ["Build a real-world mini project", "Integrate with your existing projects", "Write notes and create a cheat sheet"], "hours": "10-12", "resources": ["GitHub trending projects", "Dev.to tutorials", "Stack Overflow"]},
]


def generate_skill_roadmap(job_role: str, missing_skills: List[str], weeks: int = 8) -> List[Dict]:
    """
    Generate a week-by-week learning roadmap.

    Returns list of week objects:
    [
      {
        "week": 1,
        "title": str,
        "focus": str,
        "tasks": [str],
        "hours": str,
        "resources": [str],
        "skills_covered": [str]
      },
    ]
    """
    roadmap = []
    current_week = 1

    for skill in missing_skills:
        skill_lower = skill.lower().strip()
        curriculum = SKILL_CURRICULUM.get(skill_lower, None)

        if curriculum:
            for week_data in curriculum["path"]:
                if current_week > weeks:
                    break
                roadmap.append({
                    "week": current_week,
                    "title": f"Week {current_week}: {week_data['title']}",
                    "focus": week_data["focus"],
                    "tasks": week_data["tasks"],
                    "hours": week_data["hours"],
                    "resources": week_data["resources"],
                    "skills_covered": [skill],
                })
                current_week += 1
        else:
            # Use default path for unknown skills
            for week_data in DEFAULT_SKILL_PATH:
                if current_week > weeks:
                    break
                roadmap.append({
                    "week": current_week,
                    "title": f"Week {current_week}: Learn {skill} — {week_data['title']}",
                    "focus": f"{week_data['focus']} for {skill}",
                    "tasks": [t.replace("this skill", skill) for t in week_data["tasks"]],
                    "hours": week_data["hours"],
                    "resources": week_data["resources"],
                    "skills_covered": [skill],
                })
                current_week += 1

        if current_week > weeks:
            break

    # If we have remaining weeks, add review/portfolio weeks
    while current_week <= weeks:
        roadmap.append({
            "week": current_week,
            "title": f"Week {current_week}: Portfolio & Review",
            "focus": "Consolidate learning and build portfolio",
            "tasks": [
                "Review all skills learned so far",
                f"Build a capstone project combining learned skills for {job_role} role",
                "Update resume with new skills and projects",
                "Practice interview questions for new skills",
            ],
            "hours": "10-12",
            "resources": ["GitHub portfolio guide", "Resume optimization tips", "Interview prep resources"],
            "skills_covered": missing_skills[:3],
        })
        current_week += 1

    return roadmap
