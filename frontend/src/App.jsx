import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import UploadResume from './pages/UploadResume';
import Dashboard from './pages/Dashboard';
import InterviewSimulator from './pages/InterviewSimulator';
import SkillRoadmap from './pages/SkillRoadmap';
import ProjectSuggestions from './pages/ProjectSuggestions';
import ResumeRewriter from './pages/ResumeRewriter';
import ProgressTracker from './pages/ProgressTracker';
import GitHubAnalyzer from './pages/GitHubAnalyzer';

/* ───── Dark Mode Context ───── */
export const DarkModeContext = createContext();

export function useDarkMode() {
  return useContext(DarkModeContext);
}

function App() {
  /* ── state for uploaded resume data ── */
  const [resumeData, setResumeData] = useState(null);
  /* ── state for analysis results ── */
  const [analysisData, setAnalysisData] = useState(null);
  /* ── global loading flag ── */
  const [loading, setLoading] = useState(false);
  /* ── dark mode toggle ── */
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : true; // default to dark
  });

  /* persist dark mode preference */
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  /* restore saved session data on mount */
  useEffect(() => {
    const savedResume = localStorage.getItem('resumeData');
    const savedAnalysis = localStorage.getItem('analysisData');
    if (savedResume) setResumeData(JSON.parse(savedResume));
    if (savedAnalysis) setAnalysisData(JSON.parse(savedAnalysis));
  }, []);

  /* save resume data when it changes */
  useEffect(() => {
    if (resumeData) localStorage.setItem('resumeData', JSON.stringify(resumeData));
  }, [resumeData]);

  /* save analysis data when it changes */
  useEffect(() => {
    if (analysisData) localStorage.setItem('analysisData', JSON.stringify(analysisData));
  }, [analysisData]);

  const toggleDarkMode = () => setDarkMode((prev) => !prev);

  return (
    <DarkModeContext.Provider value={{ darkMode, toggleDarkMode }}>
      <Router>
        <div className="min-h-screen bg-surface-50 dark:bg-surface-900 transition-colors duration-300">
          <Navbar resumeData={resumeData} />

          <Routes>
            <Route path="/" element={<Home />} />
            <Route
              path="/upload"
              element={
                <UploadResume
                  setResumeData={setResumeData}
                  setLoading={setLoading}
                />
              }
            />
            <Route
              path="/dashboard"
              element={
                <Dashboard
                  resumeData={resumeData}
                  analysisData={analysisData}
                  setAnalysisData={setAnalysisData}
                  loading={loading}
                  setLoading={setLoading}
                />
              }
            />
            <Route
              path="/interview"
              element={
                <InterviewSimulator
                  resumeData={resumeData}
                  analysisData={analysisData}
                  loading={loading}
                  setLoading={setLoading}
                />
              }
            />
            <Route
              path="/roadmap"
              element={
                <SkillRoadmap
                  analysisData={analysisData}
                  resumeData={resumeData}
                  loading={loading}
                  setLoading={setLoading}
                />
              }
            />
            <Route
              path="/projects"
              element={
                <ProjectSuggestions
                  analysisData={analysisData}
                  loading={loading}
                  setLoading={setLoading}
                />
              }
            />
            <Route
              path="/rewriter"
              element={
                <ResumeRewriter
                  resumeData={resumeData}
                  loading={loading}
                  setLoading={setLoading}
                />
              }
            />
            <Route
              path="/progress"
              element={
                <ProgressTracker
                  resumeData={resumeData}
                  analysisData={analysisData}
                />
              }
            />
            <Route path="/github" element={<GitHubAnalyzer />} />
          </Routes>

          <Toaster
            position="bottom-right"
            toastOptions={{
              className: 'font-sans',
              style: {
                background: darkMode ? '#1e293b' : '#ffffff',
                color: darkMode ? '#f1f5f9' : '#0f172a',
                border: darkMode ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e2e8f0',
              },
            }}
          />
        </div>
      </Router>
    </DarkModeContext.Provider>
  );
}

export default App;
