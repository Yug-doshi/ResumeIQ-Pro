import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Map, Loader2, BookOpen, CheckCircle, Clock, ExternalLink, Zap } from 'lucide-react';
import toast from 'react-hot-toast';
import { getSkillRoadmap } from '../api/apiClient';

function SkillRoadmap({ analysisData, loading, setLoading }) {
  const [roadmap, setRoadmap] = useState(null);
  const [weeks, setWeeks] = useState(8);
  const [generating, setGenerating] = useState(false);
  const [completedTasks, setCompletedTasks] = useState({});

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
      const data = await getSkillRoadmap(jobRole, missingSkills, weeks);
      setRoadmap(data.roadmap || data);
      toast.success('Roadmap generated!');
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
          <h1 className="section-title">Skill Gap <span className="gradient-text">Roadmap</span></h1>
          <p className="section-subtitle">Personalized week-by-week learning plan for missing skills</p>
        </motion.div>

        {/* Missing skills preview */}
        {missingSkills.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card-solid p-5 mb-6">
            <h3 className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-3">Skills to Learn</h3>
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
                {generating ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : <><Zap className="w-4 h-4" /> Generate Roadmap</>}
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
                  transition={{ delay: wIdx * 0.08 }}
                  className="relative md:pl-16"
                >
                  {/* Week badge */}
                  <div className="hidden md:flex absolute left-0 top-4 w-12 h-12 rounded-xl gradient-bg items-center justify-center text-white font-bold text-sm shadow-lg shadow-brand-500/20 z-10">
                    W{wIdx + 1}
                  </div>

                  <div className="glass-card-solid p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <span className="md:hidden badge badge-purple">Week {wIdx + 1}</span>
                      <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200">
                        {week.title || `Week ${wIdx + 1}`}
                      </h3>
                      <span className="ml-auto flex items-center gap-1 text-xs text-gray-500">
                        <Clock className="w-3 h-3" /> {week.hours || '8-10'} hrs
                      </span>
                    </div>

                    {week.focus && (
                      <p className="text-sm text-brand-600 dark:text-brand-400 mb-3 font-medium">{week.focus}</p>
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
