import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Brain, Upload, BarChart3, Mic, Map, FolderGit2,
  FileEdit, Trophy, Sparkles, ArrowRight, Zap, Shield, Target
} from 'lucide-react';

/* ──── Feature cards data ──── */
const FEATURES = [
  { icon: BarChart3, title: 'ATS Score Calculator', desc: 'LSTM-powered resume scoring against job descriptions with keyword analysis', color: 'from-blue-500 to-cyan-500' },
  { icon: Brain, title: 'AI Interview Simulator', desc: 'Practice HR, Technical & Behavioral questions generated from your resume', color: 'from-purple-500 to-pink-500' },
  { icon: Mic, title: 'Voice Interview Practice', desc: 'Answer via voice, get real-time transcription and NLP-based evaluation', color: 'from-rose-500 to-orange-500' },
  { icon: Map, title: 'Skill Gap Roadmap', desc: 'Week-by-week learning plan with courses and milestones for missing skills', color: 'from-emerald-500 to-teal-500' },
  { icon: FolderGit2, title: 'Smart Project Suggestions', desc: 'Portfolio project ideas mapped to your skill gaps with tech stacks', color: 'from-amber-500 to-yellow-500' },
  { icon: Trophy, title: 'Candidate Ranking', desc: 'See your percentile among 100 simulated candidates for your target role', color: 'from-indigo-500 to-violet-500' },
  { icon: FileEdit, title: 'Resume Rewriter', desc: 'Transform weak bullet points into impactful statements with metrics', color: 'from-cyan-500 to-blue-500' },
  { icon: Target, title: 'Weakness Detection', desc: 'AI detects weak resume sections and provides targeted improvements', color: 'from-red-500 to-pink-500' },
];

/* ──── Stats ──── */
const STATS = [
  { number: '95%', label: 'Accuracy' },
  { number: '10K+', label: 'Resumes Analyzed' },
  { number: '50+', label: 'Job Roles' },
  { number: '8', label: 'AI Features' },
];

/* ──── Animation variants ──── */
const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: 'easeOut' },
  }),
};

function Home() {
  return (
    <div className="overflow-hidden">
      {/* ═══════════ HERO ═══════════ */}
      <section className="relative min-h-[90vh] flex items-center particles-bg">
        <div className="page-container relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-500/10 border border-brand-500/20 mb-6">
              <Sparkles className="w-4 h-4 text-brand-500" />
              <span className="text-sm font-semibold text-brand-600 dark:text-brand-400">
                LSTM & GRU Powered AI
              </span>
            </div>

            {/* Title */}
            <h1 className="text-5xl md:text-7xl font-black leading-tight mb-6">
              Ace Your Dream Job
              <br />
              <span className="gradient-text">With AI Intelligence</span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              Upload your resume, get LSTM-powered ATS scoring, practice with AI interviews,
              and receive a complete career roadmap — all in one platform.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/upload" className="btn-primary flex items-center gap-2 text-lg px-8 py-4">
                <Upload className="w-5 h-5" />
                Analyze My Resume
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link to="/dashboard" className="btn-secondary flex items-center gap-2 text-lg px-8 py-4">
                View Demo Dashboard
              </Link>
            </div>
          </motion.div>

          {/* Floating decorative elements */}
          <div className="absolute top-20 left-10 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-20 right-10 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl animate-float animate-delay-300" />
        </div>
      </section>

      {/* ═══════════ STATS BAR ═══════════ */}
      <section className="py-12 bg-gradient-to-r from-brand-600 to-purple-600">
        <div className="page-container">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {STATS.map((stat, i) => (
              <motion.div
                key={i}
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                variants={fadeUp}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-black text-white mb-1">{stat.number}</div>
                <div className="text-sm text-white/70 font-medium">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ FEATURES ═══════════ */}
      <section className="py-24">
        <div className="page-container">
          <div className="text-center mb-16">
            <h2 className="section-title">
              Powerful <span className="gradient-text">AI Features</span>
            </h2>
            <p className="section-subtitle">Everything you need to land your dream job</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={i}
                  custom={i}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeUp}
                  className="glass-card-solid p-6 card-hover group cursor-pointer"
                >
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold mb-2 text-gray-800 dark:text-gray-200">{feature.title}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{feature.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════ HOW IT WORKS ═══════════ */}
      <section className="py-24 bg-gray-50/50 dark:bg-surface-800/30">
        <div className="page-container">
          <div className="text-center mb-16">
            <h2 className="section-title">How It Works</h2>
            <p className="section-subtitle">Four simple steps to career success</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { step: '01', title: 'Upload Resume', desc: 'Upload your PDF or DOCX resume', icon: Upload },
              { step: '02', title: 'Select Target Role', desc: 'Choose job role or paste a JD', icon: Target },
              { step: '03', title: 'Get AI Analysis', desc: 'LSTM-powered scoring & insights', icon: Brain },
              { step: '04', title: 'Improve & Practice', desc: 'Roadmap, interview prep & more', icon: Zap },
            ].map((item, i) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={i}
                  custom={i}
                  initial="hidden"
                  whileInView="visible"
                  viewport={{ once: true }}
                  variants={fadeUp}
                  className="text-center"
                >
                  <div className="relative inline-block mb-4">
                    <div className="w-16 h-16 rounded-2xl gradient-bg flex items-center justify-center shadow-lg shadow-brand-500/20">
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-white dark:bg-surface-800 border-2 border-brand-500 text-brand-600 text-xs font-bold flex items-center justify-center">
                      {item.step}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold mb-2 text-gray-800 dark:text-gray-200">{item.title}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{item.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ═══════════ CTA ═══════════ */}
      <section className="py-24">
        <div className="page-container text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-card-solid p-12 md:p-16 max-w-3xl mx-auto"
          >
            <Sparkles className="w-10 h-10 text-brand-500 mx-auto mb-4" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to <span className="gradient-text">Transform Your Career?</span>
            </h2>
            <p className="text-gray-500 dark:text-gray-400 text-lg mb-8">
              Get AI-powered resume analysis and personalized interview preparation
            </p>
            <Link to="/upload" className="btn-primary inline-flex items-center gap-2 text-lg px-8 py-4">
              <Upload className="w-5 h-5" />
              Start Free Analysis
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ═══════════ FOOTER ═══════════ */}
      <footer className="py-8 border-t border-gray-200 dark:border-gray-800">
        <div className="page-container text-center">
          <p className="text-sm text-gray-500 dark:text-gray-500">
            © 2025 ResumeAI — Built with LSTM/GRU Neural Networks, React & FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default Home;
