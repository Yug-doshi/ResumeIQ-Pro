"""
Model Trainer — PRODUCTION-GRADE LSTM Resume Scorer Training

Generates 1000+ realistic synthetic training samples covering:
  - 12 job roles (SWE, DS, AI, Web, DevOps, PM, etc.)
  - Realistic resume structures (summary, skills, experience, education, projects)
  - Diverse job descriptions with requirements, responsibilities, qualifications
  - Accurate match scoring based on actual skill overlap analysis
  - Edge cases: over-qualified, under-qualified, career-switchers

Usage:
  python train_model.py                         # default: 1000 samples, 15 epochs
  python train_model.py --samples 2000 --epochs 25
"""

import argparse
import random
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.lstm_scorer import LSTMResumeScorer


# =====================================================================
#  COMPREHENSIVE SKILL DATABASE BY CATEGORY
# =====================================================================

SKILLS_DB = {
    "programming_languages": [
        "Python", "JavaScript", "Java", "C++", "C#", "TypeScript", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Dart",
    ],
    "frontend_frameworks": [
        "React", "Angular", "Vue.js", "Next.js", "Svelte", "Gatsby", "Nuxt.js",
        "React Native", "Flutter", "Ionic", "Ember.js",
    ],
    "backend_frameworks": [
        "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
        "Laravel", "Ruby on Rails", "ASP.NET", "Gin", "Fiber", "NestJS",
    ],
    "databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "DynamoDB",
        "Cassandra", "SQLite", "Oracle", "MariaDB", "CouchDB", "Neo4j", "Firebase",
    ],
    "cloud_devops": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible",
        "Jenkins", "CI/CD", "GitHub Actions", "CircleCI", "Prometheus", "Grafana",
        "Nginx", "Apache", "CloudFormation", "Pulumi", "ArgoCD",
    ],
    "ml_ai": [
        "TensorFlow", "PyTorch", "Keras", "scikit-learn", "Pandas", "NumPy",
        "OpenCV", "NLTK", "spaCy", "Hugging Face", "MLflow", "Kubeflow",
        "Apache Spark", "Airflow", "XGBoost", "LightGBM", "ONNX", "TensorRT",
    ],
    "data_tools": [
        "Tableau", "Power BI", "Looker", "Apache Kafka", "Hadoop", "Snowflake",
        "BigQuery", "Redshift", "Databricks", "dbt", "Jupyter", "Matplotlib",
        "Seaborn", "Plotly", "D3.js",
    ],
    "soft_skills": [
        "team leadership", "project management", "communication", "problem-solving",
        "agile methodology", "scrum", "mentoring", "cross-functional collaboration",
        "stakeholder management", "critical thinking", "time management",
    ],
    "security": [
        "OWASP", "penetration testing", "OAuth2", "JWT", "encryption", "SSL/TLS",
        "IAM", "RBAC", "security auditing", "compliance", "SOC 2",
    ],
    "testing": [
        "pytest", "Jest", "Selenium", "Cypress", "JUnit", "Mocha", "Chai",
        "unit testing", "integration testing", "load testing", "TDD", "BDD",
    ],
}

# =====================================================================
#  ROLE CONFIGURATIONS — what each role typically requires
# =====================================================================

