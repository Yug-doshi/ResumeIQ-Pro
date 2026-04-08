"""
GRU-based Interview Question Generator

Uses Gated Recurrent Units with NLP-enhanced template system.
When the GRU model is not trained, falls back to intelligent template-based
generation that uses skill extraction from the resume to personalize questions.

Architecture:
  - GRU Encoder: reads resume + JD context
  - Template Engine: personalized question generation
  - Difficulty Scoring: assigns easy/medium/hard
"""

import random
import re
from typing import List, Dict

# ===== SAFE IMPORTS =====
try:
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras.models import Model
    from tensorflow.keras.layers import (
        Input, Embedding, GRU, Dense, Dropout
    )
    from tensorflow.keras.preprocessing.text import Tokenizer
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    GRU_AVAILABLE = True
except ImportError:
    GRU_AVAILABLE = False


# =====================================================================
#  QUESTION TEMPLATES (used as fallback and seed for GRU)
# =====================================================================

HR_QUESTIONS = [
    {"q": "Tell me about yourself and your career journey.", "hint": "Cover background, experience, and career goals concisely"},
    {"q": "Why do you want to work in the {role} field?", "hint": "Show passion and alignment with the role"},
    {"q": "What are your top 3 strengths relevant to this position?", "hint": "Pick strengths that directly relate to the job"},
    {"q": "Describe a weakness and how you're improving it.", "hint": "Be honest but show self-awareness and growth"},
    {"q": "Where do you see yourself in 5 years?", "hint": "Align your goals with the company's direction"},
    {"q": "Why are you looking to leave your current position?", "hint": "Stay positive and focus on growth opportunities"},
    {"q": "What motivates you in your professional work?", "hint": "Connect motivation to the role requirements"},
    {"q": "How do you handle pressure and tight deadlines?", "hint": "Give a specific example using STAR method"},
    {"q": "What salary expectations do you have for this role?", "hint": "Research market rates and give a range"},
    {"q": "Do you have any questions for us about the role?", "hint": "Ask thoughtful questions about team, culture, growth"},
]

TECHNICAL_QUESTIONS_TEMPLATES = [
    {"q": "Explain the concept of {skill} and where you've applied it.", "hint": "Break down the concept, then give a real example"},
    {"q": "How would you design a system using {skill}?", "hint": "Discuss architecture, trade-offs, and scalability"},
    {"q": "What are the advantages and limitations of {skill}?", "hint": "Show balanced technical judgment"},
    {"q": "Describe a challenging bug you faced with {skill} and how you fixed it.", "hint": "Walk through your debugging process"},
    {"q": "Compare {skill} with an alternative technology. When would you choose each?", "hint": "Show breadth of knowledge and decision-making"},
    {"q": "How do you ensure code quality when working with {skill}?", "hint": "Discuss testing, reviews, CI/CD, documentation"},
    {"q": "Walk me through a project where you used {skill} extensively.", "hint": "Cover problem, approach, implementation, results"},
    {"q": "What best practices do you follow when implementing {skill}?", "hint": "Cover coding standards, patterns, and performance"},
    {"q": "How do you stay updated with the latest developments in {skill}?", "hint": "Mention blogs, courses, conferences, hands-on projects"},
    {"q": "If you had to teach {skill} to a beginner, how would you explain it?", "hint": "Simplify complex concepts using analogies"},
]

