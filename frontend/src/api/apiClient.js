import axios from 'axios';

/* ──── Base URL — uses Vite proxy in dev, direct URL in production ──── */
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

/* ===================== RESUME UPLOAD ===================== */
export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload-resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

/* ===================== ANALYZE RESUME ===================== */
export async function analyzeResume(resumeId, jobRole, jobDescription) {
  const body = {
    resume_id: resumeId,
    job_role: { role_name: jobRole, experience_level: 'mid' },
  };

  if (jobDescription && jobDescription.trim()) {
    body.job_description = {
      job_title: jobRole,
      description: jobDescription,
      required_skills: [],
    };
  }

  const response = await api.post('/analyze-resume', body);
  return response.data;
}

/* ===================== INTERVIEW QUESTIONS ===================== */
export async function generateInterviewQuestions(resumeId, jobRole, count = 10) {
  const response = await api.post('/generate-questions', {
    resume_id: resumeId,
    job_role: jobRole,
    num_questions: count,
  });
  return response.data;
}

/* ===================== EVALUATE ANSWER ===================== */
export async function evaluateAnswer(question, userAnswer, idealAnswer, category) {
  const response = await api.post('/evaluate-answer', {
    question,
    user_answer: userAnswer,
    ideal_answer: idealAnswer,
    category,
  });
  return response.data;
}

/* ===================== VOICE TO TEXT ===================== */
export async function voiceToText(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  const response = await api.post('/voice-to-text', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

/* ===================== SKILL ROADMAP ===================== */
export async function getSkillRoadmap(jobRole, missingSkills, weeks = 8) {
  const response = await api.post('/skill-roadmap', {
    job_role: jobRole,
    missing_skills: missingSkills,
    weeks,
  });
  return response.data;
}

/* ===================== PROJECT SUGGESTIONS ===================== */
export async function suggestProjects(jobRole, missingSkills, count = 5) {
  const response = await api.post('/suggest-projects', {
    job_role: jobRole,
    missing_skills: missingSkills,
    num_projects: count,
  });
  return response.data;
}

/* ===================== CANDIDATE RANKING ===================== */
export async function getCandidateRanking(atsScore, jobRole) {
  const response = await api.post('/candidate-ranking', {
    ats_score: atsScore,
    job_role: jobRole,
  });
  return response.data;
}

/* ===================== RESUME REWRITER ===================== */
export async function rewriteResume(resumeText, jobRole) {
  const response = await api.post('/rewrite-resume', {
    resume_text: resumeText,
    job_role: jobRole,
  });
  return response.data;
}

/* ===================== WEAKNESS ANALYSIS ===================== */
export async function getWeaknessAnalysis(resumeId) {
  const response = await api.post('/weakness-analysis', {
    resume_id: resumeId,
  });
  return response.data;
}

/* ===================== READINESS SCORE ===================== */
export async function getReadinessScore(atsScore, interviewScore, skillMatchPercent) {
  const response = await api.post('/readiness-score', {
    ats_score: atsScore,
    interview_score: interviewScore,
    skill_match_percent: skillMatchPercent,
  });
  return response.data;
}

/* ===================== PROGRESS HISTORY ===================== */
export async function saveProgress(data) {
  const response = await api.post('/save-progress', data);
  return response.data;
}

export async function getProgressHistory() {
  const response = await api.get('/progress-history');
  return response.data;
}

/* ===================== KEYWORD ANALYSIS ===================== */
export async function getKeywordAnalysis(resumeId, jobDescription, jobRole) {
  const response = await api.post('/keyword-analysis', {
    resume_id: resumeId,
    job_description: jobDescription,
    job_role: jobRole,
  });
  return response.data;
}

/* ===================== RESUME COMPATIBILITY ===================== */
export async function getResumeCompatibility(resumeId, jobDescription, jobRole) {
  const response = await api.post('/resume-compatibility', {
    resume_id: resumeId,
    job_description: jobDescription,
    job_role: jobRole,
  });
  return response.data;
}

/* ===================== RESUME SUMMARY ===================== */
export async function generateSummary(resumeId, jobRole) {
  const response = await api.post('/generate-summary', {
    resume_id: resumeId,
    job_role: jobRole,
  });
  return response.data;
}

export default api;