ROLE_CONFIGS = {
    "Software Engineer": {
        "primary": ["Python", "Java", "JavaScript", "C++"],
        "must_have": ["Git", "SQL", "REST API", "unit testing"],
        "frameworks": ["React", "Django", "Spring Boot", "Node.js", "FastAPI"],
        "infra": ["Docker", "AWS", "CI/CD", "Linux"],
        "nice_to_have": ["Kubernetes", "Redis", "GraphQL", "microservices"],
    },
    "Data Scientist": {
        "primary": ["Python", "R", "SQL"],
        "must_have": ["Pandas", "NumPy", "scikit-learn", "statistics"],
        "frameworks": ["TensorFlow", "PyTorch", "Keras", "XGBoost"],
        "infra": ["Jupyter", "AWS", "Docker"],
        "nice_to_have": ["Apache Spark", "Tableau", "Deep Learning", "NLP", "MLflow"],
    },
    "AI Engineer": {
        "primary": ["Python", "C++"],
        "must_have": ["TensorFlow", "PyTorch", "Deep Learning", "NLP"],
        "frameworks": ["Keras", "Hugging Face", "ONNX", "TensorRT"],
        "infra": ["Docker", "GPU computing", "AWS", "Kubernetes"],
        "nice_to_have": ["computer vision", "reinforcement learning", "MLOps", "Kubeflow"],
    },
    "Frontend Developer": {
        "primary": ["JavaScript", "TypeScript", "HTML", "CSS"],
        "must_have": ["React", "responsive design", "REST API", "Git"],
        "frameworks": ["Next.js", "Vue.js", "Angular", "TailwindCSS"],
        "infra": ["Webpack", "Vite", "Jest", "Cypress"],
        "nice_to_have": ["GraphQL", "Storybook", "Figma", "accessibility", "performance optimization"],
    },
    "Backend Developer": {
        "primary": ["Python", "Java", "Go", "Node.js"],
        "must_have": ["SQL", "REST API", "microservices", "Git"],
        "frameworks": ["FastAPI", "Django", "Spring Boot", "Express.js"],
        "infra": ["Docker", "PostgreSQL", "Redis", "AWS"],
        "nice_to_have": ["Kubernetes", "Kafka", "GraphQL", "message queues", "caching"],
    },
    "Full Stack Developer": {
        "primary": ["JavaScript", "TypeScript", "Python"],
        "must_have": ["React", "Node.js", "SQL", "Git", "REST API"],
        "frameworks": ["Next.js", "Express.js", "Django", "MongoDB"],
        "infra": ["Docker", "AWS", "CI/CD", "Nginx"],
        "nice_to_have": ["GraphQL", "Redis", "WebSocket", "serverless"],
    },
    "DevOps Engineer": {
        "primary": ["Python", "Bash", "Go"],
        "must_have": ["Docker", "Kubernetes", "CI/CD", "Linux", "AWS"],
        "frameworks": ["Terraform", "Ansible", "Jenkins", "GitHub Actions"],
        "infra": ["Prometheus", "Grafana", "ELK Stack", "Nginx"],
        "nice_to_have": ["ArgoCD", "Helm", "service mesh", "chaos engineering"],
    },
    "ML Engineer": {
        "primary": ["Python", "C++", "Java"],
        "must_have": ["TensorFlow", "PyTorch", "scikit-learn", "Docker"],
        "frameworks": ["MLflow", "Kubeflow", "Airflow", "FastAPI"],
        "infra": ["AWS", "GPU computing", "Kubernetes", "CI/CD"],
        "nice_to_have": ["ONNX", "TensorRT", "model optimization", "A/B testing"],
    },
    "Cloud Architect": {
        "primary": ["Python", "Go", "Java"],
        "must_have": ["AWS", "Azure", "Terraform", "networking", "security"],
        "frameworks": ["CloudFormation", "Pulumi", "Docker", "Kubernetes"],
        "infra": ["VPC", "IAM", "load balancing", "auto-scaling"],
        "nice_to_have": ["multi-cloud", "cost optimization", "compliance", "disaster recovery"],
    },
    "Product Manager": {
        "primary": ["SQL", "data analysis"],
        "must_have": ["agile methodology", "product roadmap", "stakeholder management"],
        "frameworks": ["Jira", "Confluence", "analytics tools"],
        "infra": ["A/B testing", "user research"],
        "nice_to_have": ["Python", "Tableau", "product metrics", "competitive analysis"],
    },
    "Mobile Developer": {
        "primary": ["Swift", "Kotlin", "Dart", "JavaScript"],
        "must_have": ["iOS", "Android", "REST API", "Git"],
        "frameworks": ["React Native", "Flutter", "SwiftUI", "Jetpack Compose"],
        "infra": ["Firebase", "App Store", "CI/CD"],
        "nice_to_have": ["GraphQL", "push notifications", "offline storage", "app performance"],
    },
    "Cybersecurity Engineer": {
        "primary": ["Python", "C", "Bash"],
        "must_have": ["OWASP", "penetration testing", "network security", "Linux"],
        "frameworks": ["Burp Suite", "Wireshark", "Metasploit", "Nmap"],
        "infra": ["SIEM", "firewall", "IDS/IPS", "encryption"],
        "nice_to_have": ["cloud security", "SOC 2", "malware analysis", "incident response"],
    },
}