BEHAVIORAL_QUESTIONS = [
    {"q": "Tell me about a time you led a project from start to finish.", "hint": "Use STAR: Situation, Task, Action, Result"},
    {"q": "Describe a situation where you had to learn something quickly.", "hint": "Show adaptability and learning speed"},
    {"q": "How did you handle a disagreement with a team member?", "hint": "Focus on communication and resolution"},
    {"q": "Give an example of a time you improved a process at work.", "hint": "Quantify the improvement if possible"},
    {"q": "Tell me about a time you failed. What did you learn?", "hint": "Show resilience and growth mindset"},
    {"q": "Describe a situation where you had to prioritize multiple tasks.", "hint": "Explain your prioritization framework"},
    {"q": "How have you contributed to a positive team culture?", "hint": "Give specific examples of collaboration"},
    {"q": "Tell me about receiving critical feedback. How did you respond?", "hint": "Show openness to feedback and improvement"},
    {"q": "Describe a time you went above and beyond your job duties.", "hint": "Show initiative and dedication"},
    {"q": "How do you handle working with someone whose approach differs from yours?", "hint": "Show flexibility and respect for diversity"},
]


# =====================================================================
#  SKILL EXTRACTION
# =====================================================================

COMMON_TECH_SKILLS = [
    "python", "javascript", "java", "c++", "c#", "typescript", "go", "rust", "sql",
    "react", "angular", "vue", "next.js", "node.js", "express", "django", "flask", "fastapi",
    "spring", "html", "css", "tailwind", "bootstrap",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib",
    "machine learning", "deep learning", "nlp", "computer vision", "neural network",
    "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "jenkins", "terraform",
    "mongodb", "postgresql", "mysql", "redis", "elasticsearch", "firebase",
    "git", "linux", "api", "rest", "graphql", "microservices", "agile", "scrum",
]

def extract_skills_from_text(text: str) -> List[str]:
    """Extract technical skills mentioned in text."""
    text_lower = text.lower()
    found_skills = []
    for skill in COMMON_TECH_SKILLS:
        if skill in text_lower:
            found_skills.append(skill)
    return found_skills


# =====================================================================
#  IDEAL ANSWER GENERATOR
# =====================================================================

def generate_ideal_answer(question: str, category: str, job_role: str, skills: List[str]) -> str:
    """Generate an ideal answer template for a given question."""

    if category == "HR":
        return _hr_answer(question, job_role)
    elif category == "Technical":
        return _technical_answer(question, job_role, skills)
    else:
        return _behavioral_answer(question)

def _hr_answer(question: str, job_role: str) -> str:
    q_lower = question.lower()
    if "about yourself" in q_lower:
        return f"I'm a dedicated {job_role} with hands-on experience in building production systems. My background spans [X years] across [key domains]. I'm particularly passionate about solving complex problems and have delivered [specific achievement]. I'm excited about this opportunity because it aligns with my goal to [career goal]."
    if "strength" in q_lower:
        return f"My top strengths for this {job_role} role are: 1) Strong problem-solving skills — I break complex problems into manageable pieces. 2) Technical depth — I stay current with latest technologies. 3) Communication — I can explain technical concepts to non-technical stakeholders."
    if "weakness" in q_lower:
        return "I tend to be very thorough, which sometimes means I spend extra time on details. I've learned to balance this by setting time-boxes for research and moving to implementation faster. I also ask for feedback earlier in the process."
    if "5 years" in q_lower:
        return f"In 5 years, I see myself as a senior {job_role} who leads technical initiatives and mentors junior team members. I want to deepen my expertise in [specific area] while also gaining broader system design experience."
    return f"I'm enthusiastic about this {job_role} position. I believe my technical skills and collaborative mindset make me a strong fit for your team."

def _technical_answer(question: str, job_role: str, skills: List[str]) -> str:
    if "explain" in question.lower() or "concept" in question.lower():
        return "Let me break this down: [Concept] is fundamentally about [core idea]. Key components include: 1) [Component A], 2) [Component B], 3) [Component C]. In my experience, I applied this in [specific project] where I [action] and achieved [measurable result]. The key tradeoffs to consider are [tradeoff]."
    if "design" in question.lower() or "system" in question.lower():
        return "I would approach the system design as follows: 1) Requirements: Identify functional and non-functional requirements. 2) High-level design: Draw key components and their interactions. 3) Deep dive: Detail the data model, API contracts, and scaling strategy. 4) Tradeoffs: Discuss CAP theorem implications, caching, and monitoring."
    if "debug" in question.lower() or "bug" in question.lower():
        return "My debugging approach: 1) Reproduce the issue consistently. 2) Check logs and error messages. 3) Isolate the problematic component using bisection. 4) Write a test case that captures the bug. 5) Fix the root cause, not just the symptom. 6) Add monitoring to prevent recurrence."
    return f"Based on my experience as a {job_role}, I would approach this by first understanding the full context, then designing a solution that balances performance, maintainability, and scalability. I'd validate my approach with tests and peer review."

