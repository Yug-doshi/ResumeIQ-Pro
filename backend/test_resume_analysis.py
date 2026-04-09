"""
Comprehensive Resume Analysis Tester
Extracts text from all uploaded resumes, runs the full scoring pipeline,
and outputs detailed results for manual verification.
"""

import os
import sys
import json

import builtins

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.file_handler import extract_text_from_resume
from utils.nlp_scorer import calculate_ats_score, extract_skills, get_missing_skills
from utils.lstm_scorer import get_lstm_score
from utils.weakness_detector import analyze_weaknesses
from utils.shortlist_predictor import predict_shortlist_chance
from utils.keyword_optimizer import analyze_keywords
from utils.ranking_engine import calculate_ranking

UPLOAD_DIR = "uploads"

# Make console output robust on Windows terminals that aren't UTF-8.
_real_print = builtins.print
def _safe_print(*args, **kwargs):
    enc = getattr(sys.stdout, "encoding", None) or "cp1252"
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    s = sep.join(str(a) for a in args) + end
    s = s.encode(enc, errors="replace").decode(enc, errors="replace")
    kwargs2 = dict(kwargs)
    kwargs2.pop("sep", None)
    kwargs2.pop("end", None)
    _real_print(s, **kwargs2)

builtins.print = _safe_print

# A generic Software Engineer JD for testing
TEST_JD = """
We are looking for a Software Engineer with experience in Python, JavaScript, 
React, Node.js, SQL, Docker, AWS, Git, REST APIs, and agile methodologies.
Requirements:
- 2+ years experience in software development
- Proficiency in Python and JavaScript
- Experience with React or Angular
- Database experience (SQL, MongoDB)
- Version control with Git
- CI/CD pipelines
- Cloud services (AWS/GCP/Azure)
- Strong problem-solving skills
"""

TEST_JD_DS = """
We are looking for a Data Scientist with strong experience in Python, R, SQL,
machine learning, deep learning, TensorFlow, PyTorch, Pandas, NumPy, statistics,
data visualization, and feature engineering.
Requirements:
- 3+ years experience in data science or machine learning
- Strong Python programming skills
- Experience with ML frameworks (TensorFlow, PyTorch, scikit-learn)
- SQL proficiency
- Statistical analysis and modeling
- Data visualization (Matplotlib, Tableau)
"""

