"""
Weakness Detector — Analyzes resume sections for weaknesses

Scans resume text and evaluates:
  - Skills section quality
  - Experience section quality
  - Projects section quality
  - Education section quality
  - Overall formatting

Returns per-section scores (0-100) and specific improvement tips.
"""

import re
from typing import Dict, List


def analyze_weaknesses(resume_text: str) -> Dict:
    """
    Analyze resume for weak sections.

    Returns:
    {
      "sections": {
        "skills": { "score": int, "status": str, "tips": [str] },
        "experience": { ... },
        "projects": { ... },
        "education": { ... },
        "formatting": { ... },
      },
      "overall_score": int,
      "critical_issues": [str],
      "strengths": [str]
    }
    """
    text_lower = resume_text.lower()
    sections = {}

    # ── Skills Section ──
    skills_score, skills_tips = _evaluate_skills(resume_text, text_lower)
    sections["skills"] = {
        "score": skills_score,
        "status": _status(skills_score),
        "tips": skills_tips,
    }

    # ── Experience Section ──
    exp_score, exp_tips = _evaluate_experience(resume_text, text_lower)
    sections["experience"] = {
        "score": exp_score,
        "status": _status(exp_score),
        "tips": exp_tips,
    }

    # ── Projects Section ──
    proj_score, proj_tips = _evaluate_projects(resume_text, text_lower)
    sections["projects"] = {
        "score": proj_score,
        "status": _status(proj_score),
        "tips": proj_tips,
    }

    # ── Education Section ──
    edu_score, edu_tips = _evaluate_education(resume_text, text_lower)
    sections["education"] = {
        "score": edu_score,
        "status": _status(edu_score),
        "tips": edu_tips,
    }

    # ── Formatting ──
    fmt_score, fmt_tips = _evaluate_formatting(resume_text)
    sections["formatting"] = {
        "score": fmt_score,
        "status": _status(fmt_score),
        "tips": fmt_tips,
    }

    # ── Overall ──
    scores = [s["score"] for s in sections.values()]
    overall = int(sum(scores) / len(scores))

    # Critical issues
    critical = []
    for name, data in sections.items():
        if data["score"] < 40:
            critical.append(f"⚠️ {name.title()} section is critically weak ({data['score']}/100)")

    # Strengths
    strengths = []
    for name, data in sections.items():
        if data["score"] >= 70:
            strengths.append(f"✅ {name.title()} section is strong ({data['score']}/100)")

    return {
        "sections": sections,
        "overall_score": overall,
        "critical_issues": critical,
        "strengths": strengths,
    }


def _status(score: int) -> str:
    if score >= 75:
        return "strong"
    elif score >= 50:
        return "moderate"
    elif score >= 25:
        return "weak"
    return "critical"


def _evaluate_skills(full_text: str, text_lower: str) -> tuple:
    """Evaluate skills section quality."""
    score = 30  # baseline
    tips = []

    # Check if skills section exists
    has_section = any(kw in text_lower for kw in ['skills', 'technical skills', 'technologies', 'tools'])
    if has_section:
        score += 20
    else:
        tips.append("Add a dedicated 'Technical Skills' section to your resume")

    # Count technical keywords
    tech_keywords = [
        'python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
        'tensorflow', 'machine learning', 'api', 'git', 'linux', 'node'
    ]
    found = sum(1 for kw in tech_keywords if kw in text_lower)

    if found >= 8:
        score += 30
    elif found >= 5:
        score += 20
    elif found >= 2:
        score += 10
        tips.append("Add more technical skills relevant to your target role (aim for 8-12)")
    else:
        tips.append("Your resume mentions very few technical skills — add at least 6-8 relevant technologies")

    # Check for skill categories
    categories = ['programming', 'framework', 'database', 'cloud', 'tool']
    cat_found = sum(1 for c in categories if c in text_lower)
    if cat_found >= 2:
        score += 10
    else:
        tips.append("Organize skills into categories: Languages, Frameworks, Databases, Tools")

    if not tips:
        tips.append("Skills section looks good. Consider adding proficiency levels.")

    return min(100, score), tips


