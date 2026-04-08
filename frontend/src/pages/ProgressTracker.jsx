import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp, Target, Award, Brain, BarChart3, Calendar
} from 'lucide-react';
import {
  LineChart, Line, AreaChart, Area, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from 'recharts';
import { useDarkMode } from '../App';
import ScoreGauge from '../components/ScoreGauge';

function ProgressTracker({ resumeData, analysisData }) {
  const { darkMode } = useDarkMode();
  const [history, setHistory] = useState([]);

  /* ── Load progress history from localStorage ── */
  useEffect(() => {
    const saved = localStorage.getItem('progressHistory');
    if (saved) {
      setHistory(JSON.parse(saved));
    } else {
      /* Generate demo data */
      const demo = generateDemoHistory();
      setHistory(demo);
      localStorage.setItem('progressHistory', JSON.stringify(demo));
    }
  }, []);

  /* ── Save current analysis to history ── */
  useEffect(() => {
    if (analysisData?.ats_score) {
      const entry = {
        date: new Date().toISOString().split('T')[0],
        ats_score: analysisData.ats_score,
        keyword_match: analysisData.keyword_match_percentage || 0,
        skills_count: analysisData.matching_skills?.length || 0,
        missing_count: analysisData.missing_skills?.length || 0,
      };

      setHistory((prev) => {
        const updated = [...prev.filter((h) => h.date !== entry.date), entry].slice(-20);
        localStorage.setItem('progressHistory', JSON.stringify(updated));
        return updated;
      });
    }
  }, [analysisData]);

  /* ── Compute readiness score ── */
  const atsScore = analysisData?.ats_score || 0;
  const skillMatch = analysisData?.keyword_match_percentage || 0;
  const readinessScore = Math.round(atsScore * 0.4 + skillMatch * 0.35 + (analysisData?.matching_skills?.length || 0) * 3);
  const clampedReadiness = Math.min(100, Math.max(0, readinessScore));

  /* ── Strength/weakness radar ── */
  const radarData = [
    { area: 'Skills', score: Math.min(100, (analysisData?.matching_skills?.length || 3) * 12) },
    { area: 'Experience', score: Math.floor(Math.random() * 20) + 60 },
    { area: 'Education', score: Math.floor(Math.random() * 15) + 70 },
    { area: 'Projects', score: Math.floor(Math.random() * 25) + 55 },
    { area: 'Keywords', score: Math.round(skillMatch) },
    { area: 'Format', score: Math.floor(Math.random() * 10) + 75 },
  ];

  const axisColor = darkMode ? '#64748b' : '#94a3b8';

  return (
    <div className="page-container">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <h1 className="section-title">Progress <span className="gradient-text">Tracker</span></h1>
          <p className="section-subtitle">Track your improvement over time and measure interview readiness</p>
        </motion.div>

        {/* ── Top Cards ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* ATS Score */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card-solid p-6 flex flex-col items-center">
            <ScoreGauge score={atsScore} size={130} label="ATS Score" />
          </motion.div>

          {/* Readiness Score */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card-solid p-6 flex flex-col items-center">
            <ScoreGauge score={clampedReadiness} size={130} label="Readiness" color="#8b5cf6" />
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">ATS + Skills + Keywords</p>
          </motion.div>

          {/* Quick Stats */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card-solid p-6 space-y-4">
            <h3 className="font-bold text-gray-800 dark:text-gray-200 flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-500" /> Quick Stats
            </h3>
            {[
              { label: 'Analyses Run', value: history.length, icon: BarChart3 },
              { label: 'Best ATS Score', value: Math.max(0, ...history.map((h) => h.ats_score)), icon: Target },
              { label: 'Skills Matched', value: analysisData?.matching_skills?.length || 0, icon: Brain },
            ].map((stat, i) => {
              const Icon = stat.icon;
              return (
                <div key={i} className="flex items-center justify-between">
                  <span className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <Icon className="w-4 h-4 text-brand-500" /> {stat.label}
                  </span>
                  <span className="font-bold text-gray-800 dark:text-gray-200">{stat.value}</span>
                </div>
              );
            })}
          </motion.div>
        </div>

        {/* ── Score Trend Chart ── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card-solid p-6 mb-8">
          <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-brand-500" /> Score Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={history}>
              <defs>
                <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="kwGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? '#1e293b' : '#f1f5f9'} />
              <XAxis dataKey="date" tick={{ fill: axisColor, fontSize: 11 }} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: axisColor, fontSize: 11 }} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: darkMode ? '#1e293b' : '#fff',
                  border: darkMode ? '1px solid #334155' : '1px solid #e2e8f0',
                  borderRadius: '12px',
                  fontSize: '13px',
                }}
              />
              <Area type="monotone" dataKey="ats_score" stroke="#6366f1" fill="url(#scoreGradient)" strokeWidth={2} name="ATS Score" />
              <Area type="monotone" dataKey="keyword_match" stroke="#10b981" fill="url(#kwGradient)" strokeWidth={2} name="Keyword %" />
            </AreaChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-6 mt-2 text-sm">
            <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-brand-500" /> ATS Score</span>
            <span className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-emerald-500" /> Keyword Match</span>
          </div>
        </motion.div>

        {/* ── Strength/Weakness Radar ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="glass-card-solid p-6">
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4">Strength Analysis</h3>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={radarData}>
                <PolarGrid stroke={darkMode ? '#334155' : '#e2e8f0'} />
                <PolarAngleAxis dataKey="area" tick={{ fill: axisColor, fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.25} strokeWidth={2} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Session History */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="glass-card-solid p-6">
            <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-brand-500" /> Recent Sessions
            </h3>
            <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
              {history.slice(-10).reverse().map((entry, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-surface-800 hover:bg-gray-100 dark:hover:bg-surface-700 transition-colors">
                  <div>
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{entry.date}</p>
                    <p className="text-xs text-gray-500">{entry.skills_count} skills matched</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-lg font-bold ${
                      entry.ats_score >= 75 ? 'text-emerald-500' :
                      entry.ats_score >= 50 ? 'text-amber-500' : 'text-red-500'
                    }`}>
                      {entry.ats_score}
                    </p>
                    <p className="text-xs text-gray-500">ATS</p>
                  </div>
                </div>
              ))}
              {history.length === 0 && (
                <p className="text-sm text-gray-400 text-center py-8">No sessions yet</p>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

/* ── Generate demo history for first load ── */
function generateDemoHistory() {
  const entries = [];
  const today = new Date();
  for (let i = 9; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i * 3);
    entries.push({
      date: date.toISOString().split('T')[0],
      ats_score: Math.floor(Math.random() * 30) + 50 + i * 2,
      keyword_match: Math.floor(Math.random() * 25) + 40 + i * 3,
      skills_count: Math.floor(Math.random() * 5) + 3,
      missing_count: Math.max(0, 8 - i),
    });
  }
  return entries;
}

export default ProgressTracker;