# =====================================================================
#  RESUME SECTION TEMPLATES
# =====================================================================

SUMMARY_TEMPLATES = [
    "Highly motivated {role} with {years}+ years of experience in {domain}. Proven track record in building {project_type} using {tech_list}. Passionate about {passion}.",
    "Results-driven {role} specializing in {domain}. Expert in {tech_list} with experience delivering {project_type} at scale. Strong background in {passion}.",
    "Experienced {role} with deep expertise in {tech_list}. Led teams of {team_size} developers, shipping production-quality {project_type}. Committed to {passion}.",
    "Detail-oriented {role} with {years}+ years building {project_type}. Proficient in {tech_list}. Experience with {domain} and {passion}.",
    "Innovative {role} focused on {domain}. Skilled in {tech_list}. Delivered {project_type} serving millions of users. Enthusiastic about {passion}.",
]

EXPERIENCE_TEMPLATES = [
    "Developed {project_type} using {tech1} and {tech2}, resulting in {pct}% improvement in {metric}",
    "Led a team of {team_size} engineers to deliver {project_type} on time, increasing {metric} by {pct}%",
    "Architected and deployed {project_type} handling {users}+ daily active users with 99.{uptime}% uptime",
    "Implemented {tech1}-based solution reducing {metric} by {pct}%, saving ${cost}K annually",
    "Built RESTful APIs using {tech1} serving {users}+ requests per second with sub-{latency}ms latency",
    "Optimized {tech2} database queries improving response time by {pct}% across {endpoints} endpoints",
    "Migrated legacy {tech2} system to {tech1}, improving developer productivity by {pct}%",
    "Designed and implemented CI/CD pipeline using {tech1} enabling {deploys}+ daily deployments",
    "Mentored {team_size} junior developers, improving code quality scores by {pct}%",
    "Integrated {tech1} with {tech2} to create automated {project_type} reducing manual effort by {pct}%",
    "Conducted {pct}+ code reviews per month, maintaining high code quality standards",
    "Wrote comprehensive unit and integration tests achieving {pct}% code coverage using {tech1}",
    "Deployed {project_type} on {tech2} cloud infrastructure serving {users}+ concurrent users",
    "Reduced infrastructure costs by {pct}% through {tech1} optimization and resource management",
    "Collaborated with cross-functional teams to deliver {project_type} 2 weeks ahead of schedule",
]

PROJECT_TYPES = [
    "microservices architecture", "real-time analytics dashboard", "recommendation engine",
    "e-commerce platform", "content management system", "data pipeline",
    "machine learning model", "mobile application", "payment processing system",
    "user authentication system", "notification service", "search engine",
    "chat application", "monitoring dashboard", "inventory management system",
    "CI/CD pipeline", "API gateway", "distributed caching system",
]

PASSIONS = [
    "clean code and best practices", "scalable architecture", "continuous learning",
    "open source contribution", "performance optimization", "user experience",
    "data-driven decision making", "agile development", "innovation and automation",
    "mentoring and knowledge sharing", "building impactful products",
]

METRICS = [
    "response time", "system performance", "user engagement", "conversion rate",
    "deployment frequency", "page load speed", "throughput", "error rate",
    "customer satisfaction", "processing time", "infrastructure costs",
]

DOMAINS = [
    "web development", "cloud computing", "machine learning", "data engineering",
    "mobile development", "distributed systems", "DevOps", "cybersecurity",
    "e-commerce", "fintech", "healthcare tech", "EdTech", "SaaS platforms",
]