def _evaluate_experience(full_text: str, text_lower: str) -> tuple:
    """Evaluate experience section quality."""
    score = 25
    tips = []

    has_section = any(kw in text_lower for kw in ['experience', 'work history', 'employment', 'professional experience', 'internship', 'intern'])
    if has_section:
        score += 15
    else:
        tips.append("Add a 'Professional Experience' or 'Work Experience' section")

    # Check for action verbs
    action_verbs = ['developed', 'implemented', 'led', 'built', 'created', 'managed',
                    'designed', 'optimized', 'improved', 'reduced', 'delivered', 'architected']
    found_verbs = sum(1 for v in action_verbs if v in text_lower)
    if found_verbs >= 5:
        score += 25
    elif found_verbs >= 2:
        score += 15
        tips.append("Use more action verbs: Developed, Implemented, Led, Optimized, Delivered")
    else:
        tips.append("Start each bullet point with a strong action verb")

    # Check for metrics/numbers
    metrics = re.findall(r'\d+%|\d+x|\$\d+|\d+ users|\d+ team', text_lower)
    if len(metrics) >= 3:
        score += 20
    elif len(metrics) >= 1:
        score += 10
        tips.append("Add more quantifiable achievements (e.g., 'Improved by 30%', 'Served 10K users')")
    else:
        tips.append("Add quantifiable metrics to your experience bullets — numbers make impact tangible")

    # Check for dates
    date_pattern = re.findall(r'\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec', text_lower)
    if len(date_pattern) >= 2:
        score += 10
    else:
        tips.append("Include dates for each role (e.g., 'Jan 2023 – Present')")

    if not tips:
        tips.append("Experience section is well-structured with strong impact statements")

    return min(100, score), tips


def _evaluate_projects(full_text: str, text_lower: str) -> tuple:
    """Evaluate projects section quality."""
    score = 20
    tips = []

    has_section = any(kw in text_lower for kw in ['project', 'portfolio', 'personal project', 'side project'])
    if has_section:
        score += 20
    else:
        tips.append("Add a 'Projects' section to showcase hands-on experience")
        return min(100, score), tips

    # Check for tech stack mentions in projects
    tech_mentions = re.findall(r'(using|built with|technologies?|stack|tools?)\s*:?\s*[a-zA-Z, ]+', text_lower)
    if tech_mentions:
        score += 15
    else:
        tips.append("Mention the tech stack for each project (e.g., 'Built with React, FastAPI, PostgreSQL')")

    # Check for project descriptions
    bullet_count = text_lower.count('•') + text_lower.count('-') + text_lower.count('*')
    if bullet_count >= 6:
        score += 20
    elif bullet_count >= 3:
        score += 10
        tips.append("Add more bullet points describing project features and your role")
    else:
        tips.append("Write 2-3 bullet points per project describing what you built and the impact")

    # Check for github/links
    if any(kw in text_lower for kw in ['github', 'link', 'demo', 'live', 'deploy']):
        score += 15
    else:
        tips.append("Add GitHub links or live demo URLs to your projects")

    if not tips:
        tips.append("Projects section is strong — great job showcasing your work!")

    return min(100, score), tips


def _evaluate_education(full_text: str, text_lower: str) -> tuple:
    """Evaluate education section."""
    score = 30
    tips = []

    has_section = any(kw in text_lower for kw in ['education', 'degree', 'university', 'college', 'bachelor', 'master'])
    if has_section:
        score += 25
    else:
        tips.append("Add an 'Education' section with your degree and university")
        return min(100, score), tips

    # GPA mention
    if re.search(r'gpa|cgpa|grade', text_lower):
        score += 10

    # Relevant coursework
    if any(kw in text_lower for kw in ['coursework', 'courses', 'relevant courses']):
        score += 10
    else:
        tips.append("Include relevant coursework to show domain knowledge")

    # Certifications
    if any(kw in text_lower for kw in ['certif', 'certified', 'certification', 'aws certified', 'google certified']):
        score += 15
    else:
        tips.append("Add relevant certifications (AWS, Google, Coursera, etc.)")

    if not tips:
        tips.append("Education section is complete and well-structured")

    return min(100, score), tips


def _evaluate_formatting(full_text: str) -> tuple:
    """Evaluate resume formatting quality."""
    score = 40
    tips = []

    # Check reasonable length
    word_count = len(full_text.split())
    if 200 <= word_count <= 800:
        score += 20
    elif word_count < 150:
        tips.append("Resume is too short — aim for 300-600 words for a single-page resume")
    elif word_count > 1200:
        tips.append("Resume may be too long — try to keep it to 1-2 pages")
    else:
        score += 10

    # Check for summary/objective
    if any(kw in full_text.lower() for kw in ['summary', 'objective', 'profile', 'about me']):
        score += 15
    else:
        tips.append("Add a brief professional summary at the top (2-3 sentences)")

    # Check for contact info
    has_email = bool(re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', full_text))
    has_phone = bool(re.search(r'[\+]?[\d\s\-\(\)]{10,}', full_text))
    if has_email:
        score += 5
    if has_phone:
        score += 5
    if not has_email:
        tips.append("Include your email address")
    if any(kw in full_text.lower() for kw in ['linkedin', 'github.com']):
        score += 10

    if not tips:
        tips.append("Formatting looks professional and well-organized")

    return min(100, score), tips
