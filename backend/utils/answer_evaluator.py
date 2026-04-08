"""
Answer Evaluator — NLP-based interview answer scoring

Evaluates user answers against ideal answers using:
  1. TF-IDF cosine similarity (keyword overlap)
  2. Structural analysis (length, specificity, metrics)
  3. Category-specific criteria (HR vs Technical vs Behavioral)

Returns:
  - score: 0-10
  - feedback: text summary
  - suggestions: list of improvement tips
  - better_answer: improved version of user's answer
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def evaluate_answer_quality(
    question: str,
    user_answer: str,
    ideal_answer: str,
    category: str
) -> dict:
    """
    Evaluate the quality of a user's interview answer.

    Returns dict with: score, feedback, suggestions, better_answer
    """
    if not user_answer or not user_answer.strip():
        return {
            "score": 0,
            "feedback": "No answer provided.",
            "suggestions": ["Try to provide a thoughtful answer."],
            "better_answer": ideal_answer,
        }

    # ── 1. Cosine similarity score ──
    similarity_score = _compute_similarity(user_answer, ideal_answer)

    # ── 2. Length / detail score ──
    length_score = _score_length(user_answer, category)

    # ── 3. Specificity score (numbers, metrics, examples) ──
    specificity_score = _score_specificity(user_answer)

    # ── 4. Structure score (STAR method for behavioral, etc.) ──
    structure_score = _score_structure(user_answer, category)

    # ── Combine scores ──
    raw_score = (
        similarity_score * 0.35 +
        length_score * 0.2 +
        specificity_score * 0.25 +
        structure_score * 0.2
    )

    # Scale to 0-10
    final_score = round(min(10, max(0, raw_score * 10)), 1)

    # ── Generate feedback ──
    feedback = _generate_feedback(final_score, similarity_score, length_score, specificity_score, category)
    suggestions = _generate_suggestions(final_score, user_answer, category)
    better_answer = _generate_better_answer(user_answer, ideal_answer, category)

    return {
        "score": final_score,
        "feedback": feedback,
        "suggestions": suggestions,
        "better_answer": better_answer,
    }


def _compute_similarity(user_answer: str, ideal_answer: str) -> float:
    """Compute TF-IDF cosine similarity between answers."""
    try:
        vectorizer = TfidfVectorizer(max_features=300, stop_words='english')
        matrix = vectorizer.fit_transform([user_answer.lower(), ideal_answer.lower()])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(sim)
    except Exception:
        return 0.3


def _score_length(answer: str, category: str) -> float:
    """Score based on answer length (too short or too long is bad)."""
    word_count = len(answer.split())
    ideal_min = 30 if category == "HR" else 50
    ideal_max = 200 if category == "HR" else 300

    if word_count < 10:
        return 0.1
    elif word_count < ideal_min:
        return 0.3 + (word_count / ideal_min) * 0.3
    elif word_count <= ideal_max:
        return 0.8
    else:
        return 0.6  # slightly penalize very long answers


def _score_specificity(answer: str) -> float:
    """Score based on specific details: numbers, percentages, examples."""
    score = 0.3  # baseline

    # Check for numbers/metrics
    if re.search(r'\d+%', answer):
        score += 0.2
    if re.search(r'\d+', answer):
        score += 0.1

    # Check for specific action verbs
    action_verbs = ['developed', 'implemented', 'led', 'created', 'built', 'designed',
                    'optimized', 'improved', 'reduced', 'increased', 'managed', 'delivered']
    for verb in action_verbs:
        if verb in answer.lower():
            score += 0.05
            if score >= 0.9:
                break

    # Check for specific examples
    if any(word in answer.lower() for word in ['for example', 'specifically', 'instance', 'project']):
        score += 0.1

    return min(1.0, score)


def _score_structure(answer: str, category: str) -> float:
    """Score based on answer structure."""
    score = 0.4  # baseline
    answer_lower = answer.lower()

    if category == "Behavioral":
        # Check for STAR method elements
        star_keywords = ['situation', 'task', 'action', 'result']
        for kw in star_keywords:
            if kw in answer_lower:
                score += 0.15

    elif category == "Technical":
        # Check for structured technical answer
        if any(w in answer_lower for w in ['first', 'second', 'then', 'finally', 'step']):
            score += 0.2
        if any(w in answer_lower for w in ['because', 'reason', 'advantage', 'tradeoff']):
            score += 0.15

    # General: having multiple sentences shows completeness
    sentence_count = len([s for s in answer.split('.') if s.strip()])
    if sentence_count >= 3:
        score += 0.1

    return min(1.0, score)


def _generate_feedback(score, similarity, length_score, specificity, category):
    """Generate human-readable feedback."""
    if score >= 8:
        return "Excellent answer! You demonstrated strong knowledge with specific examples and clear structure. This would impress interviewers."
    elif score >= 6:
        return "Good answer with solid content. Consider adding more specific metrics or examples to make it even stronger."
    elif score >= 4:
        return "Decent start, but your answer needs more depth. Add specific examples, quantify your achievements, and structure your response better."
    elif score >= 2:
        return "Your answer is too brief or generic. Interviewers want to hear specific experiences with measurable outcomes."
    else:
        return "This answer needs significant improvement. Try using the STAR method and include concrete examples from your experience."


def _generate_suggestions(score, answer, category):
    """Generate specific improvement suggestions."""
    suggestions = []

    word_count = len(answer.split())

    if word_count < 30:
        suggestions.append("Expand your answer to at least 3-4 sentences with specific details")

    if not re.search(r'\d+', answer):
        suggestions.append("Add quantifiable metrics (e.g., 'improved performance by 30%')")

    if category == "Behavioral" and 'situation' not in answer.lower():
        suggestions.append("Use the STAR method: Situation → Task → Action → Result")

    if category == "Technical" and not any(w in answer.lower() for w in ['because', 'reason', 'tradeoff']):
        suggestions.append("Explain the 'why' behind your technical decisions")

    action_verbs = ['developed', 'implemented', 'led', 'built', 'designed', 'optimized']
    if not any(v in answer.lower() for v in action_verbs):
        suggestions.append("Use strong action verbs: Developed, Implemented, Led, Optimized")

    if not suggestions:
        suggestions.append("Great job! Consider adding one more specific example for impact")

    return suggestions[:4]


def _generate_better_answer(user_answer, ideal_answer, category):
    """Generate an improved version of the user's answer."""
    user_words = user_answer.split()

    if len(user_words) < 15:
        return ideal_answer

    # Combine user's key points with ideal answer structure
    prefix = "Here's a stronger version: "
    if category == "Behavioral":
        return f"{prefix}Using the STAR method — SITUATION: [Draw from your experience]. TASK: [Your specific responsibility]. ACTION: I {' '.join(user_words[:10])}... [add specific steps you took]. RESULT: [Include measurable outcome, e.g., 'reduced processing time by 40%']."
    elif category == "Technical":
        return f"{prefix}{ideal_answer}"
    else:
        return f"{prefix}Drawing from my experience, {user_answer.strip()}. Additionally, {ideal_answer.split('.')[0] if ideal_answer else 'I bring strong problem-solving skills to the team'}."