EDUCATION = [
    "Bachelor of Science in Computer Science from {university}",
    "Master of Science in Computer Science from {university}",
    "B.Tech in Information Technology from {university}",
    "Bachelor of Engineering in Computer Science from {university}",
    "M.Tech in Artificial Intelligence from {university}",
    "Bachelor of Science in Software Engineering from {university}",
    "Master in Data Science from {university}",
]

UNIVERSITIES = [
    "MIT", "Stanford University", "IIT Delhi", "Carnegie Mellon", "UC Berkeley",
    "Georgia Tech", "University of Michigan", "IIT Bombay", "NIT Trichy",
    "University of Texas", "BITS Pilani", "ETH Zurich", "Caltech",
    "National University of Singapore", "University of Toronto",
]


# =====================================================================
#  JOB DESCRIPTION TEMPLATES
# =====================================================================

JD_TEMPLATES = [
    """We are looking for a {role} to join our {team} team at {company}.

Requirements:
- {years}+ years of experience in {domain}
- Strong proficiency in {tech_list_required}
- Experience with {tech_list_preferred}
- Excellent problem-solving and communication skills
- {degree} in Computer Science or related field

Responsibilities:
- Design and develop {project_type}
- Collaborate with cross-functional teams
- Write clean, maintainable, and well-tested code
- Participate in code reviews and technical discussions
- Mentor junior team members

Nice to have:
- Experience with {tech_nice}
- {certification} certification
- Open source contributions""",

    """{company} is hiring a {role}!

About the role:
You will be building {project_type} that serve millions of users.

Required skills:
- {tech_list_required}
- {years}+ years professional experience
- Strong foundation in {domain}
- Experience with agile development practices

Preferred qualifications:
- {tech_list_preferred}
- {certification} experience
- Published technical blog posts or conference talks
- {degree} or equivalent practical experience""",

    """Join {company} as a {role}

We need someone who can:
- Build and maintain {project_type}
- Work with {tech_list_required}
- Lead technical design discussions
- Ensure code quality through testing and reviews

Must have:
- {years}+ years with {tech_list_required}
- Track record of delivering complex projects
- {degree} in relevant field

Bonus points for:
- {tech_list_preferred}
- {certification}
- Experience at scale ({users}+ users)""",
]

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix",
    "Uber", "Airbnb", "Stripe", "Shopify", "Salesforce", "Adobe",
    "Atlassian", "Spotify", "LinkedIn", "Twitter", "Coinbase",
    "a fast-growing startup", "a leading fintech company", "a top SaaS platform",
]

CERTIFICATIONS = [
    "AWS Solutions Architect", "Google Cloud Professional", "Azure Administrator",
    "Kubernetes (CKA)", "Terraform Associate", "Scrum Master", "PMP",
    "TensorFlow Developer", "MongoDB Developer", "Oracle Java",
]

TEAMS = [
    "Engineering", "Platform", "Infrastructure", "Data", "Product",
    "Security", "Mobile", "Growth", "Core Services", "AI/ML",
]


# =====================================================================
#  INTELLIGENT DATA GENERATOR
# =====================================================================

def _pick_skills(role_config, count, overlap_ratio=1.0):
    """Pick skills from role config with controlled randomness."""
    all_role_skills = (
        role_config["primary"] +
        role_config["must_have"] +
        role_config["frameworks"] +
        role_config["infra"] +
        role_config["nice_to_have"]
    )

    # How many from role vs random
    from_role = int(count * overlap_ratio)
    from_random = count - from_role

    selected = random.sample(all_role_skills, min(from_role, len(all_role_skills)))

    # Add random skills from other categories
    all_skills = []
    for cat_skills in SKILLS_DB.values():
        all_skills.extend(cat_skills)
    remaining = [s for s in all_skills if s not in selected]
    selected += random.sample(remaining, min(from_random, len(remaining)))

    return selected[:count]