def analyze_single_resume(file_path, filename):
    """Run full analysis pipeline on a single resume."""
    print(f"\n{'='*80}")
    print(f"  RESUME: {filename}")
    print(f"{'='*80}")
    
    # Step 1: Extract text
    try:
        text = extract_text_from_resume(file_path)
    except Exception as e:
        print(f"  ERROR extracting text: {e}")
        return None
    
    word_count = len(text.split())
    print(f"\n  Word count: {word_count}")
    print(f"  Text preview (first 800 chars):")
    print(f"  ---")
    for line in text[:800].split('\n'):
        try:
            print(f"    {line}")
        except UnicodeEncodeError:
            enc = getattr(getattr(__import__("sys"), "stdout", None), "encoding", None) or "cp1252"
            safe_line = line.encode(enc, errors="replace").decode(enc, errors="replace")
            print(f"    {safe_line}")
    print(f"  ---")
    
    # Step 2: Extract skills
    skills = extract_skills(text)
    print(f"\n  Skills found ({len(skills)}): {', '.join(skills)}")
    
    # Step 3: LSTM scoring (with SWE JD)
    lstm_result_swe = get_lstm_score(text, TEST_JD)
    print(f"\n  LSTM Score (vs SWE JD):")
    print(f"     Match Score: {lstm_result_swe['match_score']}")
    print(f"     Selection Prob: {lstm_result_swe['selection_probability']}")
    print(f"     Method: {lstm_result_swe['method']}")
    
    # Step 4: NLP scoring
    nlp_score_swe, kw_pct_swe = calculate_ats_score(text, TEST_JD, "Software Engineer")
    print(f"\n  NLP ATS Score (vs SWE JD):")
    print(f"     ATS Score: {nlp_score_swe}")
    print(f"     Keyword Match %: {kw_pct_swe}")
    
    # Step 5: Blended score
    if lstm_result_swe["method"] == "lstm":
        final_swe = int(lstm_result_swe["match_score"] * 0.6 + nlp_score_swe * 0.4)
    else:
        final_swe = int(lstm_result_swe["match_score"] * 0.4 + nlp_score_swe * 0.6)
    final_swe = min(100, max(0, final_swe))
    print(f"     Final Blended Score: {final_swe}")
    
    # Step 6: Weakness analysis
    weakness = analyze_weaknesses(text)
    print(f"\n  Weakness Analysis (overall: {weakness['overall_score']}/100):")
    for section, data in weakness["sections"].items():
        print(f"     {section}: {data['score']}/100 ({data['status']})")
        for tip in data["tips"][:2]:
            print(f"       → {tip}")
    
    if weakness["critical_issues"]:
        print(f"\n  Critical Issues:")
        for issue in weakness["critical_issues"]:
            print(f"     {issue}")
    
    if weakness["strengths"]:
        print(f"\n  Strengths:")
        for s in weakness["strengths"]:
            print(f"     {s}")
    
    # Step 7: Shortlist prediction
    shortlist = predict_shortlist_chance(text, TEST_JD, "Software Engineer")
    print(f"\n  Shortlist Prediction (vs SWE role):")
    print(f"     Probability: {shortlist['shortlist_probability']}%")
    print(f"     Label: {shortlist['prediction_label']}")
    print(f"     Confidence: {shortlist['confidence_level']}")
    print(f"     Detailed Scores:")
    for k, v in shortlist["detailed_scores"].items():
        print(f"       {k}: {v}")
    
    # Step 8: Keyword analysis
    keywords = analyze_keywords(text, TEST_JD, "Software Engineer")
    print(f"\n  Keyword Analysis:")
    print(f"     ATS Optimization Score: {keywords['ats_optimization_score']}")
    print(f"     Matched Keywords: {len(keywords['matched_keywords'])}")
    print(f"     Missing Keywords: {len(keywords['missing_keywords'])}")
    print(f"     Action Verbs Score: {keywords['action_verbs']['score']}")
    matched_kws = [m['keyword'] for m in keywords['matched_keywords'][:8]]
    missing_kws = [m['keyword'] for m in keywords['missing_keywords'][:8]]
    print(f"     Top Matched: {', '.join(matched_kws)}")
    print(f"     Top Missing: {', '.join(missing_kws)}")
    
    # Step 9: Ranking
    ranking = calculate_ranking(final_swe, "Software Engineer")
    print(f"\n  Ranking (among 100 simulated candidates):")
    print(f"     Percentile: {ranking['percentile']}th")
    print(f"     Rank: #{ranking['rank']}")
    print(f"     Message: {ranking['rank_message']}")
    
    # Step 10: My manual assessment
    print(f"\n  MANUAL SKILL VERIFICATION:")
    text_lower = text.lower()
    
    # Check specific technologies
    check_skills = {
        "python": ["python"],
        "javascript": ["javascript", "js"],
        "java": ["java"],
        "react": ["react"],
        "node.js": ["node.js", "nodejs", "node"],
        "sql": ["sql", "mysql", "postgresql"],
        "docker": ["docker"],
        "aws": ["aws", "amazon web services"],
        "git": ["git", "github"],
        "machine learning": ["machine learning", "ml"],
        "tensorflow": ["tensorflow"],
        "pytorch": ["pytorch"],
        "deep learning": ["deep learning"],
        "html/css": ["html", "css"],
        "mongodb": ["mongodb", "mongo"],
        "kubernetes": ["kubernetes", "k8s"],
        "ci/cd": ["ci/cd", "cicd", "continuous integration"],
        "agile": ["agile", "scrum"],
    }
    
    present = []
    absent = []
    for skill, variants in check_skills.items():
        found = any(v in text_lower for v in variants)
        if found:
            present.append(skill)
        else:
            absent.append(skill)
    
    print(f"     Present: {', '.join(present)}")
    print(f"     Absent: {', '.join(absent)}")
    
    # Check resume structure
    sections_check = {
        "summary/objective": any(w in text_lower for w in ["summary", "objective", "profile", "about"]),
        "experience": any(w in text_lower for w in ["experience", "work history", "employment"]),
        "education": any(w in text_lower for w in ["education", "degree", "university", "college"]),
        "projects": any(w in text_lower for w in ["project", "portfolio"]),
        "skills": any(w in text_lower for w in ["skills", "technologies", "tools"]),
        "certifications": any(w in text_lower for w in ["certif", "certification"]),
    }
    print(f"\n  📋 SECTION VERIFICATION:")
    for section, exists in sections_check.items():
        icon = "✅" if exists else "❌"
        print(f"     {icon} {section}")
    
    # Check for metrics/quantification
    import re
    metrics = re.findall(r'\d+%|\$\d+|\d+\+?\s*(users|clients|customers|projects|team)', text_lower)
    has_action_verbs = sum(1 for v in ["developed", "implemented", "led", "built", "created", "designed", "optimized", "managed", "deployed"] if v in text_lower)
    print(f"\n  📊 IMPACT METRICS:")
    print(f"     Quantifiable metrics found: {len(metrics)}")
    print(f"     Action verbs found: {has_action_verbs}")
    
    # Give MY assessment
    my_swe_score = 0
    # Skills match for SWE
    swe_skills = ["python", "javascript", "react", "sql", "docker", "aws", "git", "ci/cd", "node.js", "agile"]
    swe_matched = sum(1 for s in swe_skills if s in present)
    my_swe_score = int((swe_matched / len(swe_skills)) * 40)  # 40% for skills
    
    # Sections
    section_count = sum(1 for v in sections_check.values() if v)
    my_swe_score += int((section_count / 6) * 20)  # 20% for sections
    
    # Metrics & impact
    my_swe_score += min(20, len(metrics) * 4 + has_action_verbs * 2)  # 20% for impact
    
    # Word count (content depth)
    if word_count > 300:
        my_swe_score += 10
    elif word_count > 150:
        my_swe_score += 5
    
    # Experience indicators
    if any(w in text_lower for w in ["years", "senior", "lead", "experience"]):
        my_swe_score += 10
    
    my_swe_score = min(100, my_swe_score)
    
    print(f"\n  🔍 MY ASSESSMENT vs MODEL:")
    print(f"     My estimated SWE score:    {my_swe_score}")
    print(f"     Model's blended score:     {final_swe}")
    print(f"     LSTM raw score:            {lstm_result_swe['match_score']}")
    print(f"     NLP raw score:             {nlp_score_swe}")
    print(f"     Shortlist prediction:      {shortlist['shortlist_probability']}%")
    
    diff = abs(my_swe_score - final_swe)
    if diff <= 10:
        print(f"     ✅ Scores aligned (diff: {diff})")
    elif diff <= 20:
        print(f"     ⚠️ Moderate deviation (diff: {diff})")
    else:
        print(f"     🔴 SIGNIFICANT DEVIATION (diff: {diff}) — needs investigation")
    
    return {
        "filename": filename,
        "word_count": word_count,
        "skills_found": skills,
        "skills_count": len(skills),
        "lstm_score": lstm_result_swe["match_score"],
        "nlp_score": nlp_score_swe,
        "blended_score": final_swe,
        "method": lstm_result_swe["method"],
        "weakness_overall": weakness["overall_score"],
        "shortlist_probability": shortlist["shortlist_probability"],
        "shortlist_label": shortlist["prediction_label"],
        "keyword_optimization": keywords["ats_optimization_score"],
        "ranking_percentile": ranking["percentile"],
        "my_assessment": my_swe_score,
        "deviation": diff,
        "present_skills": present,
        "absent_skills": absent,
        "sections": sections_check,
        "text_preview": text[:500],
    }


