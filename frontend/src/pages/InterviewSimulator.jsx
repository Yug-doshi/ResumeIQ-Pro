import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic, Brain, ChevronLeft, ChevronRight, Loader2, Send,
  CheckCircle, Star, MessageSquare, Award, Zap, Smile, Frown, Meh, HelpCircle, AlertTriangle, TrendingUp
} from 'lucide-react';
import toast from 'react-hot-toast';
import VoiceRecorder from '../components/VoiceRecorder';
import ScoreGauge from '../components/ScoreGauge';
import { generateInterviewQuestions, evaluateAnswer, analyzeEmotion } from '../api/apiClient';

const EMOTION_ICONS = {
  confident: { icon: Smile, color: 'text-emerald-500', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  nervous: { icon: Frown, color: 'text-red-500', bg: 'bg-red-500/10 border-red-500/20' },
  hesitant: { icon: HelpCircle, color: 'text-amber-500', bg: 'bg-amber-500/10 border-amber-500/20' },
  neutral: { icon: Meh, color: 'text-gray-500', bg: 'bg-gray-500/10 border-gray-500/20' },
};

const CATEGORIES = ['All', 'HR', 'Technical', 'Behavioral'];
const DIFFICULTIES = ['All', 'easy', 'medium', 'hard'];
const JOB_ROLES = [
  'Software Engineer', 'Data Scientist', 'AI Engineer', 'Web Developer',
  'DevOps Engineer', 'Product Manager',
];

function InterviewSimulator({ resumeData, analysisData, loading, setLoading }) {
  const navigate = useNavigate();

  /* ── State ── */
  const [jobRole, setJobRole] = useState('Software Engineer');
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [started, setStarted] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [answers, setAnswers] = useState({});
  const [evaluations, setEvaluations] = useState({});
  const [evaluating, setEvaluating] = useState(false);
  const [filterCategory, setFilterCategory] = useState('All');
  const [filterDifficulty, setFilterDifficulty] = useState('All');
  const [emotions, setEmotions] = useState({});
  const [analyzingEmotion, setAnalyzingEmotion] = useState(false);

  /* ── No resume guard ── */
  if (!resumeData) {
    return (
      <div className="page-container flex items-center justify-center min-h-[60vh]">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card-solid p-10 text-center max-w-md">
          <Brain className="w-12 h-12 text-brand-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2 text-gray-800 dark:text-gray-200">Upload Resume First</h2>
          <p className="text-gray-500 mb-6">We need your resume to generate personalized questions</p>
          <button onClick={() => navigate('/upload')} className="btn-primary">Upload Resume</button>
        </motion.div>
      </div>
    );
  }

  /* ── Generate questions ── */
  const handleStart = async () => {
    setGenerating(true);
    setLoading(true);
    try {
      const data = await generateInterviewQuestions(resumeData.resume_id, jobRole, 12);
      setQuestions(data.questions || []);
      setStarted(true);
      setCurrentIndex(0);
      setAnswers({});
      setEvaluations({});
      toast.success(`${data.questions?.length || 0} questions generated!`);
    } catch (err) {
      toast.error('Failed to generate questions');
    } finally {
      setGenerating(false);
      setLoading(false);
    }
  };

  /* ── Evaluate answer ── */
  const handleEvaluate = async () => {
    const q = filteredQuestions[currentIndex];
    const answer = answers[q.question_id] || '';
    if (!answer.trim()) { toast.error('Write or speak your answer first'); return; }

    setEvaluating(true);
    setAnalyzingEmotion(true);
    try {
      // Run evaluation and emotion analysis in parallel
      const [result, emotionResult] = await Promise.all([
        evaluateAnswer(q.question, answer, q.ideal_answer, q.category),
        analyzeEmotion(answer).catch(() => null),
      ]);
      setEvaluations((prev) => ({ ...prev, [q.question_id]: result }));
      if (emotionResult) {
        setEmotions((prev) => ({ ...prev, [q.question_id]: emotionResult }));
      }
      toast.success(`Score: ${result.score}/10`);
    } catch (err) {
      toast.error('Evaluation failed');
    } finally {
      setEvaluating(false);
      setAnalyzingEmotion(false);
    }
  };

  /* ── Voice callback ── */
  const handleVoiceTranscript = (text) => {
    const q = filteredQuestions[currentIndex];
    setAnswers((prev) => ({ ...prev, [q.question_id]: text }));
    toast.success('Voice transcribed!');
  };

  /* ── Filtering ── */
  const filteredQuestions = questions.filter((q) => {
    if (filterCategory !== 'All' && q.category !== filterCategory) return false;
    if (filterDifficulty !== 'All' && q.difficulty !== filterDifficulty) return false;
    return true;
  });

  const currentQuestion = filteredQuestions[currentIndex];
  const currentEval = currentQuestion ? evaluations[currentQuestion.question_id] : null;
  const currentEmotion = currentQuestion ? emotions[currentQuestion.question_id] : null;

  /* ── Session score ── */
  const completedCount = Object.keys(evaluations).length;
  const avgScore = completedCount > 0
    ? (Object.values(evaluations).reduce((sum, e) => sum + (e.score || 0), 0) / completedCount).toFixed(1)
    : 0;

  /* ═══════ NOT STARTED ═══════ */
  if (!started) {
    return (
      <div className="page-container">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-xl mx-auto text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-3xl gradient-bg flex items-center justify-center shadow-xl shadow-brand-500/20">
            <Mic className="w-10 h-10 text-white" />
          </div>
          <h1 className="section-title mb-2">AI Interview <span className="gradient-text">Simulator</span></h1>
          <p className="section-subtitle">Practice with AI-generated questions personalized to your resume</p>

          <div className="glass-card-solid p-6 mb-6 text-left space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1">Target Role</label>
              <select value={jobRole} onChange={(e) => setJobRole(e.target.value)} className="input-field">
                {JOB_ROLES.map((r) => <option key={r}>{r}</option>)}
              </select>
            </div>

            <div className="grid grid-cols-3 gap-3 text-center">
              {['HR', 'Technical', 'Behavioral'].map((cat) => (
                <div key={cat} className="p-3 rounded-xl bg-gray-50 dark:bg-surface-800">
                  <p className="text-lg font-bold text-gray-800 dark:text-gray-200">4</p>
                  <p className="text-xs text-gray-500">{cat}</p>
                </div>
              ))}
            </div>
          </div>

          <button onClick={handleStart} disabled={generating} className="btn-primary text-lg px-8 py-4 flex items-center gap-2 mx-auto">
            {generating ? <><Loader2 className="w-5 h-5 animate-spin" /> Generating...</> : <><Zap className="w-5 h-5" /> Start Interview</>}
          </button>
        </motion.div>
      </div>
    );
  }

  /* ═══════ INTERVIEW IN PROGRESS ═══════ */
  return (
    <div className="page-container">
      <div className="max-w-4xl mx-auto">
        {/* ── Header + progress ── */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">Interview Session</h1>
            <p className="text-sm text-gray-500 mt-1">
              Question {currentIndex + 1} of {filteredQuestions.length} • Avg Score: {avgScore}/10
            </p>
          </div>
          {/* Filter pills */}
          <div className="flex gap-2 flex-wrap">
            {CATEGORIES.map((c) => (
              <button
                key={c}
                onClick={() => { setFilterCategory(c); setCurrentIndex(0); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  filterCategory === c ? 'gradient-bg text-white' : 'bg-gray-100 dark:bg-surface-800 text-gray-600 dark:text-gray-400'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full h-2 rounded-full bg-gray-200 dark:bg-surface-800 mb-6 overflow-hidden">
          <motion.div
            className="h-full rounded-full gradient-bg"
            animate={{ width: `${((currentIndex + 1) / filteredQuestions.length) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>

        {currentQuestion ? (
          <div className="space-y-6">
            {/* ── Question Card ── */}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentQuestion.question_id}
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -30 }}
                className="glass-card-solid p-6"
              >
                <div className="flex items-center gap-2 mb-4">
                  <span className={`badge ${
                    currentQuestion.category === 'HR' ? 'badge-blue' :
                    currentQuestion.category === 'Technical' ? 'badge-purple' : 'badge-amber'
                  }`}>
                    {currentQuestion.category}
                  </span>
                  <span className={`badge ${
                    currentQuestion.difficulty === 'easy' ? 'badge-green' :
                    currentQuestion.difficulty === 'hard' ? 'badge-red' : 'badge-amber'
                  }`}>
                    {currentQuestion.difficulty}
                  </span>
                </div>
                <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200 leading-relaxed">
                  {currentQuestion.question}
                </h2>
                {currentQuestion.hint && (
                  <p className="mt-3 text-sm text-brand-600 dark:text-brand-400 bg-brand-500/5 dark:bg-brand-500/10 px-4 py-2 rounded-lg">
                    💡 {currentQuestion.hint}
                  </p>
                )}
              </motion.div>
            </AnimatePresence>

            {/* ── Answer Area ── */}
            <div className="glass-card-solid p-6 space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare className="w-5 h-5 text-brand-500" />
                <h3 className="font-bold text-gray-800 dark:text-gray-200">Your Answer</h3>
              </div>

              <textarea
                value={answers[currentQuestion.question_id] || ''}
                onChange={(e) => setAnswers((prev) => ({ ...prev, [currentQuestion.question_id]: e.target.value }))}
                placeholder="Type your answer here, or use voice recording below..."
                rows={5}
                className="input-field resize-none"
              />

              {/* Voice recorder */}
              <VoiceRecorder onTranscript={handleVoiceTranscript} />

              <button
                onClick={handleEvaluate}
                disabled={evaluating || !answers[currentQuestion.question_id]?.trim()}
                className="btn-accent flex items-center gap-2"
              >
                {evaluating ? <><Loader2 className="w-4 h-4 animate-spin" /> Evaluating...</> : <><Send className="w-4 h-4" /> Submit & Evaluate</>}
              </button>
            </div>

            {/* ── Evaluation Result ── */}
            {currentEval && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card-solid p-6 space-y-4"
              >
                <div className="flex items-center gap-4">
                  <ScoreGauge score={currentEval.score * 10} size={100} label="Score" />
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-800 dark:text-gray-200 mb-1 flex items-center gap-2">
                      <Award className="w-5 h-5 text-amber-500" />
                      Evaluation Results
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                      {currentEval.feedback}
                    </p>
                  </div>
                </div>

                {currentEval.suggestions && currentEval.suggestions.length > 0 && (
                  <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800/30">
                    <h4 className="text-sm font-bold text-amber-700 dark:text-amber-400 mb-2">💡 Improvement Tips</h4>
                    <ul className="space-y-1">
                      {currentEval.suggestions.map((s, i) => (
                        <li key={i} className="text-sm text-amber-600 dark:text-amber-300">• {s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {currentEval.better_answer && (
                  <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-800/30">
                    <h4 className="text-sm font-bold text-emerald-700 dark:text-emerald-400 mb-2">✨ Better Answer</h4>
                    <p className="text-sm text-emerald-600 dark:text-emerald-300 leading-relaxed">
                      {currentEval.better_answer}
                    </p>
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Emotion Detection Result ── */}
            {currentEmotion && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card-solid p-6"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Brain className="w-5 h-5 text-purple-500" />
                  <h3 className="font-bold text-gray-800 dark:text-gray-200">Emotion & Confidence Analysis</h3>
                </div>

                {/* Emotion Label */}
                <div className="flex items-center gap-4 mb-4">
                  {(() => {
                    const ei = EMOTION_ICONS[currentEmotion.primary_emotion] || EMOTION_ICONS.neutral;
                    const EmIcon = ei.icon;
                    return (
                      <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border ${ei.bg}`}>
                        <EmIcon className={`w-8 h-8 ${ei.color}`} />
                        <div>
                          <p className={`text-lg font-bold ${ei.color}`}>{currentEmotion.emotion_label}</p>
                          <p className="text-xs text-gray-500">Primary detected emotion</p>
                        </div>
                      </div>
                    );
                  })()}
                </div>

                {/* Confidence Bars */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  {Object.entries(currentEmotion.confidence_scores || {}).map(([key, val]) => {
                    const ei = EMOTION_ICONS[key] || EMOTION_ICONS.neutral;
                    return (
                      <div key={key} className="text-center">
                        <p className="text-xs text-gray-500 dark:text-gray-400 capitalize mb-1">{key}</p>
                        <div className="h-2 rounded-full bg-gray-200 dark:bg-surface-800 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-700`}
                            style={{ width: `${val}%`, backgroundColor: ei.color === 'text-emerald-500' ? '#10b981' : ei.color === 'text-red-500' ? '#ef4444' : ei.color === 'text-amber-500' ? '#f59e0b' : '#6b7280' }}
                          />
                        </div>
                        <p className="text-xs font-bold mt-1 text-gray-700 dark:text-gray-300">{val}%</p>
                      </div>
                    );
                  })}
                </div>

                {/* Text Signals */}
                {currentEmotion.analysis?.text_signals?.length > 0 && (
                  <div className="mb-4 space-y-2">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Text Signals</p>
                    {currentEmotion.analysis.text_signals.map((sig, i) => (
                      <div key={i} className={`flex items-start gap-2 text-sm p-2 rounded-lg ${
                        sig.type === 'positive' ? 'bg-emerald-50 dark:bg-emerald-900/10 text-emerald-700 dark:text-emerald-400' :
                        sig.type === 'warning' ? 'bg-amber-50 dark:bg-amber-900/10 text-amber-700 dark:text-amber-400' :
                        'bg-gray-50 dark:bg-surface-800 text-gray-600 dark:text-gray-400'
                      }`}>
                        {sig.type === 'positive' ? <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" /> :
                         sig.type === 'warning' ? <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" /> :
                         <TrendingUp className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                        <span>{sig.signal}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Assessment */}
                {currentEmotion.analysis?.overall_assessment && (
                  <div className="p-3 rounded-xl bg-purple-50 dark:bg-purple-900/10 border border-purple-200 dark:border-purple-800/30 mb-4">
                    <p className="text-sm text-purple-700 dark:text-purple-300">{currentEmotion.analysis.overall_assessment}</p>
                  </div>
                )}

                {/* Tips */}
                {currentEmotion.tips?.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Coaching Tips</p>
                    {currentEmotion.tips.map((tip, i) => (
                      <p key={i} className="text-sm text-gray-600 dark:text-gray-400">{tip}</p>
                    ))}
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Navigation ── */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
                disabled={currentIndex === 0}
                className="btn-secondary flex items-center gap-1"
              >
                <ChevronLeft className="w-4 h-4" /> Previous
              </button>
              <span className="text-sm text-gray-500 font-medium">
                {currentIndex + 1} / {filteredQuestions.length}
              </span>
              <button
                onClick={() => setCurrentIndex((i) => Math.min(filteredQuestions.length - 1, i + 1))}
                disabled={currentIndex >= filteredQuestions.length - 1}
                className="btn-secondary flex items-center gap-1"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : (
          <div className="glass-card-solid p-10 text-center">
            <p className="text-gray-500">No questions match your filters. Try changing the category.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default InterviewSimulator;