def generate_realistic_resume(role, skills, experience_level="mid"):
    """Generate a highly realistic resume text."""
    years = {"junior": random.randint(0, 2), "mid": random.randint(3, 5), "senior": random.randint(6, 12)}
    yr = years.get(experience_level, 3)
    team_size = random.randint(2, 8)

    # Summary
    summary = random.choice(SUMMARY_TEMPLATES).format(
        role=role, years=yr, domain=random.choice(DOMAINS),
        project_type=random.choice(PROJECT_TYPES),
        tech_list=", ".join(skills[:4]),
        passion=random.choice(PASSIONS), team_size=team_size
    )

    # Skills section
    skill_section = "TECHNICAL SKILLS\n"
    skill_section += f"Languages: {', '.join(skills[:4])}\n"
    skill_section += f"Frameworks: {', '.join(skills[4:7])}\n"
    skill_section += f"Tools & Infrastructure: {', '.join(skills[7:10])}\n"
    if len(skills) > 10:
        skill_section += f"Other: {', '.join(skills[10:])}\n"

    # Experience
    exp_section = "PROFESSIONAL EXPERIENCE\n"
    num_exp = random.randint(3, 7)
    for _ in range(num_exp):
        template = random.choice(EXPERIENCE_TEMPLATES)
        tech_pool = skills if skills else ["Python"]
        line = template.format(
            project_type=random.choice(PROJECT_TYPES),
            tech1=random.choice(tech_pool),
            tech2=random.choice(tech_pool),
            pct=random.randint(15, 70),
            metric=random.choice(METRICS),
            users=random.choice(["1K", "5K", "10K", "50K", "100K", "500K", "1M"]),
            team_size=team_size,
            uptime=random.randint(9, 99),
            cost=random.choice([10, 25, 50, 100, 250]),
            latency=random.choice([50, 100, 200, 500]),
            endpoints=random.randint(10, 50),
            deploys=random.randint(5, 50),
        )
        exp_section += f"- {line}\n"

    # Education
    edu = random.choice(EDUCATION).format(university=random.choice(UNIVERSITIES))
    edu_section = f"EDUCATION\n{edu}\nGPA: {random.uniform(3.0, 4.0):.1f}/4.0\n"

    # Projects
    proj_section = "PROJECTS\n"
    for _ in range(random.randint(1, 3)):
        proj_section += f"- {random.choice(PROJECT_TYPES).title()}: Built using {', '.join(random.sample(skills, min(3, len(skills))))}\n"

    # Certifications (sometimes)
    cert_section = ""
    if random.random() > 0.5:
        cert_section = f"CERTIFICATIONS\n- {random.choice(CERTIFICATIONS)}\n"

    resume = f"PROFESSIONAL SUMMARY\n{summary}\n\n{skill_section}\n{exp_section}\n{edu_section}\n{proj_section}\n{cert_section}"
    return resume


def generate_realistic_jd(role, required_skills, preferred_skills):
    """Generate a realistic job description."""
    template = random.choice(JD_TEMPLATES)

    return template.format(
        role=role,
        company=random.choice(COMPANIES),
        team=random.choice(TEAMS),
        years=random.randint(2, 7),
        domain=random.choice(DOMAINS),
        tech_list_required=", ".join(required_skills[:5]),
        tech_list_preferred=", ".join(preferred_skills[:3]),
        tech_nice=", ".join(preferred_skills[3:5]) if len(preferred_skills) > 3 else "cloud services",
        project_type=random.choice(PROJECT_TYPES),
        degree="B.S./M.S.",
        certification=random.choice(CERTIFICATIONS),
        users=random.choice(["50K", "100K", "1M", "10M"]),
    )


def calculate_actual_overlap(resume_skills, jd_skills):
    """Calculate true skill overlap between resume and JD."""
    resume_lower = set(s.lower() for s in resume_skills)
    jd_lower = set(s.lower() for s in jd_skills)

    if not jd_lower:
        return 0.5

    overlap = resume_lower & jd_lower
    overlap_ratio = len(overlap) / len(jd_lower)
    return overlap_ratio


