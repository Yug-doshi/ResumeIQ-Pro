"""
Resume Summary Generator — AI-powered professional summary creation

Takes extracted resume text and generates:
  1. A professional summary paragraph
  2. Key strengths extracted from experience
  3. Elevator pitch for interviews
  4. LinkedIn headline suggestion

Works entirely offline using NLP (no API keys needed).
"""

import re
from typing import Dict, List
from collections import Counter


# ── Role-specific summary templates ──
SUMMARY_TEMPLATES = {
    "software engineer": [
        "Results-driven Software Engineer with {years} of experience building {specialization}. Proficient in {top_skills}, with a proven track record of delivering {achievement}. Passionate about {passion} and committed to writing clean, efficient code.",
        "Innovative Software Engineer specializing in {specialization}. Expert in {top_skills} with hands-on experience {achievement}. Strong advocate for {passion} and agile development practices.",
    ],
    "data scientist": [
        "Analytical Data Scientist with {years} of experience transforming complex data into actionable insights. Skilled in {top_skills}, with expertise in {specialization}. Demonstrated ability to {achievement}.",
        "Data-driven scientist with deep expertise in {top_skills}. Experienced in {specialization} with a focus on {achievement}. Passionate about {passion} and evidence-based decision making.",
    ],
    "ai engineer": [
        "AI Engineer with {years} of experience building intelligent systems using {top_skills}. Specialized in {specialization} with a track record of {achievement}. Committed to {passion}.",
        "Machine Learning specialist with deep expertise in {top_skills}. Experienced in {specialization}, delivering {achievement}. Passionate about {passion}.",
    ],
    "web developer": [
        "Creative Web Developer with {years} building responsive, user-centric applications using {top_skills}. Experienced in {specialization} with a focus on {achievement}. Dedicated to {passion}.",
        "Full-stack Web Developer proficient in {top_skills}. Specialized in {specialization}, consistently delivering {achievement}. Strong commitment to {passion}.",
    ],
    "devops engineer": [
        "DevOps Engineer with {years} of experience automating infrastructure and CI/CD pipelines using {top_skills}. Expert in {specialization} with achievements including {achievement}. Passionate about {passion}.",
    ],
    "default": [
        "Experienced professional with {years} in {specialization}. Skilled in {top_skills} with a proven ability to {achievement}. Dedicated to {passion}.",
    ],
}

SPECIALIZATIONS = {
    "software engineer": ["scalable backend systems", "full-stack applications", "distributed architectures", "cloud-native applications"],
    "data scientist": ["predictive modeling", "deep learning and NLP", "statistical analysis and visualization", "recommendation systems"],
    "ai engineer": ["NLP and transformer models", "computer vision systems", "deep learning architectures", "MLOps and model deployment"],
    "web developer": ["modern SPA frameworks", "responsive design and accessibility", "e-commerce platforms", "progressive web applications"],
    "devops engineer": ["container orchestration and CI/CD", "cloud infrastructure automation", "monitoring and observability", "infrastructure as code"],
}

PASSIONS = {
    "software engineer": ["clean architecture and design patterns", "open-source contribution", "performance optimization", "continuous learning"],
    "data scientist": ["uncovering hidden patterns in data", "bridging the gap between data and business", "reproducible research"],
    "ai engineer": ["pushing the boundaries of AI", "responsible AI development", "deploying ML at scale"],
    "web developer": ["pixel-perfect designs and smooth UX", "web performance and accessibility", "modern frontend architecture"],
    "devops engineer": ["reliability engineering and zero-downtime deployments", "infrastructure automation", "site reliability"],
}

ACHIEVEMENTS = [
    "reducing system latency by 40%", "scaling applications to 100K+ users",
    "improving team productivity by 30%", "delivering projects ahead of schedule",
    "building systems processing millions of records daily", "driving 25% revenue growth through optimization",
    "mentoring junior developers", "reducing infrastructure costs by 35%",
]


def generate_resume_summary(resume_text: str, job_role: str = "Software Engineer") -> Dict:
    """
    Generate a comprehensive professional summary from resume text.

    Returns:
    {
      "professional_summary": str,
      "key_strengths": [str],
      "elevator_pitch": str,
      "linkedin_headline": str,
      "career_highlights": [str],
      "experience_years": str,
    }
    """
    role_key = job_role.lower().strip()

    # Extract information from resume
    skills = _extract_skills_from_text(resume_text)
    years = _estimate_experience(resume_text)
    highlights = _extract_highlights(resume_text)
    sections_present = _detect_sections(resume_text)

    # Top skills (limit to 4)
    top_skills = ", ".join(skills[:4]) if skills else "modern technologies"

    # Pick specialization
    specs = SPECIALIZATIONS.get(role_key, SPECIALIZATIONS.get("software engineer"))
    import random
    specialization = random.choice(specs) if specs else "software development"

    # Pick passion
    passions = PASSIONS.get(role_key, PASSIONS.get("software engineer"))
    passion = random.choice(passions) if passions else "continuous improvement"

    # Pick achievement
    if highlights:
        achievement = highlights[0]
    else:
        achievement = random.choice(ACHIEVEMENTS)

    # ── Generate Professional Summary ──
    templates = SUMMARY_TEMPLATES.get(role_key, SUMMARY_TEMPLATES["default"])
    template = random.choice(templates)
    professional_summary = template.format(
        years=years,
        top_skills=top_skills,
        specialization=specialization,
        achievement=achievement,
        passion=passion,
    )

    # ── Key Strengths ──
    key_strengths = _generate_key_strengths(skills, highlights, role_key)

    # ── Elevator Pitch ──
    elevator_pitch = _generate_elevator_pitch(role_key, top_skills, years, achievement)

    # ── LinkedIn Headline ──
    linkedin_headline = _generate_linkedin_headline(role_key, skills)

    # ── Career Highlights ──
    career_highlights = highlights[:5] if highlights else [
        f"Proficient in {', '.join(skills[:3])}" if skills else "Building software solutions",
        f"{years} of professional experience",
        f"Specialized in {specialization}",
    ]

    return {
        "professional_summary": professional_summary,
        "key_strengths": key_strengths,
        "elevator_pitch": elevator_pitch,
        "linkedin_headline": linkedin_headline,
        "career_highlights": career_highlights,
        "experience_years": years,
        "detected_skills": skills[:12],
    }


