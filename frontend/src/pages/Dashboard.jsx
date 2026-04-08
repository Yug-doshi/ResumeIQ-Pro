import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  BarChart3, Trophy, Lightbulb, AlertTriangle, Loader2,
  ArrowRight, Mic, Map, FolderGit2, FileEdit, Target, Shield, Zap, Sparkles, Copy, CheckCheck
} from 'lucide-react';
import toast from 'react-hot-toast';
import ScoreGauge from '../components/ScoreGauge';
import SkillHeatmap from '../components/SkillHeatmap';
import { analyzeResume, getCandidateRanking, getWeaknessAnalysis, getKeywordAnalysis, generateSummary, predictShortlist } from '../api/apiClient';

/* ──── Job role options ──── */
const JOB_ROLES = [
  'Software Engineer', 'Data Scientist', 'AI Engineer', 'Web Developer',
  'DevOps Engineer', 'Product Manager', 'Backend Developer', 'Frontend Developer',
  'Full Stack Developer', 'ML Engineer', 'Cloud Architect', 'Mobile Developer',
];

function Dashboard({ resumeData, analysisData, setAnalysisData, loading, setLoading }) {
  const navigate = useNavigate();
  const [jobRole, setJobRole] = useState('Software Engineer');
  const [jobDescription, setJobDescription] = useState('');
  const [analyzing, setAnalyzing] = useState(false);

  /* ── Redirect if no resume ── */
  if (!resumeData) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card-solid p-10 text-center max-w-md"
        >
          <BarChart3 className="w-12 h-12 text-brand-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2 text-gray-800 dark:text-gray-200">
            No Resume Uploaded
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mb-6">
            Upload your resume first to access the dashboard
          </p>
          <button onClick={() => navigate('/upload')} className="btn-primary">
            Upload Resume
          </button>
        </motion.div>
      </div>
    );
  }

  /* ── Run analysis ── */
  const handleAnalyze = async () => {
    setAnalyzing(true);
    setLoading(true);

    try {
      /* Step 1: Analyze resume */
      const result = await analyzeResume(resumeData.resume_id, jobRole, jobDescription);

      /* Step 2: Get ranking */
      let ranking = null;
      try {
        ranking = await getCandidateRanking(result.ats_score, jobRole);
      } catch (e) {
        /* ranking is optional */
      }

      /* Step 3: Get weakness analysis */
      let weakness = null;
      try {
        weakness = await getWeaknessAnalysis(resumeData.resume_id);
      } catch (e) {
        /* weakness is optional */
      }

      /* Step 4: Keyword analysis */
      let keywords = null;
      try {
        keywords = await getKeywordAnalysis(resumeData.resume_id, jobDescription, jobRole);
      } catch (e) {
        /* keywords is optional */
      }

      /* Step 5: Resume summary */
      let summary = null;
      try {
        summary = await generateSummary(resumeData.resume_id, jobRole);
      } catch (e) {
        /* summary is optional */
      }

      /* Step 6: Shortlist prediction */
      let shortlist = null;
      try {
        shortlist = await predictShortlist(resumeData.resume_id, jobDescription, jobRole);
      } catch (e) {
        /* shortlist is optional */
      }

      const fullResult = { ...result, ranking, weakness, keywords, summary, shortlist };
      setAnalysisData(fullResult);
      toast.success('Analysis complete! 🎉');
    } catch (err) {
      toast.error('Analysis failed. Make sure the backend is running.');
      console.error(err);
    } finally {
      setAnalyzing(false);
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* ═══════ LEFT SIDEBAR ═══════ */}
        <aside className="lg:col-span-4 xl:col-span-3 space-y-6">
          {/* Resume Info */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="glass-card-solid p-5"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center shadow-md">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-800 dark:text-gray-200 text-sm">
                  Uploaded Resume
                </h3>
                <p className="text-xs text-gray-500 truncate max-w-[180px]">
                  {resumeData.filename}
                </p>
              </div>
            </div>

            {/* Job Role selector */}
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                  Target Job Role
                </label>
                <select
                  value={jobRole}
                  onChange={(e) => setJobRole(e.target.value)}
                  className="input-field text-sm"
                >
                  {JOB_ROLES.map((role) => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                  Job Description (optional)
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here for more accurate analysis..."
                  rows={5}
                  className="input-field text-sm resize-none"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {analyzing ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
                ) : (
                  <><Zap className="w-4 h-4" /> Analyze Resume</>
                )}
              </button>
            </div>
          </motion.div>

          {/* Quick Actions */}
          {analysisData && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card-solid p-5 space-y-2"
            >
              <h4 className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-3">
                Quick Actions
              </h4>
              {[
                { to: '/interview', icon: Mic, label: 'Practice Interview', color: 'text-purple-500' },
                { to: '/roadmap', icon: Map, label: 'Skill Roadmap', color: 'text-emerald-500' },
                { to: '/projects', icon: FolderGit2, label: 'Project Ideas', color: 'text-amber-500' },
                { to: '/rewriter', icon: FileEdit, label: 'Rewrite Resume', color: 'text-cyan-500' },
              ].map((action) => {
                const Icon = action.icon;
                return (
                  <button
                    key={action.to}
                    onClick={() => navigate(action.to)}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-gray-50 dark:hover:bg-surface-800 transition-colors group text-left"
                  >
                    <Icon className={`w-5 h-5 ${action.color}`} />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300 flex-1">
                      {action.label}
                    </span>
                    <ArrowRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                );
              })}
            </motion.div>
          )}
        </aside>

        {/* ═══════ MAIN CONTENT ═══════ */}
        <main className="lg:col-span-8 xl:col-span-9 space-y-6">
          {analysisData ? (
            <>
              {/* ── Row 1: Score + Ranking ── */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* ATS Score */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass-card-solid p-6 flex flex-col items-center"
                >
                  <ScoreGauge score={analysisData.ats_score} size={160} label="ATS Score" />
                  <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
                    Keyword match: <strong>{analysisData.keyword_match_percentage}%</strong>
                  </p>
                </motion.div>

                {/* Selection Probability */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="glass-card-solid p-6 flex flex-col items-center"
                >
                  <ScoreGauge
                    score={analysisData.selection_probability || Math.min(95, analysisData.ats_score + 10)}
                    size={160}
                    label="Selection Chance"
                    color="#8b5cf6"
                  />
                  <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
                    ML model prediction
                  </p>
                </motion.div>

                {/* Ranking */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="glass-card-solid p-6 flex flex-col items-center justify-center"
                >
                  {analysisData.ranking ? (
                    <>
                      <div className="w-14 h-14 rounded-2xl bg-amber-500/10 flex items-center justify-center mb-3">
                        <Trophy className="w-7 h-7 text-amber-500" />
                      </div>
                      <p className="text-3xl font-black text-gray-800 dark:text-gray-200">
                        Top {100 - (analysisData.ranking.percentile || 50)}%
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 text-center">
                        {analysisData.ranking.rank_message}
                      </p>
                    </>
                  ) : (
                    <>
                      <Trophy className="w-8 h-8 text-gray-300 dark:text-gray-600 mb-2" />
                      <p className="text-sm text-gray-400">Ranking unavailable</p>
                    </>
                  )}
                </motion.div>
              </div>

              {/* ── Row 1.5: Shortlist Prediction ── */}
              {analysisData.shortlist && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.25 }}
                  className="glass-card-solid p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Target className="w-5 h-5 text-purple-500" />
                      <h3 className="font-bold text-gray-800 dark:text-gray-200">
                        Shortlisting Prediction
                      </h3>
                      <span className="badge badge-purple">AI NLC</span>
                    </div>
                    <span className="text-xs text-gray-500">Confidence: {analysisData.shortlist.confidence_level}</span>
                  </div>

                  <div className="flex flex-col md:flex-row items-center gap-6">
                    {/* Big probability number */}
                    <div className="text-center">
                      <div className={`w-32 h-32 rounded-3xl border-2 flex flex-col items-center justify-center ${
                        analysisData.shortlist.shortlist_probability >= 65 ? 'bg-emerald-500/10 border-emerald-500/20' :
                        analysisData.shortlist.shortlist_probability >= 40 ? 'bg-amber-500/10 border-amber-500/20' :
                        'bg-red-500/10 border-red-500/20'
                      }`}>
                        <span className={`text-4xl font-black ${
                          analysisData.shortlist.shortlist_probability >= 65 ? 'text-emerald-500' :
                          analysisData.shortlist.shortlist_probability >= 40 ? 'text-amber-500' :
                          'text-red-500'
                        }`}>
                          {analysisData.shortlist.shortlist_probability}%
                        </span>
                        <span className="text-xs text-gray-500 mt-1">Shortlist Chance</span>
                      </div>
                      <p className="text-sm font-semibold mt-2 text-gray-700 dark:text-gray-300">
                        {analysisData.shortlist.prediction_label}
                      </p>
                    </div>

                    {/* Key Factors */}
                    <div className="flex-1 w-full">
                      <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">Key Factors</p>
                      <div className="space-y-2">
                        {(analysisData.shortlist.key_factors || []).slice(0, 5).map((f, i) => (
                          <div key={i} className="flex items-center gap-3">
                            <span className="text-sm">{f.emoji}</span>
                            <span className="text-sm text-gray-700 dark:text-gray-300 flex-1">{f.factor}</span>
                            <div className="w-24 h-1.5 bg-gray-200 dark:bg-surface-800 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  f.impact === 'positive' ? 'bg-emerald-500' :
                                  f.impact === 'negative' ? 'bg-red-500' : 'bg-amber-500'
                                }`}
                                style={{ width: `${f.score}%` }}
                              />
                            </div>
                            <span className="text-xs font-bold text-gray-500 w-10 text-right">{f.score}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Improvements */}
                  {analysisData.shortlist.improvements?.length > 0 && (
                    <div className="mt-4 p-4 rounded-xl bg-brand-500/5 dark:bg-brand-500/10 border border-brand-500/20">
                      <p className="text-xs font-semibold text-brand-600 dark:text-brand-400 mb-2">💡 How to Improve</p>
                      <ul className="space-y-1">
                        {analysisData.shortlist.improvements.map((imp, i) => (
                          <li key={i} className="text-sm text-gray-600 dark:text-gray-400">{imp}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              )}

              {/* ── Row 2: Skills ── */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Matching Skills */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="glass-card-solid p-6"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Shield className="w-5 h-5 text-emerald-500" />
                    <h3 className="font-bold text-gray-800 dark:text-gray-200">
                      Matching Skills
                    </h3>
                    <span className="badge badge-green ml-auto">
                      {analysisData.matching_skills?.length || 0}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(analysisData.matching_skills || []).map((skill, i) => (
                      <span
                        key={i}
                        className="px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 text-sm font-medium border border-emerald-200 dark:border-emerald-800/40"
                      >
                        ✓ {skill}
                      </span>
                    ))}
                    {(!analysisData.matching_skills || analysisData.matching_skills.length === 0) && (
                      <p className="text-sm text-gray-400">No matching skills found</p>
                    )}
                  </div>
                </motion.div>

                {/* Missing Skills */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="glass-card-solid p-6"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <h3 className="font-bold text-gray-800 dark:text-gray-200">
                      Missing Skills
                    </h3>
                    <span className="badge badge-red ml-auto">
                      {analysisData.missing_skills?.length || 0}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(analysisData.missing_skills || []).map((skill, i) => (
                      <span
                        key={i}
                        className="px-3 py-1.5 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm font-medium border border-red-200 dark:border-red-800/40"
                      >
                        ✗ {skill}
                      </span>
                    ))}
                    {(!analysisData.missing_skills || analysisData.missing_skills.length === 0) && (
                      <p className="text-sm text-gray-400">No missing skills detected</p>
                    )}
                  </div>
                </motion.div>
              </div>

              {/* ── Row 3: Heatmap ── */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <SkillHeatmap
                  matchingSkills={analysisData.matching_skills || []}
                  missingSkills={analysisData.missing_skills || []}
                />
              </motion.div>

              {/* ── Row 4: Suggestions + Weakness ── */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Suggestions */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="glass-card-solid p-6"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Lightbulb className="w-5 h-5 text-amber-500" />
                    <h3 className="font-bold text-gray-800 dark:text-gray-200">
                      AI Recommendations
                    </h3>
                  </div>
                  <ul className="space-y-3">
                    {(analysisData.suggestions || []).map((tip, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        <span className="mt-0.5 flex-shrink-0">{tip.startsWith('🔴') || tip.startsWith('🟡') || tip.startsWith('🟢') ? '' : '→'}</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </motion.div>

                {/* Rewritten Bullets */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 }}
                  className="glass-card-solid p-6"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <FileEdit className="w-5 h-5 text-cyan-500" />
                    <h3 className="font-bold text-gray-800 dark:text-gray-200">
                      Improved Bullet Points
                    </h3>
                  </div>
                  <ul className="space-y-3">
                    {(analysisData.rewritten_bullets || []).map((bullet, i) => (
                      <li key={i} className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed pl-4 border-l-2 border-brand-500/30">
                        {bullet}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              </div>

              {/* ── Row 5: Keyword Optimization ── */}
              {analysisData.keywords && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8 }}
                  className="glass-card-solid p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Target className="w-5 h-5 text-purple-500" />
                      <h3 className="font-bold text-gray-800 dark:text-gray-200">
                        ATS Keyword Optimizer
                      </h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Optimization Score:</span>
                      <span className={`text-lg font-bold ${
                        analysisData.keywords.ats_optimization_score >= 70 ? 'text-emerald-500' :
                        analysisData.keywords.ats_optimization_score >= 40 ? 'text-amber-500' : 'text-red-500'
                      }`}>
                        {analysisData.keywords.ats_optimization_score}/100
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    {/* Action Verbs Score */}
                    <div className="p-4 rounded-xl bg-brand-500/5 dark:bg-brand-500/10 border border-brand-500/20">
                      <p className="text-sm font-semibold text-brand-600 dark:text-brand-400 mb-1">Action Verbs</p>
                      <p className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                        {analysisData.keywords.action_verbs?.score || 0}%
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {(analysisData.keywords.action_verbs?.found || []).slice(0, 4).map((v, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400">
                            {v}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Matched Keywords */}
                    <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-800/30">
                      <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400 mb-1">Matched Keywords</p>
                      <p className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                        {analysisData.keywords.matched_keywords?.length || 0}
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {(analysisData.keywords.matched_keywords || []).slice(0, 4).map((k, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400">
                            {k.keyword}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Missing Keywords */}
                    <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30">
                      <p className="text-sm font-semibold text-red-600 dark:text-red-400 mb-1">Missing Keywords</p>
                      <p className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                        {analysisData.keywords.missing_keywords?.length || 0}
                      </p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {(analysisData.keywords.missing_keywords || []).filter(k => k.importance === 'critical').slice(0, 4).map((k, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 rounded bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400">
                            ❗{k.keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Placement Suggestions */}
                  {analysisData.keywords.placement_suggestions?.length > 0 && (
                    <div className="p-4 rounded-xl bg-gray-50 dark:bg-surface-800 space-y-2">
                      <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">📌 Where to Add Keywords</p>
                      {analysisData.keywords.placement_suggestions.map((s, i) => (
                        <p key={i} className="text-sm text-gray-600 dark:text-gray-400">{s}</p>
                      ))}
                    </div>
                  )}

                  {/* Scoring method badge */}
                  <div className="mt-4 flex items-center gap-2">
                    <span className={`badge ${analysisData.scoring_method === 'lstm' ? 'badge-purple' : 'badge-blue'}`}>
                      {analysisData.scoring_method === 'lstm' ? '🧠 LSTM Model' : '⚡ TF-IDF Fallback'}
                    </span>
                    <span className="text-xs text-gray-500">
                      Scored by {analysisData.scoring_method === 'lstm' ? 'trained neural network' : 'TF-IDF cosine similarity'}
                    </span>
                  </div>
                </motion.div>
              )}

              {/* ── Row 6: AI Summary Generator ── */}
              {analysisData.summary && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.9 }}
                  className="glass-card-solid p-6"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Sparkles className="w-5 h-5 text-amber-500" />
                    <h3 className="font-bold text-gray-800 dark:text-gray-200">
                      AI-Generated Professional Summary
                    </h3>
                  </div>

                  {/* Professional Summary */}
                  <div className="p-4 rounded-xl bg-gradient-to-r from-brand-500/5 to-purple-500/5 dark:from-brand-500/10 dark:to-purple-500/10 border border-brand-500/20 mb-4">
                    <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed italic">
                      "{analysisData.summary.professional_summary}"
                    </p>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(analysisData.summary.professional_summary);
                        toast.success('Summary copied!');
                      }}
                      className="mt-2 text-xs text-brand-500 hover:text-brand-400 flex items-center gap-1"
                    >
                      <Copy className="w-3 h-3" /> Copy to clipboard
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Elevator Pitch */}
                    <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800/30">
                      <p className="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-2">🎤 Elevator Pitch</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        {analysisData.summary.elevator_pitch}
                      </p>
                    </div>

                    {/* LinkedIn Headline */}
                    <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800/30">
                      <p className="text-sm font-semibold text-blue-700 dark:text-blue-400 mb-2">💼 LinkedIn Headline</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                        {analysisData.summary.linkedin_headline}
                      </p>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(analysisData.summary.linkedin_headline);
                          toast.success('Headline copied!');
                        }}
                        className="mt-2 text-xs text-blue-500 hover:text-blue-400 flex items-center gap-1"
                      >
                        <Copy className="w-3 h-3" /> Copy
                      </button>
                    </div>
                  </div>

                  {/* Key Strengths */}
                  {analysisData.summary.key_strengths?.length > 0 && (
                    <div className="mt-4 p-4 rounded-xl bg-gray-50 dark:bg-surface-800">
                      <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">💪 Key Strengths</p>
                      <ul className="space-y-1">
                        {analysisData.summary.key_strengths.map((s, i) => (
                          <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                            <CheckCheck className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" /> {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              )}
            </>
          ) : (
            /* ── Empty state ── */
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-card-solid p-16 text-center"
            >
              <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-brand-500/10 flex items-center justify-center">
                <BarChart3 className="w-10 h-10 text-brand-500" />
              </div>
              <h2 className="text-2xl font-bold mb-3 text-gray-800 dark:text-gray-200">
                Ready to Analyze?
              </h2>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto mb-6">
                Select your target job role and optionally paste a job description.
                Our LSTM model will score your resume and provide detailed insights.
              </p>
              <div className="flex justify-center gap-3">
                <span className="badge badge-purple">LSTM Scoring</span>
                <span className="badge badge-blue">NLP Analysis</span>
                <span className="badge badge-green">Smart Matching</span>
              </div>
            </motion.div>
          )}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;