def generate_training_data(num_samples=1000):
    """
    Generate diverse, realistic training data.

    Creates 5 categories of resume-JD pairs:
      1. Strong matches (same role, high skill overlap) → score 0.7-0.95
      2. Good matches (similar role, moderate overlap) → score 0.5-0.75
      3. Partial matches (some overlap) → score 0.3-0.55
      4. Weak matches (different field) → score 0.1-0.35
      5. No matches (completely different) → score 0.0-0.15
    """
    resumes = []
    jds = []
    match_scores = []
    selection_labels = []

    roles = list(ROLE_CONFIGS.keys())
    samples_per_category = num_samples // 5

    print(f"   Generating {samples_per_category} strong matches...")
    # ── Category 1: Strong matches (same role, 70-95% overlap) ──
    for _ in range(samples_per_category):
        role = random.choice(roles)
        config = ROLE_CONFIGS[role]
        resume_skills = _pick_skills(config, random.randint(8, 14), overlap_ratio=0.85)
        jd_required = _pick_skills(config, random.randint(6, 10), overlap_ratio=0.9)
        jd_preferred = _pick_skills(config, random.randint(3, 5), overlap_ratio=0.6)

        resume = generate_realistic_resume(role, resume_skills, random.choice(["mid", "senior"]))
        jd = generate_realistic_jd(role, jd_required, jd_preferred)

        overlap = calculate_actual_overlap(resume_skills, jd_required + jd_preferred)
        score = min(0.95, 0.65 + overlap * 0.3 + random.uniform(-0.05, 0.05))
        selected = 1 if score > 0.6 else 0

        resumes.append(resume)
        jds.append(jd)
        match_scores.append(round(score, 3))
        selection_labels.append(selected)

    print(f"   Generating {samples_per_category} good matches...")
    # ── Category 2: Good matches (similar role, 50-75% overlap) ──
    for _ in range(samples_per_category):
        role = random.choice(roles)
        config = ROLE_CONFIGS[role]
        resume_skills = _pick_skills(config, random.randint(6, 12), overlap_ratio=0.65)

        # Use a slightly different role's JD
        jd_role = random.choice(roles)
        jd_config = ROLE_CONFIGS[jd_role]
        jd_required = _pick_skills(jd_config, random.randint(5, 8), overlap_ratio=0.8)
        jd_preferred = _pick_skills(jd_config, random.randint(2, 4), overlap_ratio=0.5)

        resume = generate_realistic_resume(role, resume_skills, "mid")
        jd = generate_realistic_jd(jd_role, jd_required, jd_preferred)

        overlap = calculate_actual_overlap(resume_skills, jd_required + jd_preferred)
        score = min(0.75, 0.45 + overlap * 0.3 + random.uniform(-0.05, 0.1))
        selected = 1 if score > 0.55 else 0

        resumes.append(resume)
        jds.append(jd)
        match_scores.append(round(score, 3))
        selection_labels.append(selected)

    print(f"   Generating {samples_per_category} partial matches...")
    # ── Category 3: Partial matches (30-55%) ──
    for _ in range(samples_per_category):
        role = random.choice(roles)
        config = ROLE_CONFIGS[role]
        resume_skills = _pick_skills(config, random.randint(5, 10), overlap_ratio=0.4)

        jd_role = random.choice([r for r in roles if r != role])
        jd_config = ROLE_CONFIGS[jd_role]
        jd_required = _pick_skills(jd_config, random.randint(5, 8), overlap_ratio=0.85)
        jd_preferred = _pick_skills(jd_config, random.randint(2, 4), overlap_ratio=0.7)

        resume = generate_realistic_resume(role, resume_skills, "junior")
        jd = generate_realistic_jd(jd_role, jd_required, jd_preferred)

        overlap = calculate_actual_overlap(resume_skills, jd_required + jd_preferred)
        score = min(0.55, 0.25 + overlap * 0.3 + random.uniform(-0.05, 0.1))
        selected = 1 if score > 0.5 and random.random() > 0.6 else 0

        resumes.append(resume)
        jds.append(jd)
        match_scores.append(round(score, 3))
        selection_labels.append(selected)

    print(f"   Generating {samples_per_category} weak matches...")
    # ── Category 4: Weak matches (10-35%) ──
    for _ in range(samples_per_category):
        role = random.choice(roles)
        config = ROLE_CONFIGS[role]
        resume_skills = _pick_skills(config, random.randint(4, 8), overlap_ratio=0.2)

        # Completely different role's JD
        different_roles = [r for r in roles if r != role]
        jd_role = random.choice(different_roles)
        jd_config = ROLE_CONFIGS[jd_role]
        jd_required = _pick_skills(jd_config, random.randint(6, 10), overlap_ratio=0.95)
        jd_preferred = _pick_skills(jd_config, random.randint(3, 5), overlap_ratio=0.8)

        resume = generate_realistic_resume(role, resume_skills, "junior")
        jd = generate_realistic_jd(jd_role, jd_required, jd_preferred)

        overlap = calculate_actual_overlap(resume_skills, jd_required + jd_preferred)
        score = min(0.35, 0.05 + overlap * 0.3 + random.uniform(0, 0.1))
        selected = 0

        resumes.append(resume)
        jds.append(jd)
        match_scores.append(round(score, 3))
        selection_labels.append(selected)

    print(f"   Generating {samples_per_category} no matches...")
    # ── Category 5: No match (0-15%) ──
    for _ in range(samples_per_category):
        # Marketing person applying for SWE, etc.
        non_tech_skills = random.sample(["social media", "content writing", "Canva", "WordPress",
            "marketing analytics", "SEO", "copywriting", "event planning", "public relations",
            "graphic design", "Adobe Photoshop", "video editing"], random.randint(3, 6))

        resume = f"""PROFESSIONAL SUMMARY
{random.choice(['Marketing', 'Sales', 'HR', 'Finance', 'Teaching'])} professional with {random.randint(1,5)} years experience.

SKILLS
{', '.join(non_tech_skills)}

EXPERIENCE
- Managed {random.choice(['social media accounts', 'marketing campaigns', 'client relationships', 'team scheduling'])}
- Created {random.choice(['presentations', 'reports', 'marketing materials', 'training documents'])}

EDUCATION
Bachelor of Arts from {random.choice(UNIVERSITIES)}"""

        jd_role = random.choice(["Software Engineer", "Data Scientist", "AI Engineer", "DevOps Engineer"])
        jd_config = ROLE_CONFIGS[jd_role]
        jd_required = _pick_skills(jd_config, random.randint(6, 10), overlap_ratio=0.95)
        jd_preferred = _pick_skills(jd_config, random.randint(3, 5), overlap_ratio=0.8)
        jd = generate_realistic_jd(jd_role, jd_required, jd_preferred)

        score = random.uniform(0.0, 0.15)
        selected = 0

        resumes.append(resume)
        jds.append(jd)
        match_scores.append(round(score, 3))
        selection_labels.append(selected)

    # ── Shuffle everything ──
    combined = list(zip(resumes, jds, match_scores, selection_labels))
    random.shuffle(combined)
    resumes, jds, match_scores, selection_labels = zip(*combined)

    return list(resumes), list(jds), list(match_scores), list(selection_labels)


