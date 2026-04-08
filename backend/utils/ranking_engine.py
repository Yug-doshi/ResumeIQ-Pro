"""
Ranking Engine — Simulates 100 candidates and ranks the user

Generates realistic score distributions for a given job role and
calculates the user's percentile among simulated candidates.
"""

import random
import numpy as np
from typing import Dict


# ── Score distribution parameters by role (mean, std_dev) ──
ROLE_DISTRIBUTIONS = {
    "software engineer":  {"mean": 58, "std": 15},
    "data scientist":     {"mean": 55, "std": 18},
    "ai engineer":        {"mean": 52, "std": 20},
    "web developer":      {"mean": 62, "std": 14},
    "devops engineer":    {"mean": 54, "std": 16},
    "product manager":    {"mean": 60, "std": 13},
    "backend developer":  {"mean": 57, "std": 15},
    "frontend developer": {"mean": 61, "std": 14},
    "full stack developer":{"mean": 56, "std": 16},
    "ml engineer":        {"mean": 50, "std": 19},
    "cloud architect":    {"mean": 53, "std": 17},
    "mobile developer":   {"mean": 59, "std": 15},
}

NUM_SIMULATED_CANDIDATES = 100


def calculate_ranking(ats_score: int, job_role: str) -> Dict:
    """
    Simulate 100 candidates and calculate user's ranking.

    Returns:
    {
      "percentile": int (0-100),
      "rank": int (1-100),
      "rank_message": str,
      "total_candidates": int,
      "score_distribution": {
        "min": int, "max": int, "average": float, "median": float
      },
      "breakdown": { "top_10": bool, "top_25": bool, "top_50": bool }
    }
    """
    # Get distribution for this role
    role_key = job_role.lower().strip()
    dist = ROLE_DISTRIBUTIONS.get(role_key, {"mean": 55, "std": 16})

    # Generate simulated candidate scores
    np.random.seed(hash(job_role) % 2**31)  # deterministic per role for consistency
    simulated_scores = np.random.normal(dist["mean"], dist["std"], NUM_SIMULATED_CANDIDATES)
    simulated_scores = np.clip(simulated_scores, 10, 98).astype(int)

    # Add user's score
    all_scores = list(simulated_scores)

    # Calculate percentile
    below_count = sum(1 for s in all_scores if s < ats_score)
    percentile = int((below_count / len(all_scores)) * 100)

    # Calculate rank (1 = best)
    sorted_scores = sorted(all_scores, reverse=True)
    rank = 1
    for s in sorted_scores:
        if ats_score >= s:
            break
        rank += 1

    return {
        "percentile": percentile,
        "rank": rank,
        "rank_message": _get_rank_message(percentile),
        "total_candidates": NUM_SIMULATED_CANDIDATES,
        "score_distribution": {
            "min": int(min(all_scores)),
            "max": int(max(all_scores)),
            "average": round(float(np.mean(all_scores)), 1),
            "median": round(float(np.median(all_scores)), 1),
        },
        "breakdown": {
            "top_10": percentile >= 90,
            "top_25": percentile >= 75,
            "top_50": percentile >= 50,
        },
    }


def _get_rank_message(percentile: int) -> str:
    """Generate motivational ranking message."""
    if percentile >= 90:
        return "🏆 Outstanding! You're in the TOP 10% of candidates!"
    elif percentile >= 75:
        return "⭐ Excellent! You're in the TOP 25% — a strong competitor!"
    elif percentile >= 50:
        return "💪 Good job! You rank above average for this role."
    elif percentile >= 25:
        return "🚀 You're building momentum — focus on missing skills to climb higher."
    else:
        return "📈 Keep improving! Follow the skill roadmap to strengthen your profile."
