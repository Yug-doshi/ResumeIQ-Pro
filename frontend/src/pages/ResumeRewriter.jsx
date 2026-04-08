import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileEdit, Loader2, ArrowRight, Sparkles, Zap, Copy, Check } from 'lucide-react';
import toast from 'react-hot-toast';
import { rewriteResume } from '../api/apiClient';

const JOB_ROLES = [
  'Software Engineer', 'Data Scientist', 'AI Engineer', 'Web Developer',
  'DevOps Engineer', 'Product Manager',
];

function ResumeRewriter({ resumeData, loading, setLoading }) {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState('');
  const [jobRole, setJobRole] = useState('Software Engineer');
  const [result, setResult] = useState(null);
  const [rewriting, setRewriting] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState(null);

  /* ── Rewrite handler ── */
  const handleRewrite = async () => {
    if (!inputText.trim()) { toast.error('Paste your resume bullet points first'); return; }
    setRewriting(true);
    setLoading(true);
    try {
      const data = await rewriteResume(inputText, jobRole);
      setResult(data);
      toast.success('Resume rewritten! ✨');
    } catch (err) {
      toast.error('Rewrite failed');
    } finally {
      setRewriting(false);
      setLoading(false);
    }
  };

  /* ── Copy to clipboard ── */
  const copyBullet = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
    toast.success('Copied!');
  };

  return (
    <div className="page-container">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-10">
          <h1 className="section-title">AI Resume <span className="gradient-text">Rewriter</span></h1>
          <p className="section-subtitle">Transform weak bullet points into impactful achievement statements</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ── Input Side ── */}
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
            <div className="glass-card-solid p-6 h-full flex flex-col">
              <div className="flex items-center gap-2 mb-4">
                <FileEdit className="w-5 h-5 text-gray-500" />
                <h3 className="font-bold text-gray-800 dark:text-gray-200">Original Text</h3>
              </div>

              <div className="mb-4">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1">Target Role</label>
                <select value={jobRole} onChange={(e) => setJobRole(e.target.value)} className="input-field text-sm">
                  {JOB_ROLES.map((r) => <option key={r}>{r}</option>)}
                </select>
              </div>

              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={`Paste your resume bullet points here...\n\nExample:\n- Worked on backend tasks\n- Made a website\n- Did data analysis`}
                rows={12}
                className="input-field flex-1 resize-none text-sm"
              />

              <button
                onClick={handleRewrite}
                disabled={rewriting || !inputText.trim()}
                className="btn-primary mt-4 flex items-center justify-center gap-2"
              >
                {rewriting ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Rewriting...</>
                ) : (
                  <><Sparkles className="w-4 h-4" /> Rewrite with AI</>
                )}
              </button>
            </div>
          </motion.div>

          {/* ── Output Side ── */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
            <div className="glass-card-solid p-6 h-full">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-brand-500" />
                <h3 className="font-bold text-gray-800 dark:text-gray-200">Enhanced Version</h3>
              </div>

              {result ? (
                <div className="space-y-4">
                  {/* Rewritten bullets */}
                  <div className="space-y-3">
                    {(result.rewritten || result.rewritten_bullets || []).map((bullet, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="flex items-start gap-3 p-4 rounded-xl bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-800/30 group"
                      >
                        <Zap className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-emerald-700 dark:text-emerald-300 leading-relaxed flex-1">
                          {bullet}
                        </p>
                        <button
                          onClick={() => copyBullet(bullet, i)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/30"
                        >
                          {copiedIdx === i ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4 text-emerald-500" />}
                        </button>
                      </motion.div>
                    ))}
                  </div>

                  {/* Tips */}
                  {result.improvement_tips && (
                    <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800/30">
                      <h4 className="text-sm font-bold text-amber-700 dark:text-amber-400 mb-2">💡 Writing Tips</h4>
                      <ul className="space-y-1">
                        {result.improvement_tips.map((tip, i) => (
                          <li key={i} className="text-sm text-amber-600 dark:text-amber-300">{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-center">
                  <FileEdit className="w-12 h-12 text-gray-200 dark:text-gray-700 mb-4" />
                  <p className="text-gray-400 dark:text-gray-500">
                    Your enhanced bullet points will appear here
                  </p>
                  <p className="text-xs text-gray-400 mt-2">
                    Paste text on the left and click "Rewrite with AI"
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

export default ResumeRewriter;