def main():
    print("=" * 80)
    print("  RESUMEIQ PRO — COMPREHENSIVE MODEL VERIFICATION TEST")
    print("=" * 80)
    
    files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(('.pdf', '.docx'))]
    print(f"\n  Found {len(files)} uploaded resumes to analyze.\n")
    
    results = []
    for filename in sorted(files):
        file_path = os.path.join(UPLOAD_DIR, filename)
        result = analyze_single_resume(file_path, filename)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n\n{'='*80}")
    print(f"  SUMMARY OF ALL RESUMES")
    print(f"{'='*80}")
    print(f"\n  {'Filename':<50} {'LSTM':>6} {'NLP':>6} {'Blend':>6} {'MyEst':>6} {'Diff':>6} {'Shortlist':>10} {'Skills':>7}")
    print(f"  {'-'*50} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*10} {'-'*7}")
    
    for r in results:
        short_name = r['filename'][:48]
        print(f"  {short_name:<50} {r['lstm_score']:>6} {r['nlp_score']:>6} {r['blended_score']:>6} {r['my_assessment']:>6} {r['deviation']:>6} {r['shortlist_probability']:>9}% {r['skills_count']:>7}")
    
    # Issues detected
    deviations = [r for r in results if r['deviation'] > 15]
    if deviations:
        print(f"\n  🔴 RESUMES WITH SCORE DEVIATIONS > 15:")
        for r in deviations:
            print(f"     - {r['filename']}: Model={r['blended_score']}, Expected≈{r['my_assessment']}, Diff={r['deviation']}")
            print(f"       Skills: {', '.join(r['present_skills'][:6])}")
            print(f"       Missing: {', '.join(r['absent_skills'][:6])}")
    
    # Save results as JSON
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  📁 Detailed results saved to test_results.json")


if __name__ == "__main__":
    main()
