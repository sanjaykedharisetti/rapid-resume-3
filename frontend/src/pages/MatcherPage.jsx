import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AlertCircle, BookOpen, Brain, ChevronDown, ChevronUp, Loader2,
  RotateCcw, Sparkles, X
} from 'lucide-react'
import DropZone from '../components/DropZone'
import { analyzeResume } from '../services/api'

const EXAMPLE_JD = `We are looking for a Senior Python Developer to join our engineering team.

Requirements:
- 3+ years of Python development experience
- Strong knowledge of Machine Learning frameworks (TensorFlow, PyTorch, or scikit-learn)
- Experience with SQL databases (PostgreSQL or MySQL)
- Familiarity with Docker and Kubernetes
- AWS or Google Cloud experience is required
- Strong understanding of REST APIs and microservices

Preferred:
- Experience with Natural Language Processing (NLP)
- Knowledge of React or Vue.js for frontend integration
- Bachelor's degree in Computer Science or related field
- Experience with Git and CI/CD pipelines

Responsibilities:
- Build and deploy ML models at scale
- Write clean, well-documented Python code
- Collaborate with cross-functional teams
- Contribute to system design decisions`

export default function MatcherPage() {
  const navigate = useNavigate()
  const [resumeFile, setResumeFile] = useState(null)
  const [fileError, setFileError] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [jdError, setJdError] = useState('')
  const [showExample, setShowExample] = useState(false)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [apiError, setApiError] = useState('')

  const handleFileChange = (file, err) => {
    setResumeFile(file)
    setFileError(err || '')
    setApiError('')
  }

  const handleFileRemove = () => {
    setResumeFile(null)
    setFileError('')
  }

  const handleJdChange = (e) => {
    setJobDescription(e.target.value)
    setJdError('')
    setApiError('')
  }

  const validate = () => {
    let valid = true
    if (!resumeFile) {
      setFileError('Please upload your resume file.')
      valid = false
    }
    if (fileError) valid = false
    if (!jobDescription.trim()) {
      setJdError('Please paste the job description.')
      valid = false
    } else if (jobDescription.trim().length < 50) {
      setJdError('Job description is too short. Please paste the complete job description.')
      valid = false
    }
    return valid
  }

  const handleAnalyze = async () => {
    if (!validate()) return
    setLoading(true)
    setApiError('')
    setUploadProgress(0)

    try {
      const result = await analyzeResume(resumeFile, jobDescription, (event) => {
        if (event.total) {
          setUploadProgress(Math.round((event.loaded / event.total) * 100))
        }
      })
      // Navigate to results with data in state
      navigate(`/results/${result.analysis_id}`, { state: { result } })
    } catch (err) {
      setApiError(err.message || 'An unexpected error occurred. Please try again.')
    } finally {
      setLoading(false)
      setUploadProgress(0)
    }
  }

  const loadExample = () => {
    setJobDescription(EXAMPLE_JD)
    setJdError('')
    setShowExample(false)
  }

  const wordCount = jobDescription.trim() ? jobDescription.trim().split(/\s+/).length : 0

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm font-medium mb-6">
          <Brain size={13} />
          NLP Resume Analyzer
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white mb-4">
          Resume Matching Dashboard
        </h1>
        <p className="text-slate-400 max-w-xl mx-auto">
          Upload your resume and paste the job description below to receive a detailed compatibility analysis.
        </p>
      </div>

      {/* Error banner */}
      {apiError && (
        <div className="mb-8 flex items-start gap-3 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 animate-fade-in">
          <AlertCircle size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-red-300 font-semibold text-sm">Analysis Failed</p>
            <p className="text-red-400 text-sm mt-0.5">{apiError}</p>
          </div>
          <button onClick={() => setApiError('')} className="text-red-400 hover:text-red-300">
            <X size={16} />
          </button>
        </div>
      )}

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* ── Left: Resume Upload ── */}
        <div className="card-glass rounded-3xl p-6">
          <div className="flex items-center gap-2 mb-5">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <Sparkles size={16} className="text-blue-400" />
            </div>
            <h2 className="text-white font-bold text-lg">Resume Upload</h2>
          </div>
          <DropZone
            file={resumeFile}
            onFileChange={handleFileChange}
            onFileRemove={handleFileRemove}
            error={fileError}
          />
        </div>

        {/* ── Right: Job Description ── */}
        <div className="card-glass rounded-3xl p-6 flex flex-col">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-violet-500/20 flex items-center justify-center">
                <BookOpen size={16} className="text-violet-400" />
              </div>
              <h2 className="text-white font-bold text-lg">Job Description</h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowExample(!showExample)}
                className="flex items-center gap-1 text-xs text-slate-400 hover:text-blue-400 transition-colors px-3 py-1.5 rounded-lg border border-white/10 hover:border-blue-500/30"
              >
                Example {showExample ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>
              {jobDescription && (
                <button
                  onClick={() => { setJobDescription(''); setJdError('') }}
                  className="flex items-center gap-1 text-xs text-slate-400 hover:text-red-400 transition-colors px-3 py-1.5 rounded-lg border border-white/10 hover:border-red-500/30"
                >
                  <RotateCcw size={12} /> Clear
                </button>
              )}
            </div>
          </div>

          {/* Example JD banner */}
          {showExample && (
            <div className="mb-3 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-sm animate-fade-in">
              <p className="text-slate-300 mb-2">Load an example Python developer job description?</p>
              <button
                onClick={loadExample}
                className="text-blue-400 hover:text-blue-300 font-semibold underline"
              >
                Load example →
              </button>
            </div>
          )}

          <textarea
            id="job-description-input"
            className="flex-1 min-h-[320px] w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-slate-200 text-sm placeholder-slate-500 resize-none focus:outline-none focus:border-blue-500/50 focus:bg-white/8 transition-all"
            placeholder="Paste the complete job description here…

Include:
• Required skills and qualifications
• Years of experience
• Responsibilities
• Educational requirements
• Preferred qualifications"
            value={jobDescription}
            onChange={handleJdChange}
            aria-label="Job description"
          />

          <div className="flex items-center justify-between mt-3 text-xs text-slate-500">
            <span className={jobDescription.length < 50 && jobDescription.length > 0 ? 'text-amber-400' : ''}>
              {jobDescription.length} characters · {wordCount} words
            </span>
            {jobDescription.length > 0 && jobDescription.length < 50 && (
              <span className="text-amber-400">Too short — add more detail</span>
            )}
          </div>

          {jdError && (
            <div className="mt-2 flex items-center gap-1.5 text-red-400 text-sm">
              <AlertCircle size={13} />
              {jdError}
            </div>
          )}
        </div>
      </div>

      {/* Analyze button */}
      <div className="text-center">
        <button
          id="analyze-btn"
          onClick={handleAnalyze}
          disabled={loading}
          className="relative inline-flex items-center gap-3 px-12 py-5 rounded-2xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-bold text-lg btn-glow disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none transition-all hover:scale-105"
        >
          {loading ? (
            <>
              <Loader2 size={22} className="spinner" />
              <span>
                {uploadProgress > 0 && uploadProgress < 100
                  ? `Uploading… ${uploadProgress}%`
                  : 'Analyzing Resume…'}
              </span>
            </>
          ) : (
            <>
              <Brain size={22} />
              Analyze My Resume
            </>
          )}
        </button>
        <p className="mt-3 text-slate-500 text-sm">
          Analysis typically takes 5–30 seconds depending on document length
        </p>

        {/* Progress bar */}
        {loading && (
          <div className="mt-4 max-w-sm mx-auto">
            <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full progress-bar-fill animate-pulse-slow"
                style={{ width: loading ? '100%' : '0%' }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
