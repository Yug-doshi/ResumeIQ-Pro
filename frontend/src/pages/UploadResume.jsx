import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { uploadResume } from '../api/apiClient';

function UploadResume({ setResumeData, setLoading }) {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');

  /* ── Drag handlers ── */
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError('');

    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) validateAndSetFile(droppedFile);
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) validateAndSetFile(selectedFile);
  };

  /* ── File validation ── */
  const validateAndSetFile = (f) => {
    const allowed = ['.pdf', '.docx'];
    const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase();

    if (!allowed.includes(ext)) {
      setError('Only PDF and DOCX files are allowed');
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File too large. Max 10 MB');
      return;
    }

    setFile(f);
    setError('');
    setUploadResult(null);
  };

  /* ── Upload handler ── */
  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setLoading(true);
    setError('');

    try {
      const result = await uploadResume(file);
      setUploadResult(result);
      setResumeData({
        ...result,
        uploaded_at: new Date().toISOString(),
      });
      toast.success('Resume uploaded successfully! 🎉');
    } catch (err) {
      const message = err.response?.data?.detail || 'Upload failed. Please try again.';
      setError(message);
      toast.error(message);
    } finally {
      setUploading(false);
      setLoading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setUploadResult(null);
    setError('');
  };

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto"
      >
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="section-title">
            Upload Your <span className="gradient-text">Resume</span>
          </h1>
          <p className="section-subtitle">
            Drop your PDF or DOCX file to get started with AI analysis
          </p>
        </div>

        {/* Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`glass-card-solid p-10 text-center cursor-pointer transition-all duration-300 ${
            dragActive
              ? 'ring-2 ring-brand-500 bg-brand-500/5 dark:bg-brand-500/10 scale-[1.01]'
              : 'hover:border-brand-400 dark:hover:border-brand-600'
          } ${error ? 'ring-2 ring-red-400' : ''}`}
          onClick={() => !file && document.getElementById('fileInput').click()}
        >
          <input
            id="fileInput"
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            className="hidden"
          />

          {!file ? (
            <div className="py-8">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl gradient-bg flex items-center justify-center shadow-lg shadow-brand-500/20">
                <Upload className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2 text-gray-800 dark:text-gray-200">
                {dragActive ? 'Drop it here!' : 'Drag & drop your resume'}
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                or click to browse files
              </p>
              <div className="flex justify-center gap-3">
                <span className="badge badge-blue">PDF</span>
                <span className="badge badge-purple">DOCX</span>
                <span className="badge text-gray-500 bg-gray-100 dark:bg-gray-800">Max 10 MB</span>
              </div>
            </div>
          ) : (
            <div className="py-6">
              <div className="flex items-center justify-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-xl bg-brand-500/10 flex items-center justify-center">
                  <FileText className="w-6 h-6 text-brand-500" />
                </div>
                <div className="text-left">
                  <p className="font-semibold text-gray-800 dark:text-gray-200">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); clearFile(); }}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-700 transition-colors"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 flex items-center gap-2 px-4 py-3 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm"
          >
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </motion.div>
        )}

        {/* Upload Button */}
        {file && !uploadResult && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
          >
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="btn-primary w-full flex items-center justify-center gap-2 text-lg py-4"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Uploading & Extracting Text...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Upload & Analyze
                </>
              )}
            </button>
          </motion.div>
        )}

        {/* Upload Success */}
        {uploadResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 space-y-4"
          >
            <div className="glass-card-solid p-6">
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle className="w-6 h-6 text-emerald-500" />
                <h3 className="text-lg font-bold text-gray-800 dark:text-gray-200">
                  Resume Uploaded Successfully!
                </h3>
              </div>

              {/* Text preview */}
              <div className="p-4 rounded-xl bg-gray-50 dark:bg-surface-800 border border-gray-200 dark:border-gray-700 max-h-48 overflow-y-auto">
                <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap leading-relaxed">
                  {uploadResult.text_preview || 'Text extracted. Ready for analysis.'}
                </p>
              </div>
            </div>

            <button
              onClick={() => navigate('/dashboard')}
              className="btn-accent w-full flex items-center justify-center gap-2 text-lg py-4"
            >
              Go to Dashboard →
            </button>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

export default UploadResume;