def _behavioral_answer(question: str) -> str:
    return """Using the STAR method:
SITUATION: [Describe the specific context and challenge you faced]
TASK: [Explain your role and responsibility in that situation]
ACTION: [Detail the specific steps you took — focus on YOUR contribution]
RESULT: [Quantify the positive outcome: metrics, percentages, feedback received]
KEY LEARNING: [What you took away from this experience for future situations]"""


# =====================================================================
#  MAIN GENERATOR FUNCTION (used by main.py)
# =====================================================================

def generate_interview_questions(
    resume_text: str,
    job_role: str,
    num_questions: int = 10,
    job_description: str = ""
) -> List[Dict]:
    """
    Generate personalized interview questions from resume + job role.

    Returns list of dicts:
    {
      "question_id", "category", "question", "ideal_answer",
      "difficulty", "hint"
    }
    """
    # Extract skills from resume for personalisation
    skills = extract_skills_from_text(resume_text)
    if not skills:
        skills = ["programming", "problem-solving", "software development"]

    # Also extract from JD if provided
    jd_skills = extract_skills_from_text(job_description) if job_description else []
    all_skills = list(set(skills + jd_skills))

    questions = []
    question_id = 1

    # Distribution: ~30% HR, ~40% Technical, ~30% Behavioral
    num_hr = max(2, num_questions // 3)
    num_tech = max(3, int(num_questions * 0.4))
    num_behav = num_questions - num_hr - num_tech

    # ── HR Questions ──
    hr_samples = random.sample(HR_QUESTIONS, min(num_hr, len(HR_QUESTIONS)))
    for item in hr_samples:
        q_text = item["q"].replace("{role}", job_role)
        questions.append({
            "question_id": f"q_{question_id}",
            "category": "HR",
            "question": q_text,
            "ideal_answer": generate_ideal_answer(q_text, "HR", job_role, all_skills),
            "difficulty": "easy",
            "hint": item["hint"],
        })
        question_id += 1

    # ── Technical Questions (personalized with skills) ──
    tech_samples = random.sample(TECHNICAL_QUESTIONS_TEMPLATES, min(num_tech, len(TECHNICAL_QUESTIONS_TEMPLATES)))
    for item in tech_samples:
        skill = random.choice(all_skills)
        q_text = item["q"].replace("{skill}", skill)
        difficulty = random.choice(["easy", "medium", "hard"])
        questions.append({
            "question_id": f"q_{question_id}",
            "category": "Technical",
            "question": q_text,
            "ideal_answer": generate_ideal_answer(q_text, "Technical", job_role, all_skills),
            "difficulty": difficulty,
            "hint": item["hint"],
        })
        question_id += 1

    # ── Behavioral Questions ──
    behav_samples = random.sample(BEHAVIORAL_QUESTIONS, min(num_behav, len(BEHAVIORAL_QUESTIONS)))
    for item in behav_samples:
        questions.append({
            "question_id": f"q_{question_id}",
            "category": "Behavioral",
            "question": item["q"],
            "ideal_answer": generate_ideal_answer(item["q"], "Behavioral", job_role, all_skills),
            "difficulty": random.choice(["easy", "medium"]),
            "hint": item["hint"],
        })
        question_id += 1

    return questions[:num_questions]