def _extract_skills_from_text(text: str) -> List[str]:
    """Extract technical skills mentioned in resume."""
    tech_skills = [
        "Python", "JavaScript", "Java", "C++", "TypeScript", "Go", "Rust", "Ruby", "PHP",
        "React", "Angular", "Vue.js", "Next.js", "Node.js", "Django", "Flask", "FastAPI",
        "Spring Boot", "Express.js", "TensorFlow", "PyTorch", "Keras", "scikit-learn",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "PostgreSQL", "MongoDB", "Redis",
        "SQL", "Git", "Linux", "CI/CD", "GraphQL", "REST API", "Microservices",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Pandas", "NumPy", "Tableau", "Power BI", "Apache Spark", "Kafka",
        "Terraform", "Jenkins", "Agile", "Scrum",
    ]

    text_lower = text.lower()
    found = []
    for skill in tech_skills:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


def _estimate_experience(text: str) -> str:
    """Estimate years of experience from resume text."""
    # Look for explicit mentions
    year_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'(\d{4})\s*[-–]\s*(?:present|current|\d{4})',
    ]

    for pattern in year_patterns:
        matches = re.findall(pattern, text.lower())
        if matches:
            try:
                val = int(matches[0])
                if val < 50:  # raw years
                    return f"{val}+ years"
                else:  # year (like 2020)
                    years = 2025 - val
                    return f"{max(1, years)}+ years"
            except ValueError:
                pass

    # Count job entries as a rough estimate
    job_keywords = len(re.findall(r'(company|inc\.|ltd\.|corp\.|llc|technologies)', text.lower()))
    if job_keywords >= 3:
        return "5+ years"
    elif job_keywords >= 1:
        return "2+ years"
    return "relevant experience"


def _extract_highlights(text: str) -> List[str]:
    """Extract quantifiable achievements from resume."""
    highlights = []

    # Find lines with metrics
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if re.search(r'\d+%|\$\d+|\d+[KkMm]\+?|\d+x', line) and len(line) > 20:
            # Clean up bullet points
            clean_line = re.sub(r'^[-•*▸→\s]+', '', line).strip()
            if clean_line:
                highlights.append(clean_line[:120])

    return highlights[:5]


def _detect_sections(text: str) -> List[str]:
    """Detect which resume sections are present."""
    sections = []
    text_lower = text.lower()
    section_names = ["summary", "experience", "education", "skills", "projects", "certifications", "awards"]
    for s in section_names:
        if s in text_lower:
            sections.append(s)
    return sections


def _generate_key_strengths(skills: list, highlights: list, role_key: str) -> List[str]:
    """Generate key strengths bullet points."""
    strengths = []

    if skills:
        strengths.append(f"Technical expertise in {', '.join(skills[:3])}")
    if len(skills) > 5:
        strengths.append(f"Versatile skill set spanning {len(skills)}+ technologies")
    if highlights:
        strengths.append("Quantifiable impact with measurable business outcomes")
    strengths.append("Strong problem-solving and analytical skills")
    strengths.append("Collaborative team player with excellent communication")

    return strengths[:5]


def _generate_elevator_pitch(role_key: str, top_skills: str, years: str, achievement: str) -> str:
    """Generate a 30-second elevator pitch."""
    role_title = role_key.replace("_", " ").title() if role_key != "default" else "Software Professional"
    return (
        f"I'm a {role_title} with {years} of hands-on experience. "
        f"I specialize in {top_skills}, and I've been able to {achievement}. "
        f"I'm looking for opportunities where I can drive technical innovation "
        f"while contributing to impactful products."
    )


def _generate_linkedin_headline(role_key: str, skills: list) -> str:
    """Generate a LinkedIn-optimized headline."""
    role_title = role_key.replace("_", " ").title() if role_key != "default" else "Software Engineer"
    skill_str = " | ".join(skills[:3]) if skills else "Technology"
    return f"{role_title} | {skill_str} | Building Impactful Solutions"
