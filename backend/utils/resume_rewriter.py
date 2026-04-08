"""
Resume Rewriter — Transform weak bullet points into impactful statements

Features:
  - Action verb injection
  - Metrics addition
  - Role-specific language
  - Before/after comparison
"""

from typing import List
import random
import re


# ── Strong action verbs by role ──
ACTION_VERBS = {
    "software engineer": ["Developed", "Architected", "Engineered", "Optimized", "Implemented", "Refactored", "Deployed", "Automated"],
    "data scientist": ["Analyzed", "Modeled", "Engineered", "Discovered", "Predicted", "Optimized", "Visualized", "Quantified"],
    "ai engineer": ["Trained", "Deployed", "Optimized", "Implemented", "Fine-tuned", "Architected", "Benchmarked", "Integrated"],
    "web developer": ["Built", "Designed", "Implemented", "Optimized", "Migrated", "Integrated", "Launched", "Created"],
    "devops engineer": ["Automated", "Deployed", "Configured", "Monitored", "Scaled", "Containerized", "Orchestrated", "Provisioned"],
    "product manager": ["Led", "Launched", "Drove", "Managed", "Prioritized", "Scaled", "Delivered", "Analyzed"],
}

# ── Impact metrics templates ──
METRICS = [
    "resulting in {pct}% improvement in performance",
    "serving {num}+ daily active users",
    "reducing processing time by {pct}%",
    "decreasing costs by ${amt}K annually",
    "improving team productivity by {pct}%",
    "achieving {pct}% test coverage",
    "handling {num}+ concurrent requests",
]


def rewrite_bullet_points(text: str, job_role: str) -> List[str]:
    """
    Rewrite weak resume bullet points into strong impact statements.

    Args:
        text:     Resume text or bullet points
        job_role: Target job role for language matching

    Returns:
        List of rewritten bullet points
    """
    # Extract lines that look like bullet points
    lines = text.split("\n")
    bullets = []
    for line in lines:
        clean = line.strip().lstrip("-•*▪▸→ ")
        if len(clean) > 10:
            bullets.append(clean)

    if not bullets:
        return generate_sample_bullets(job_role)

    rewritten = []
    for bullet in bullets[:5]:
        enhanced = _enhance_bullet(bullet, job_role)
        rewritten.append(enhanced)

    return rewritten


def _enhance_bullet(bullet: str, job_role: str) -> str:
    """Enhance a single bullet point."""
    role_key = job_role.lower().strip()
    verbs = ACTION_VERBS.get(role_key, ACTION_VERBS["software engineer"])

    # Check if bullet already starts with a strong verb
    first_word = bullet.split()[0].lower() if bullet.split() else ""
    all_verbs_lower = [v.lower() for vlist in ACTION_VERBS.values() for v in vlist]

    if first_word not in all_verbs_lower:
        # Add a strong action verb
        verb = random.choice(verbs)
        # Lowercase the first letter of existing text
        bullet = bullet[0].lower() + bullet[1:] if bullet else bullet
        bullet = f"{verb} {bullet}"

    # Check if metrics are present
    has_numbers = bool(re.search(r'\d+%|\$\d+|\d+ user|\d+ team|\d+x', bullet))
    if not has_numbers:
        # Add a plausible metric
        metric = random.choice(METRICS)
        metric = metric.replace("{pct}", str(random.randint(20, 60)))
        metric = metric.replace("{num}", str(random.choice([100, 500, 1000, 5000, 10000])))
        metric = metric.replace("{amt}", str(random.choice([10, 25, 50, 100])))

        # Only add if bullet doesn't already end with period + meaningful text
        if not bullet.rstrip().endswith('.'):
            bullet = f"{bullet}, {metric}"
        else:
            bullet = f"{bullet.rstrip('.')} , {metric}"

    return bullet


def generate_sample_bullets(job_role: str) -> List[str]:
    """Generate sample strong bullet points for a given job role."""
    samples = {
        "software engineer": [
            "Developed high-performance REST APIs using FastAPI, reducing response time by 40% and serving 10K+ daily requests",
            "Architected microservices system improving scalability and reducing deployment time from 2 hours to 15 minutes",
            "Optimized database queries improving application speed by 35% and reducing infrastructure costs by $50K annually",
            "Led code reviews and mentored 3 junior developers, improving code quality scores by 30%",
            "Implemented CI/CD pipeline using Docker and GitHub Actions, enabling 50+ deployments per month with zero downtime",
        ],
        "data scientist": [
            "Built machine learning models achieving 94% accuracy, enabling 20% improvement in customer retention predictions",
            "Engineered data pipeline processing 5M+ daily records using Apache Spark, reducing query times by 60%",
            "Developed recommendation system increasing user engagement by 35% and generating $2M additional annual revenue",
            "Analyzed complex datasets uncovering key business insights that improved marketing ROI by 45%",
            "Optimized model training reducing computational time by 70% through parallel processing and feature engineering",
        ],
        "ai engineer": [
            "Implemented transformer-based NLP model achieving state-of-the-art results on sentiment analysis (96% F1 score)",
            "Deployed ML model to production serving 1M+ predictions daily with 50ms latency using TensorFlow Serving",
            "Optimized neural network architecture reducing model size by 80% while maintaining 98% accuracy via quantization",
            "Developed computer vision pipeline for automated quality control reducing manufacturing defects by 45%",
            "Built real-time recommendation engine using deep learning processing 100K events/second with sub-100ms latency",
        ],
        "web developer": [
            "Built responsive frontend using React and TypeScript, improving page load speed by 50% and mobile conversion by 30%",
            "Implemented real-time notification system using WebSocket serving 500K+ concurrent users with 99.9% uptime",
            "Optimized webpack configuration reducing bundle size by 60% and improving Lighthouse scores from 65 to 95",
            "Developed reusable component library reducing development time by 40% across 3 product teams",
            "Migrated legacy jQuery codebase to React with 100% test coverage, enabling 10x faster feature development",
        ],
        "devops engineer": [
            "Automated infrastructure provisioning using Terraform reducing setup time from 2 days to 30 minutes",
            "Designed and managed Kubernetes clusters serving 50+ microservices with 99.99% uptime SLA",
            "Implemented monitoring and alerting system using Prometheus/Grafana reducing incident response time by 60%",
            "Built CI/CD pipelines handling 200+ daily deployments across 5 environments with automated rollback",
            "Reduced cloud infrastructure costs by 40% ($150K/year) through resource optimization and auto-scaling",
        ],
    }

    role_key = next((k for k in samples if k in job_role.lower()), "software engineer")
    return random.sample(samples[role_key], min(3, len(samples[role_key])))


def get_improvement_tips(original: str, rewritten: List[str]) -> List[str]:
    """Generate resume writing tips."""
    return [
        "✓ Start every bullet with a strong action verb (Developed, Led, Optimized)",
        "✓ Include quantifiable metrics (percentages, dollar amounts, user counts)",
        "✓ Focus on impact and business value, not just tasks performed",
        "✓ Keep bullets concise: 1-2 lines maximum for easy scanning",
        "✓ Use past tense for previous roles, present tense for current role",
        "✓ Tailor bullets to match keywords in the job description",
    ]
