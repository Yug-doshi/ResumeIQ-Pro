import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FolderGit2, Loader2, ExternalLink, Star, Clock, Code,
  ArrowRight, Zap, Layers
} from 'lucide-react';
import toast from 'react-hot-toast';
import { suggestProjects } from '../api/apiClient';

function ProjectSuggestions({ analysisData, loading, setLoading }) {
  const [projects, setProjects] = useState(null);
  const [generating, setGenerating] = useState(false);

  const missingSkills = analysisData?.missing_skills || [];
  const jobRole = analysisData?.job_role || 'Software Engineer';

  /* ── Fetch project suggestions ── */
  const handleGenerate = async () => {
    setGenerating(true);
    setLoading(true);
    try {
      const data = await suggestProjects(jobRole, missingSkills, 6);
      setProjects(data.suggested_projects || data.projects || []);
      toast.success('Projects suggested!');
    } catch (err) {
      toast.error('Failed to suggest projects');
    } finally {
      setGenerating(false);
      setLoading(false);
    }
  };

  /* ── Difficulty color ── */
  const diffColor = (d) => {
    const level = (d || 'medium').toLowerCase();
    if (level === 'easy' || level === 'beginner') return 'badge-green';
    if (level === 'hard' || level === 'advanced') return 'badge-red';
    return 'badge-amber';
  };

  return (
    <div className="page-container">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <h1 className="section-title">Smart <span className="gradient-text">Project Ideas</span></h1>
          <p className="section-subtitle">Portfolio projects mapped to your skill gaps</p>
        </motion.div>

        {/* Skill gap → project mapping */}
        {missingSkills.length > 0 && !projects && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card-solid p-6 mb-8">
            <h3 className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-3">Missing Skills → Project Ideas</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              {missingSkills.map((skill, i) => (
                <span key={i} className="flex items-center gap-1 badge badge-red">
                  {skill} <ArrowRight className="w-3 h-3" /> 🔬
                </span>
              ))}
            </div>
            <button onClick={handleGenerate} disabled={generating} className="btn-primary flex items-center gap-2">
              {generating ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : <><Zap className="w-4 h-4" /> Suggest Projects</>}
            </button>
          </motion.div>
        )}

        {/* No skills */}
        {missingSkills.length === 0 && !projects && (
          <div className="glass-card-solid p-10 text-center">
            <FolderGit2 className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-2">Run Analysis First</h2>
            <p className="text-gray-500 dark:text-gray-400">Analyze your resume to get targeted project suggestions</p>
          </div>
        )}

        {/* Project cards */}
        {projects && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {projects.map((project, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="glass-card-solid p-6 card-hover group"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg">
                      <Code className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800 dark:text-gray-200">
                        {project.name || project.title}
                      </h3>
                      <span className={`badge ${diffColor(project.difficulty)} mt-1`}>
                        {project.difficulty || 'Medium'}
                      </span>
                    </div>
                  </div>
                  {project.estimated_time && (
                    <span className="flex items-center gap-1 text-xs text-gray-500">
                      <Clock className="w-3 h-3" /> {project.estimated_time}
                    </span>
                  )}
                </div>

                {/* Description */}
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
                  {project.description}
                </p>

                {/* Tech stack */}
                {project.tech_stack && (
                  <div className="mb-4">
                    <p className="text-xs font-semibold text-gray-500 mb-2 flex items-center gap-1">
                      <Layers className="w-3 h-3" /> Tech Stack
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {(Array.isArray(project.tech_stack) ? project.tech_stack : [project.tech_stack]).map((tech, j) => (
                        <span key={j} className="px-2 py-1 text-xs font-medium rounded-md bg-gray-100 dark:bg-surface-800 text-gray-700 dark:text-gray-300">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Skills addressed */}
                {project.skills_addressed && (
                  <div>
                    <p className="text-xs font-semibold text-gray-500 mb-2">Skills Covered</p>
                    <div className="flex flex-wrap gap-1.5">
                      {(Array.isArray(project.skills_addressed) ? project.skills_addressed : [project.skills_addressed]).map((s, j) => (
                        <span key={j} className="badge badge-green">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ProjectSuggestions;
