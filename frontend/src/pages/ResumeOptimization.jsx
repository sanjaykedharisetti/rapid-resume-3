import { useState, useEffect } from 'react'
import { useParams, useLocation, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft, Brain, Sparkles, RefreshCw, AlertCircle, Loader2,
  CheckCircle2, Target, HelpCircle, Layers, FileText, ChevronRight
} from 'lucide-react'
import { getHistoryDetail, optimizeResume, getOptimization } from '../services/api'
import ATSScoreComparison from '../components/ATSScoreComparison'
import OptimizationProgress from '../components/OptimizationProgress'
import ResumePreview from '../components/ResumePreview'
import MissingSkillsPanel from '../components/MissingSkillsPanel'
import OptimizationSummary from '../components/OptimizationSummary'
import DownloadResumeButtons from '../components/DownloadResumeButtons'

export default function ResumeOptimization() {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()

  const [analysis, setAnalysis] = useState(location.state?.analysis || null)
  const [loadingAnalysis, setLoadingAnalysis] = useState(!analysis)
  const [optData, setOptData] = useState(null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [error, setError] = useState('')
  const [targetScore, setTargetScore] = useState(85)
  const [iterations, setIterations] = useState(3)

  // Fetch initial analysis if not passed in route state
  useEffect(() => {
    if (!analysis && id) {
      setLoadingAnalysis(true)
      getHistoryDetail(id)
        .then((data) => {
          setAnalysis(data)
          // Also check if this analysis was already optimized previously
          getOptimization(id)
            .then((existing) => setOptData(existing))
            .catch(() => {})
        })
        .catch((e) => setError(e.message || 'Failed to load analysis details.'))
        .finally(() => setLoadingAnalysis(false))
    } else if (analysis && id) {
      // Check if existing optimization exists in DB
      getOptimization(id)
        .then((existing) => setOptData(existing))
        .catch(() => {})
    }
  }, [id, analysis])

  const handleRunOptimization = async () => {
    if (!id) return
    setIsOptimizing(true)
    setError('')

    try {
      const result = await optimizeResume(id, {
        target_score: targetScore,
        iterations: iterations,
      })
      setOptData(result)
    } catch (e) {
      setError(e.message || 'Resume optimization failed. Please verify the backend service.')
    } finally {
      setIsOptimizing(false)
    }
  }

  if (loadingAnalysis) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <Loader2 size={40} className="spinner text-cyan-400 mx-auto mb-4" />
          <p className="text-slate-400">Loading analysis context…</p>
        </div>
      </div>
    )
  }

  if (error && !analysis) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4">
        <div className="text-center">
          <AlertCircle size={48} className="text-red-400 mx-auto mb-4" />
          <h2 className="text-white font-bold text-xl mb-2">Analysis Session Not Found</h2>
          <p className="text-slate-400 mb-6">{error}</p>
          <Link
            to="/matcher"
            className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-medium"
          >
            Start New Analysis
          </Link>
        </div>
      </div>
    )
  }

  const originalScore = optData?.original_score ?? analysis?.overall_score ?? 0
  const matchedSkillsCount = optData?.matched_skills_before?.length ?? analysis?.matched_skills?.length ?? 0
  const missingReq = optData?.remaining_missing_skills ?? analysis?.missing_required_skills ?? []
  const missingPref = optData?.missing_preferred_skills ?? analysis?.missing_preferred_skills ?? []
  const missingKw = optData?.missing_keywords ?? analysis?.missing_keywords ?? []

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-10">
      {/* Navigation header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <Link
          to={`/results/${id}`}
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm"
        >
          <ArrowLeft size={16} /> Back to Analysis Results
        </Link>
        <div className="flex items-center gap-3">
          <Link
            to="/matcher"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-slate-300 text-sm font-medium hover:bg-white/10"
          >
            <RefreshCw size={14} /> Start New Analysis
          </Link>
        </div>
      </div>

      {/* Hero Banner */}
      <div className="card-glass rounded-3xl p-8 bg-gradient-to-r from-cyan-950/30 via-slate-900/60 to-blue-950/30 border border-cyan-500/20 space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5" />
          AI Resume Optimizer
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white">
          Elevate Your ATS Compatibility
        </h1>
        <p className="max-w-3xl text-slate-300 text-sm sm:text-base leading-relaxed">
          Transform your resume into a modern, single-column ATS powerhouse. Our engine normalizes your technical taxonomy,
          sharpens bullet points with strong action verbs, and aligns section architecture—without fabricating a single skill or qualification.
        </p>

        {/* Current State Quick Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-white/10">
          <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5">
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Original Score</span>
            <p className="text-xl font-bold text-slate-200 mt-0.5">{originalScore}%</p>
          </div>
          <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
            <span className="text-[11px] text-cyan-300 uppercase font-semibold">Target Goal</span>
            <p className="text-xl font-bold text-cyan-400 mt-0.5">{targetScore}%</p>
          </div>
          <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5">
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Matched Skills</span>
            <p className="text-xl font-bold text-emerald-400 mt-0.5">{matchedSkillsCount}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5">
            <span className="text-[11px] text-slate-400 uppercase font-semibold">Missing Required</span>
            <p className="text-xl font-bold text-red-400 mt-0.5">{missingReq.length}</p>
          </div>
        </div>
      </div>

      {/* Pre-Optimization Diagnosis (if not optimized yet or as context) */}
      {!optData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card-glass rounded-2xl p-6 border border-white/10 space-y-3">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Target className="w-4 h-4 text-cyan-400" />
              Target Role Alignment
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Original resume scored <strong className="text-white">{originalScore}%</strong>. Optimization restructures your content to directly address the Job Description requirements.
            </p>
          </div>

          <div className="card-glass rounded-2xl p-6 border border-white/10 space-y-3">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              Skill Gaps Detected
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Found <strong className="text-white">{missingReq.length} missing required skills</strong>. Legitimate matching skills will be prioritized, and unearned skills flagged.
            </p>
          </div>

          <div className="card-glass rounded-2xl p-6 border border-white/10 space-y-3">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              ATS Readability
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Converts irregular headings into strict single-column ATS sections with action-oriented bullets.
            </p>
          </div>
        </div>
      )}

      {/* Optimization Action Bar */}
      <div className="card-glass rounded-2xl p-6 border border-cyan-500/30 flex flex-col sm:flex-row items-center justify-between gap-6 bg-gradient-to-r from-cyan-950/20 to-slate-900/40">
        <div>
          <h3 className="text-lg font-bold text-white">
            {optData ? 'Re-run Optimization' : 'Ready to Optimize Your Resume?'}
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Iterative engine tests multiple configurations and returns the highest truthful ATS score.
          </p>
        </div>

        <div className="flex items-center gap-4 w-full sm:w-auto justify-end">
          <button
            onClick={handleRunOptimization}
            disabled={isOptimizing}
            id="optimize-resume-btn"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl font-bold bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-lg shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isOptimizing ? (
              <>
                <Loader2 className="w-5 h-5 spinner" />
                Optimizing with AI…
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 text-cyan-200" />
                {optData ? 'Re-Optimize Resume' : 'Optimize Resume with AI'}
              </>
            )}
          </button>
        </div>
      </div>

      {/* Loading Progress State */}
      <OptimizationProgress isRunning={isOptimizing} />

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Post-Optimization Results */}
      {optData && !isOptimizing && (
        <div className="space-y-10 animate-fade-in">
          {/* 1. Score Comparison */}
          <ATSScoreComparison
            originalScore={optData.original_score}
            optimizedScore={optData.optimized_score}
            scoreImprovement={optData.score_improvement}
            targetScore={optData.target_score}
            targetReached={optData.target_reached}
            statusMessage={optData.status_message}
            componentBefore={optData.component_scores_before}
            componentAfter={optData.component_scores_after}
          />

          {/* 2. Download Buttons */}
          <DownloadResumeButtons analysisId={id} disabled={isOptimizing} />

          {/* 3. Side-by-Side Content Comparison */}
          <ResumePreview
            originalText={optData.original_resume_text}
            optimizedText={optData.optimized_resume_text}
            originalScore={optData.original_score}
            optimizedScore={optData.optimized_score}
            originalSections={optData.original_sections}
            optimizedSections={optData.optimized_sections}
          />

          {/* 4. Missing Skills & Keywords */}
          <MissingSkillsPanel
            matchedSkills={optData.matched_skills_after}
            newlyMatchedSkills={optData.newly_matched_skills}
            missingRequired={optData.remaining_missing_skills}
            missingPreferred={optData.missing_preferred_skills}
            missingKeywords={optData.missing_keywords}
          />

          {/* 5. Summary & Transparency */}
          <OptimizationSummary
            summaryOfChanges={optData.summary_of_changes}
            formattingIssues={optData.formatting_issues}
            unansweredQuestions={optData.unanswered_questions}
            remainingGaps={optData.remaining_gaps}
          />
        </div>
      )}
    </div>
  )
}
