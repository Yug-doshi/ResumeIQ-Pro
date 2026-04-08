import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Map, Loader2, BookOpen, CheckCircle, Clock, ExternalLink, Zap,
  Brain, Sparkles, ArrowRight, Target, TrendingUp, AlertTriangle
} from 'lucide-react';
import toast from 'react-hot-toast';
import { getSkillRoadmap, getDynamicRoadmap } from '../api/apiClient';

function SkillRoadmap({ analysisData, resumeData, loading, setLoading }) {
  const [roadmap, setRoadmap] = useState(null);
  const [weeks, setWeeks] = useState(8);
  const [generating, setGenerating] = useState(false);
  const [completedTasks, setCompletedTasks] = useState({});
  const [isDynamicMode, setIsDynamicMode] = useState(true);
  const [dynamicData, setDynamicData] = useState(null);

  const missingSkills = analysisData?.missing_skills || [];
  const jobRole = analysisData?.job_role || 'Software Engineer';

  /* ── Generate roadmap ── */
  const handleGenerate = async () => {
    if (missingSkills.length === 0) {
      toast.error('No missing skills to create a roadmap for!');
      return;
    }
    setGenerating(true);
    setLoading(true);
    try {
      if (isDynamicMode && resumeData?.resume_id) {
        // Dynamic AI mode
        const data = await getDynamicRoadmap(
          resumeData.resume_id, jobRole, missingSkills, '', weeks
        );
        setDynamicData(data);
        setRoadmap(data.roadmap || []);
        toast.success('Dynamic AI Roadmap generated! 🚀');
      } else {
        // Static mode
        const data = await getSkillRoadmap(jobRole, missingSkills, weeks);
        setDynamicData(null);
        setRoadmap(data.roadmap || data);
        toast.success('Roadmap generated!');
      }
    } catch (err) {
      toast.error('Failed to generate roadmap');
    } finally {
      setGenerating(false);
      setLoading(false);
    }
  };

  /* ── Toggle task completion ── */
  const toggleTask = (weekIdx, taskIdx) => {
    const key = `${weekIdx}-${taskIdx}`;
    setCompletedTasks((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  /* ── Calculate progress ── */
  const totalTasks = roadmap ? roadmap.reduce((sum, w) => sum + (w.tasks?.length || 0), 0) : 0;
  const doneTasks = Object.values(completedTasks).filter(Boolean).length;
  const progressPercent = totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0;

  return (
    <div className="page-container">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <h1 className="section-title">
            {isDynamicMode ? 'Dynamic AI ' : 'Skill Gap '}
            <span className="gradient-text">Roadmap</span>
          </h1>
          <p className="section-subtitle">
            {isDynamicMode
              ? 'AI-adaptive learning path based on your resume gaps, target job & skill level'
              : 'Personalized week-by-week learning plan for missing skills'
            }
          </p>
        </motion.div>

        {/* Missing skills preview + Controls */}
        {missingSkills.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card-solid p-5 mb-6">
            {/* Dynamic mode toggle */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-bold text-gray-800 dark:text-gray-200">Skills to Learn</h3>
              <button
                onClick={() => setIsDynamicMode(!isDynamicMode)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  isDynamicMode
                    ? 'bg-gradient-to-r from-brand-500 to-purple-500 text-white shadow-lg shadow-brand-500/20'
                    : 'bg-gray-100 dark:bg-surface-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-surface-700'
                }`}
              >
                {isDynamicMode ? <Brain className="w-4 h-4" /> : <Map className="w-4 h-4" />}
                {isDynamicMode ? 'Dynamic AI Mode' : 'Static Mode'}
              </button>
            </div>

            {isDynamicMode && (
              <div className="p-3 mb-4 rounded-xl bg-gradient-to-r from-brand-500/5 to-purple-500/5 dark:from-brand-500/10 dark:to-purple-500/10 border border-brand-500/20">
                <p className="text-xs text-brand-600 dark:text-brand-400 flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span><strong>AI Mode:</strong> Analyzes your resume to detect experience level, skill proficiency, and creates an adaptive learning path with priority-based ordering.</span>
                </p>
              </div>
            )}

            <div className="flex flex-wrap gap-2 mb-4">
              {missingSkills.map((skill, i) => (
                <span key={i} className="badge badge-red">{skill}</span>
              ))}
            </div>
            <div className="flex items-center gap-4">
              <div>
                <label className="text-xs font-medium text-gray-600 dark:text-gray-400 block mb-1">Duration</label>
                <select value={weeks} onChange={(e) => setWeeks(Number(e.target.value))} className="input-field text-sm py-2">
                  {[4, 6, 8, 10, 12].map((w) => <option key={w} value={w}>{w} weeks</option>)}
                </select>
              </div>
              <button onClick={handleGenerate} disabled={generating} className="btn-primary mt-4 flex items-center gap-2">
                {generating ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : <><Zap className="w-4 h-4" /> {isDynamicMode ? 'Generate AI Roadmap' : 'Generate Roadmap'}</>}
              </button>
            </div>
          </motion.div>
        )}

        {/* No missing skills */}
        {missingSkills.length === 0 && (
          <div className="glass-card-solid p-10 text-center">
            <Map className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-2">No Skills Gap Detected</h2>
            <p className="text-gray-500">Run a resume analysis first to identify missing skills.</p>
          </div>
        )}

        {/* ── Dynamic AI Insights ── */}
        <AnimatePresence>
          {dynamicData && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4 mb-6">
              {/* Experience Level + Milestones */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Experience Level */}
                <div className="glass-card-solid p-4 text-center">
                  <div className={`w-12 h-12 mx-auto mb-2 rounded-xl flex items-center justify-center ${
                    dynamicData.experience_level === 'senior' ? 'bg-purple-500/10' :
                    dynamicData.experience_level === 'mid' ? 'bg-brand-500/10' : 'bg-emerald-500/10'
                  }`}>
                    <Target className={`w-6 h-6 ${
                      dynamicData.experience_level === 'senior' ? 'text-purple-500' :
                      dynamicData.experience_level === 'mid' ? 'text-brand-500' : 'text-emerald-500'
                    }`} />
                  </div>
                  <p className="text-sm font-bold text-gray-800 dark:text-gray-200 capitalize">
                    {dynamicData.experience_level} Level
                  </p>
                  <p className="text-xs text-gray-500">Detected from resume</p>
                </div>

                {/* Skills to Learn */}
                <div className="glass-card-solid p-4 text-center">
                  <div className="w-12 h-12 mx-auto mb-2 rounded-xl bg-amber-500/10 flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-amber-500" />
                  </div>
                  <p className="text-sm font-bold text-gray-800 dark:text-gray-200">
                    {dynamicData.skill_priorities?.length || 0} Skills
                  </p>
                  <p className="text-xs text-gray-500">Prioritized for you</p>
                </div>

                {/* Milestones */}
                <div className="glass-card-solid p-4 text-center">
                  <div className="w-12 h-12 mx-auto mb-2 rounded-xl bg-cyan-500/10 flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-cyan-500" />
                  </div>
                  <p className="text-sm font-bold text-gray-800 dark:text-gray-200">
                    {dynamicData.milestones?.length || 0} Milestones
                  </p>
                  <p className="text-xs text-gray-500">Progress checkpoints</p>
                </div>
              </div>

              {/* Skill Priorities */}
              {dynamicData.skill_priorities?.length > 0 && (
                <div className="glass-card-solid p-4">
                  <h4 className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                    <Target className="w-4 h-4 text-brand-500" /> Skill Priority Order
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {dynamicData.skill_priorities.map((sp, i) => (
                      <div key={i} className="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-800">
                        <span className="text-xs font-bold text-gray-400 w-5 text-right">#{i + 1}</span>
                        <span className="text-sm">{sp.priority}</span>
                        <span className="text-sm font-medium text-gray-800 dark:text-gray-200 flex-1">{sp.skill}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          sp.current_level === 'none' ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400' :
                          sp.current_level === 'beginner' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400' :
                          sp.current_level === 'intermediate' ? 'bg-brand-100 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400' :
                          'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
                        }`}>
                          {sp.current_level}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Adaptive Insights */}
              {dynamicData.adaptive_insights?.length > 0 && (
                <div className="glass-card-solid p-4">
                  <h4 className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                    <Brain className="w-4 h-4 text-purple-500" /> AI Insights
                  </h4>
                  <div className="space-y-2">
                    {dynamicData.adaptive_insights.map((insight, i) => (
                      <p key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                        <ArrowRight className="w-3.5 h-3.5 mt-0.5 text-brand-500 flex-shrink-0" />
                        {insight}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Progress bar */}
        {roadmap && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card-solid p-4 mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className={`w-5 h-5 ${progressPercent === 100 ? 'text-emerald-500' : 'text-brand-500'}`} />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{doneTasks}/{totalTasks} tasks completed</span>
            </div>
            <div className="flex items-center gap-3 flex-1 max-w-xs ml-4">
              <div className="flex-1 h-2 bg-gray-200 dark:bg-surface-800 rounded-full overflow-hidden">
                <motion.div className="h-full rounded-full gradient-bg" animate={{ width: `${progressPercent}%` }} />
              </div>
              <span className="text-sm font-bold text-brand-600 dark:text-brand-400">{progressPercent}%</span>
            </div>
          </motion.div>
        )}

        {/* ── Milestones bar ── */}
        {dynamicData?.milestones?.length > 0 && roadmap && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card-solid p-4 mb-6">
            <h4 className="text-xs font-bold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">Milestones</h4>
            <div className="flex items-center gap-2">
              {dynamicData.milestones.map((ms, i) => {
                const reached = progressPercent >= ((ms.week / weeks) * 100);
                return (
                  <React.Fragment key={i}>
                    <div className={`flex flex-col items-center flex-1 ${reached ? 'opacity-100' : 'opacity-50'}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                        reached ? 'gradient-bg text-white' : 'bg-gray-200 dark:bg-surface-800 text-gray-500'
                      }`}>
                        W{ms.week}
                      </div>
                      <p className="text-xs text-center mt-1 text-gray-600 dark:text-gray-400 font-medium leading-tight">{ms.label}</p>
                    </div>
                    {i < dynamicData.milestones.length - 1 && (
                      <div className={`h-0.5 flex-1 ${reached ? 'bg-brand-500' : 'bg-gray-200 dark:bg-surface-800'}`} />
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Timeline */}
        {roadmap && (
          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-brand-500 to-purple-500 hidden md:block" />

            <div className="space-y-6">
              {roadmap.map((week, wIdx) => (
                <motion.div
                  key={wIdx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: wIdx * 0.06 }}
                  className="relative md:pl-16"
                >
                  {/* Week badge */}
                  <div className={`hidden md:flex absolute left-0 top-4 w-12 h-12 rounded-xl items-center justify-center text-white font-bold text-sm shadow-lg z-10 ${
                    week.difficulty === 'advanced' ? 'bg-gradient-to-br from-purple-500 to-pink-500 shadow-purple-500/20' :
                    week.difficulty === 'intermediate' ? 'bg-gradient-to-br from-brand-500 to-cyan-500 shadow-brand-500/20' :
                    'gradient-bg shadow-brand-500/20'
                  }`}>
                    W{wIdx + 1}
                  </div>

                  <div className="glass-card-solid p-6">
                    <div className="flex items-center gap-3 mb-4 flex-wrap">
                      <span className="md:hidden badge badge-purple">Week {wIdx + 1}</span>
                      <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200">
                        {week.title || `Week ${wIdx + 1}`}
                      </h3>
                      <div className="ml-auto flex items-center gap-2">
                        {/* Priority badge (dynamic mode) */}
                        {week.priority && (
                          <span className={`text-xs px-2 py-1 rounded-lg font-medium ${
                            week.priority.includes('Critical') ? 'bg-red-100 dark:bg-red-900/20 text-red-600 dark:text-red-400' :
                            week.priority.includes('Important') ? 'bg-amber-100 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400' :
                            'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400'
                          }`}>
                            {week.priority}
                          </span>
                        )}
                        {/* Difficulty badge */}
                        {week.difficulty && (
                          <span className={`text-xs px-2 py-1 rounded-lg font-medium ${
                            week.difficulty === 'advanced' ? 'bg-purple-100 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400' :
                            week.difficulty === 'intermediate' ? 'bg-brand-100 dark:bg-brand-900/20 text-brand-600 dark:text-brand-400' :
                            'bg-cyan-100 dark:bg-cyan-900/20 text-cyan-600 dark:text-cyan-400'
                          }`}>
                            {week.difficulty}
                          </span>
                        )}
                        <span className="flex items-center gap-1 text-xs text-gray-500">
                          <Clock className="w-3 h-3" /> {week.hours || '8-10'} hrs
                        </span>
                      </div>
                    </div>

                    {week.focus && (
                      <p className="text-sm text-brand-600 dark:text-brand-400 mb-3 font-medium">{week.focus}</p>
                    )}

                    {/* Adaptive note (dynamic mode) */}
                    {week.adaptive_note && (
                      <p className="text-xs text-purple-600 dark:text-purple-400 mb-3 flex items-center gap-1 italic">
                        <Brain className="w-3 h-3" /> {week.adaptive_note}
                      </p>
                    )}

                    {/* Tasks */}
                    <div className="space-y-2">
                      {(week.tasks || []).map((task, tIdx) => {
                        const key = `${wIdx}-${tIdx}`;
                        const done = completedTasks[key];
                        return (
                          <label key={tIdx} className={`flex items-start gap-3 p-3 rounded-xl cursor-pointer transition-all ${done ? 'bg-emerald-50 dark:bg-emerald-900/10' : 'hover:bg-gray-50 dark:hover:bg-surface-800'}`}>
                            <input
                              type="checkbox"
                              checked={!!done}
                              onChange={() => toggleTask(wIdx, tIdx)}
                              className="mt-0.5 w-4 h-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500"
                            />
                            <span className={`text-sm flex-1 ${done ? 'line-through text-gray-400' : 'text-gray-700 dark:text-gray-300'}`}>
                              {typeof task === 'string' ? task : task.name || task.description}
                            </span>
                          </label>
                        );
                      })}
                    </div>

                    {/* Resources */}
                    {week.resources && week.resources.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700/50">
                        <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2 flex items-center gap-1">
                          <BookOpen className="w-3 h-3" /> Resources
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {week.resources.map((r, i) => (
                            <span key={i} className="text-xs px-2 py-1 rounded-md bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 flex items-center gap-1">
                              <ExternalLink className="w-3 h-3" />
                              {typeof r === 'string' ? r : r.name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default SkillRoadmap;
