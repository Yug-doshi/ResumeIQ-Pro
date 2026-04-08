import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Github, Loader2, Star, GitFork, Code2, Users, BookOpen,
  ExternalLink, TrendingUp, Zap, AlertTriangle, CheckCircle,
  BarChart3, Globe, Calendar, ArrowUpRight, Sparkles
} from 'lucide-react';
import toast from 'react-hot-toast';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { analyzeGitHub } from '../api/apiClient';

const SCORE_COLORS = {
  excellent: 'text-emerald-500',
  good: 'text-brand-500',
  fair: 'text-amber-500',
  low: 'text-red-500',
};

function getScoreColor(score) {
  if (score >= 75) return SCORE_COLORS.excellent;
  if (score >= 50) return SCORE_COLORS.good;
  if (score >= 30) return SCORE_COLORS.fair;
  return SCORE_COLORS.low;
}

function getScoreBg(score) {
  if (score >= 75) return 'bg-emerald-500/10 border-emerald-500/20';
  if (score >= 50) return 'bg-brand-500/10 border-brand-500/20';
  if (score >= 30) return 'bg-amber-500/10 border-amber-500/20';
  return 'bg-red-500/10 border-red-500/20';
}

function GitHubAnalyzer() {
  const [githubInput, setGithubInput] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!githubInput.trim()) {
      toast.error('Please enter a GitHub username or URL');
      return;
    }
    setAnalyzing(true);
    try {
      const data = await analyzeGitHub(githubInput.trim());
      if (data.success === false) {
        toast.error(data.error || 'Could not analyze GitHub profile');
      } else {
        setResult(data);
        toast.success('GitHub profile analyzed! 🎉');
      }
    } catch (err) {
      toast.error('Failed to analyze GitHub profile. Check the username and try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const radarData = result ? [
    { subject: 'Code Diversity', value: result.breakdown.code_diversity.score },
    { subject: 'Project Quality', value: result.breakdown.project_quality.score },
    { subject: 'Activity', value: result.breakdown.activity.score },
    { subject: 'Documentation', value: result.breakdown.documentation.score },
    { subject: 'Profile', value: result.breakdown.profile_completeness.score },
  ] : [];

  return (
    <div className="page-container">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <h1 className="section-title">GitHub <span className="gradient-text">Profile Analyzer</span></h1>
          <p className="section-subtitle">AI-powered analysis of your GitHub portfolio — projects, activity & improvement suggestions</p>
        </motion.div>

        {/* Search Input */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card-solid p-6 mb-8 max-w-2xl mx-auto">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Github className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={githubInput}
                onChange={(e) => setGithubInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                placeholder="Enter GitHub username or URL..."
                className="input-field pl-11 text-base"
              />
            </div>
            <button onClick={handleAnalyze} disabled={analyzing} className="btn-primary flex items-center gap-2 px-6">
              {analyzing ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
              ) : (
                <><Zap className="w-4 h-4" /> Analyze</>
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Example: <span className="cursor-pointer text-brand-500 hover:text-brand-400" onClick={() => setGithubInput('torvalds')}>torvalds</span>
            {' · '}
            <span className="cursor-pointer text-brand-500 hover:text-brand-400" onClick={() => setGithubInput('https://github.com/sindresorhus')}>https://github.com/sindresorhus</span>
          </p>
        </motion.div>

        {/* Results */}
        <AnimatePresence>
          {result && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">

              {/* ── Profile Header + Overall Score ── */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card-solid p-6">
                <div className="flex flex-col md:flex-row items-center gap-6">
                  {/* Avatar */}
                  <img
                    src={result.profile.avatar_url}
                    alt={result.profile.name}
                    className="w-20 h-20 rounded-2xl border-2 border-brand-500/30 shadow-lg"
                  />

                  {/* Info */}
                  <div className="flex-1 text-center md:text-left">
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                      {result.profile.name || result.username}
                    </h2>
                    <p className="text-gray-500 dark:text-gray-400 text-sm mb-2">@{result.username}</p>
                    {result.profile.bio && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 max-w-md">{result.profile.bio}</p>
                    )}
                    <div className="flex items-center gap-4 mt-3 justify-center md:justify-start">
                      <span className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                        <Code2 className="w-4 h-4" /> {result.profile.public_repos} repos
                      </span>
                      <span className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                        <Users className="w-4 h-4" /> {result.profile.followers} followers
                      </span>
                      <a
                        href={result.profile.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-sm text-brand-500 hover:text-brand-400"
                      >
                        <ExternalLink className="w-3 h-3" /> View Profile
                      </a>
                    </div>
                  </div>

                  {/* Overall Score */}
                  <div className="text-center">
                    <div className={`w-28 h-28 rounded-3xl border-2 ${getScoreBg(result.overall_score)} flex flex-col items-center justify-center`}>
                      <span className={`text-3xl font-black ${getScoreColor(result.overall_score)}`}>
                        {result.overall_score}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">/100</span>
                    </div>
                    <p className="text-sm font-semibold mt-2 text-gray-700 dark:text-gray-300">{result.score_label}</p>
                  </div>
                </div>
              </motion.div>

              {/* ── Score Breakdown Row ── */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {[
                  { label: 'Diversity', score: result.breakdown.code_diversity.score, sublabel: result.breakdown.code_diversity.label, icon: Code2, color: 'text-purple-500' },
                  { label: 'Quality', score: result.breakdown.project_quality.score, sublabel: result.breakdown.project_quality.label, icon: Star, color: 'text-amber-500' },
                  { label: 'Activity', score: result.breakdown.activity.score, sublabel: result.breakdown.activity.label, icon: TrendingUp, color: 'text-emerald-500' },
                  { label: 'Docs', score: result.breakdown.documentation.score, sublabel: result.breakdown.documentation.label, icon: BookOpen, color: 'text-cyan-500' },
                  { label: 'Profile', score: result.breakdown.profile_completeness.score, sublabel: result.breakdown.profile_completeness.label, icon: Globe, color: 'text-brand-500' },
                ].map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <motion.div
                      key={item.label}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.06 }}
                      className="glass-card-solid p-4 text-center"
                    >
                      <Icon className={`w-5 h-5 ${item.color} mx-auto mb-2`} />
                      <p className={`text-2xl font-bold ${getScoreColor(item.score)}`}>{item.score}</p>
                      <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">{item.label}</p>
                      <p className="text-xs text-gray-500">{item.sublabel}</p>
                    </motion.div>
                  );
                })}
              </div>

              {/* ── Charts Row ── */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Language Distribution */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card-solid p-6">
                  <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                    <Code2 className="w-5 h-5 text-purple-500" /> Language Distribution
                  </h3>
                  {result.languages.length > 0 ? (
                    <div className="flex items-center gap-4">
                      <ResponsiveContainer width={160} height={160}>
                        <PieChart>
                          <Pie data={result.languages} dataKey="count" nameKey="language" cx="50%" cy="50%" innerRadius={35} outerRadius={70} strokeWidth={2}>
                            {result.languages.map((entry, i) => (
                              <Cell key={i} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value, name) => [`${value} repos`, name]} />
                        </PieChart>
                      </ResponsiveContainer>
                      <div className="flex-1 space-y-2">
                        {result.languages.slice(0, 6).map((lang, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: lang.color }} />
                            <span className="text-sm text-gray-700 dark:text-gray-300 flex-1">{lang.language}</span>
                            <span className="text-xs font-medium text-gray-500">{lang.percentage}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-gray-400 text-center py-6">No language data available</p>
                  )}
                </motion.div>

                {/* Radar Chart */}
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-card-solid p-6">
                  <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-brand-500" /> Profile Radar
                  </h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="#e2e8f0" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
                      <Radar name="Score" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.2} strokeWidth={2} />
                    </RadarChart>
                  </ResponsiveContainer>
                </motion.div>
              </div>

              {/* ── Top Projects ── */}
              {result.top_projects?.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="glass-card-solid p-6">
                  <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                    <Star className="w-5 h-5 text-amber-500" /> Top Projects
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {result.top_projects.map((proj, i) => (
                      <a
                        key={i}
                        href={proj.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-4 rounded-xl border border-gray-200 dark:border-gray-700/50 hover:border-brand-500/40 hover:bg-brand-500/5 transition-all group"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold text-sm text-gray-800 dark:text-gray-200 group-hover:text-brand-500 transition-colors truncate flex-1">
                            {proj.name}
                          </h4>
                          <ArrowUpRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-3 min-h-[2rem]">
                          {proj.description || 'No description'}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-gray-500">
                          {proj.language && (
                            <span className="flex items-center gap-1">
                              <span className="w-2 h-2 rounded-full bg-brand-500" /> {proj.language}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Star className="w-3 h-3" /> {proj.stars}
                          </span>
                          <span className="flex items-center gap-1">
                            <GitFork className="w-3 h-3" /> {proj.forks}
                          </span>
                          <span className="flex items-center gap-1 ml-auto">
                            <Calendar className="w-3 h-3" /> {proj.updated_at}
                          </span>
                        </div>
                        {proj.topics?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {proj.topics.slice(0, 3).map((t, j) => (
                              <span key={j} className="text-xs px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400">
                                {t}
                              </span>
                            ))}
                          </div>
                        )}
                      </a>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* ── Suggestions ── */}
              {result.suggestions?.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="glass-card-solid p-6">
                  <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-amber-500" /> Improvement Suggestions
                  </h3>
                  <div className="space-y-4">
                    {result.suggestions.map((sug, i) => (
                      <div
                        key={i}
                        className={`p-4 rounded-xl border ${
                          sug.priority === 'high' ? 'border-red-200 dark:border-red-800/40 bg-red-50/50 dark:bg-red-900/10' :
                          sug.priority === 'medium' ? 'border-amber-200 dark:border-amber-800/40 bg-amber-50/50 dark:bg-amber-900/10' :
                          'border-gray-200 dark:border-gray-700/40 bg-gray-50/50 dark:bg-gray-800/30'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-xl flex-shrink-0">{sug.emoji}</span>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold text-sm text-gray-800 dark:text-gray-200">
                                {sug.category}
                              </h4>
                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                sug.priority === 'high' ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400' :
                                sug.priority === 'medium' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400' :
                                'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
                              }`}>
                                {sug.priority}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{sug.suggestion}</p>
                            {sug.action && (
                              <p className="text-sm text-brand-600 dark:text-brand-400 flex items-center gap-1">
                                <CheckCircle className="w-3 h-3 flex-shrink-0" /> {sug.action}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* ── Categories Covered ── */}
              {result.categories_covered?.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }} className="glass-card-solid p-6">
                  <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-emerald-500" /> Categories Covered
                  </h3>
                  <div className="flex flex-wrap gap-3">
                    {result.categories_covered.map((cat, i) => (
                      <div key={i} className="px-4 py-3 rounded-xl bg-brand-500/5 dark:bg-brand-500/10 border border-brand-500/20">
                        <p className="text-sm font-semibold text-brand-600 dark:text-brand-400">{cat.category}</p>
                        <p className="text-xs text-gray-500 mt-1">{cat.repo_count} repos · {cat.languages.join(', ')}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {!result && !analyzing && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-card-solid p-16 text-center max-w-lg mx-auto">
            <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gray-100 dark:bg-surface-800 flex items-center justify-center">
              <Github className="w-10 h-10 text-gray-400 dark:text-gray-500" />
            </div>
            <h2 className="text-2xl font-bold mb-3 text-gray-800 dark:text-gray-200">
              Analyze Your GitHub Profile
            </h2>
            <p className="text-gray-500 dark:text-gray-400 max-w-sm mx-auto mb-6">
              Enter your GitHub username above and we'll analyze your projects,
              code diversity, activity patterns, and provide improvement suggestions.
            </p>
            <div className="flex justify-center gap-3">
              <span className="badge badge-purple">🔍 NLC Analysis</span>
              <span className="badge badge-blue">📊 Quality Scoring</span>
              <span className="badge badge-green">💡 Smart Tips</span>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

export default GitHubAnalyzer;