# =====================================================================
#  MAIN TRAINING
# =====================================================================

def train(num_samples=1000, epochs=15):
    """Train the LSTM model with production-grade data."""
    print("=" * 65)
    print("  🧠 LSTM Resume Scorer — Production Training Pipeline")
    print("=" * 65)

    start_time = time.time()

    print(f"\n📊 Generating {num_samples} realistic training samples...")
    print(f"   Covering {len(ROLE_CONFIGS)} job roles with diverse skill patterns\n")
    resumes, jds, scores, labels = generate_training_data(num_samples)

    print(f"\n   ✅ {len(resumes)} resume-JD pairs created")
    print(f"   📈 Score distribution:")
    print(f"      Min: {min(scores):.3f}  Max: {max(scores):.3f}  Avg: {sum(scores)/len(scores):.3f}")
    print(f"   🎯 Selection rate: {sum(labels)}/{len(labels)} ({sum(labels)/len(labels)*100:.1f}%)")

    print(f"\n🧠 Building dual-input Bi-LSTM model...")
    scorer = LSTMResumeScorer()

    print(f"\n🚀 Training for {epochs} epochs with {num_samples} samples...")
    print(f"   Architecture: Resume Bi-LSTM(64) + JD Bi-LSTM(64) → Dense(128) → Dense(64) → 2 outputs")
    print(f"   Embedding: 100-dim, Vocab: 8000, Max sequence: 300 tokens\n")

    scorer.train(resumes, jds, scores, labels, epochs=epochs)

    elapsed = time.time() - start_time

    print(f"\n{'='*65}")
    print(f"  ✅ TRAINING COMPLETE — {elapsed:.1f} seconds")
    print(f"{'='*65}")

    # ── Run test predictions ──
    print(f"\n🧪 Running test predictions on 5 scenarios...\n")

    test_cases = [
        {
            "name": "Strong match (Python SWE → Python SWE role)",
            "resume": "Experienced Software Engineer with 5 years Python, Django, REST APIs, PostgreSQL, Docker, AWS, CI/CD. Built microservices serving 100K users.",
            "jd": "Software Engineer needed. Python, Django, REST APIs, Docker, AWS required. 3+ years experience.",
            "expected": "High (70-95)"
        },
        {
            "name": "Moderate match (Frontend dev → Full Stack role)",
            "resume": "Frontend developer skilled in React, TypeScript, CSS, HTML. 3 years experience building responsive web apps.",
            "jd": "Full Stack Developer. Need: React, Node.js, PostgreSQL, Docker. Experience with backend APIs required.",
            "expected": "Medium (40-65)"
        },
        {
            "name": "Weak match (Junior → Senior AI role)",
            "resume": "Recent graduate with basic Python knowledge. Completed online course in HTML and CSS.",
            "jd": "Senior AI Engineer. 5+ years. PyTorch, TensorFlow, Deep Learning, MLOps, Kubernetes, GPU computing required.",
            "expected": "Low (10-30)"
        },
        {
            "name": "No match (Marketing → DevOps)",
            "resume": "Marketing specialist with social media management. Expert in Canva and content writing.",
            "jd": "DevOps Engineer. Docker, Kubernetes, Terraform, AWS, CI/CD, Linux required. 4+ years.",
            "expected": "Very Low (0-15)"
        },
        {
            "name": "Perfect match (Data Scientist → DS role)",
            "resume": "Data Scientist with PhD. Expert in Python, TensorFlow, PyTorch, scikit-learn, Pandas, SQL, Spark. Published 5 ML papers. Built recommendation engine at scale.",
            "jd": "Data Scientist. Python, TensorFlow, scikit-learn, SQL, statistics, deep learning. PhD preferred.",
            "expected": "Very High (80-95)"
        },
    ]

    for i, tc in enumerate(test_cases):
        result = scorer.score_resume(tc["resume"], tc["jd"])
        icon = "✅" if result["method"] == "lstm" else "⚡"
        print(f"   {i+1}. {tc['name']}")
        print(f"      {icon} Score: {result['match_score']}  |  Selection: {result['selection_probability']:.2f}  |  Expected: {tc['expected']}")
        print(f"      Method: {result['method']}\n")

    print(f"🏁 Model saved to backend/models/")
    print(f"   The API will now use LSTM scoring automatically!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train LSTM Resume Scorer — Production Grade")
    parser.add_argument("--samples", type=int, default=1000, help="Training samples (recommended: 1000+)")
    parser.add_argument("--epochs", type=int, default=15, help="Training epochs (recommended: 15-25)")

    args = parser.parse_args()
    train(num_samples=args.samples, epochs=args.epochs)
