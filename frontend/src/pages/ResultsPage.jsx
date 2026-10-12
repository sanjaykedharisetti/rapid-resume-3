import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import {
  AlertCircle, ArrowLeft, Award, BookOpen, Brain, CheckCircle2,
  Download, Info, Key, Lightbulb, Loader2, Plus, RefreshCw,
  Sparkles, Target, TrendingUp, User, XCircle
} from 'lucide-react'
import ScoreCircle from '../components/ScoreCircle'
import { CategoryScoreChart, CompatibilityRadar, SkillMatchChart } from '../components/Charts'
import { getHistoryDetail, getReportUrl } from '../services/api'
import { getCategoryBadge, getScoreColor, safeArray, safeNumber } from '../utils/helpers'

function Section({ icon: Icon, iconBg, title, children }) {
  return (
    <div className="card-glass rounded-2xl p-6 animate-fade-in-up">
      <div className="flex items-center gap-3 mb-5">
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${iconBg}`}>
          <Icon size={18} className="text-white" />
        </div>
        <h2 className="text-white font-bold text-lg">{title}</h2>
      </div>
      {children}
    </div>
  )
}

function SkillTag({ label, type }) {
  const styles = {
    matched: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
    missing: 'bg-red-500/15 text-red-300 border-red-500/25',
    preferred: 'bg-amber-500/15 text-amber-300 border-amber-500/25',
    additional: 'bg-blue-500/15 text-blue-300 border-blue-500/25',
  }
  const icons = {
    matched: <CheckCircle2 size={11} />,
    missing: <XCircle size={11} />,
    preferred: <Plus size={11} />,
    additional: <Plus size={11} />,
  }
  return (
    <span className={`skill-tag border ${styles[type] || styles.additional}`}>
      {icons[type]}
      {label}
    </span>
  )
}

function ProgressBar({ label, value, color = 'blue' }) {
  const [width, setWidth] = useState(0)
  useEffect(() => {
    const t = setTimeout(() => setWidth(value), 100)
    return () => clearTimeout(t)
  }, [value])
  const colors = {
    blue: 'from-blue-500 to-cyan-500',
    emerald: 'from-emerald-500 to-teal-500',
    violet: 'from-violet-500 to-purple-600',
    amber: 'from-amber-500 to-orange-500',
  }
  return (
    <div className="mb-4">
      <div className="flex justify-between text-sm mb-1.5">
        <span className="text-slate-300 font-medium">{label}</span>
        <span className="text-slate-400">{value?.toFixed(1)}</span>
      </div>
      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${colors[color]} rounded-full progress-bar-fill`}
          style={{ width: `${Math.min(100, width)}%` }}
        />
      </div>
    </div>
  )
}

export default function ResultsPage() {
  const { id } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const [data, setData] = useState(location.state?.result || null)
  const [loading, setLoading] = useState(!data)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!data && id) {
      getHistoryDetail(id)
        .then(setData)
        .catch((e) => setError(e.message || 'Failed to load analysis.'))
        .finally(() => setLoading(false))
    }
  }, [id, data])

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <Loader2 size={40} className="spinner text-blue-500 mx-auto mb-4" />
          <p className="text-slate-400">Loading analysis results…</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4">
        <div className="text-center">
          <AlertCircle size={48} className="text-red-400 mx-auto mb-4" />
          <h2 className="text-white font-bold text-xl mb-2">Results Not Found</h2>
          <p className="text-slate-400 mb-6">{error || 'No analysis data available.'}</p>
          <Link to="/matcher" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 text-white font-semibold">
            <ArrowLeft size={16} /> Try Again
          </Link>
        </div>
      </div>
    )
  }

  const score = safeNumber(data.overall_score)
  const category = data.match_category || 'Low Match'
  const matchedSkills = safeArray(data.matched_skills)
  const missingRequired = safeArray(data.missing_required_skills)
  const missingPreferred = safeArray(data.missing_preferred_skills)
  const additionalSkills = safeArray(data.additional_skills)
  const resumeQuals = safeArray(data.resume_qualifications)
  const jobQuals = safeArray(data.job_qualifications)
  const resumeExp = safeArray(data.resume_experience)
  const jobExpReq = safeArray(data.job_experience_requirements)
  const keywords = safeArray(data.important_keywords)
  const missingKw = safeArray(data.missing_keywords)
  const suggestions = safeArray(data.improvement_suggestions)
  const limitations = safeArray(data.limitations)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Back button + actions */}
      <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
        <Link
          to="/matcher"
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm"
        >
          <ArrowLeft size={16} /> Back to Analyzer
        </Link>
        <div className="flex items-center gap-3 flex-wrap">
          <Link
            to={`/optimize/${data.analysis_id}`}
            state={{ analysis: data }}
            id="improve-ats-score-btn"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-white text-sm font-bold shadow-lg shadow-emerald-500/25 transition-all transform hover:-translate-y-0.5"
          >
            <Sparkles size={16} /> 🚀 Improve My ATS Score
          </Link>
          <a
            href={getReportUrl(data.analysis_id)}
            target="_blank"
            rel="noopener noreferrer"
            id="download-report-btn"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-slate-300 text-sm font-medium hover:bg-white/10 hover:text-white transition-all"
          >
            <Download size={15} /> Download PDF Report
          </a>
          <Link
            to="/matcher"
            id="analyze-another-btn"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-semibold btn-glow"
          >
            <RefreshCw size={14} /> Analyze Another
          </Link>
        </div>
      </div>

      {/* ── Overall Score Hero ── */}
      <div className="card-glass rounded-3xl p-8 mb-6 animate-scale-in">
        <div className="flex flex-col lg:flex-row items-center gap-8">
          {/* Score Circle */}
          <div className="relative flex-shrink-0">
            <ScoreCircle score={score} size={200} />
          </div>

          {/* Score Info */}
          <div className="flex-1 text-center lg:text-left">
            <p className="text-slate-400 text-sm font-medium mb-2">
              <span className="font-mono text-slate-300">{data.filename}</span> vs. Job Description
            </p>
            <h1 className="text-3xl font-black text-white mb-3">
              Analysis Results
            </h1>
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-base font-bold mb-4 ${getCategoryBadge(category)}`}>
              <Target size={16} />
              {category}
            </div>
            <p className="text-slate-400 text-sm max-w-lg leading-relaxed">
              This score reflects estimated text-based compatibility between your resume and the job description.
              It is <strong className="text-slate-300">not a hiring probability</strong> — it helps identify areas to strengthen.
            </p>
          </div>

          {/* Component scores */}
          <div className="flex-shrink-0 w-full lg:w-64">
            <ProgressBar label="Semantic Match" value={safeNumber(data.semantic_similarity_score)} color="blue" />
            <ProgressBar label="Skill Coverage" value={safeNumber(data.skill_matching_score)} color="emerald" />
            <ProgressBar label="Qualifications" value={safeNumber(data.qualification_matching_score)} color="violet" />
            <ProgressBar label="Experience" value={safeNumber(data.experience_relevance_score)} color="amber" />
          </div>
        </div>
      </div>

      {/* ── AI Optimizer Callout Banner ── */}
      <div className="card-glass rounded-2xl p-6 mb-6 border border-cyan-500/30 bg-gradient-to-r from-cyan-950/30 via-slate-900/60 to-emerald-950/20 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="space-y-1 text-center md:text-left">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3 h-3" />
            ATS Optimization Available
          </div>
          <h3 className="text-lg font-bold text-white">
            Want to boost your ATS compatibility score toward 85%?
          </h3>
          <p className="text-xs text-slate-300">
            Our AI Resume Optimizer restructures sections, normalizes verified skills, and sharpens action verbs.
          </p>
        </div>
        <Link
          to={`/optimize/${data.analysis_id}`}
          state={{ analysis: data }}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 via-teal-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-white text-sm font-black shadow-lg shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5 shrink-0"
        >
          <Sparkles size={16} /> 🚀 Improve My ATS Score
        </Link>
      </div>

      {/* ── Charts row ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="card-glass rounded-2xl p-6 lg:col-span-1">
          <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wide">Component Scores</h3>
          <CategoryScoreChart data={data} />
        </div>
        <div className="card-glass rounded-2xl p-6 lg:col-span-1">
          <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wide">Skill Breakdown</h3>
          <SkillMatchChart
            matched={matchedSkills}
            missing={missingRequired}
            preferred={missingPreferred}
          />
        </div>
        <div className="card-glass rounded-2xl p-6 lg:col-span-1">
          <h3 className="text-white font-semibold mb-4 text-sm uppercase tracking-wide">Compatibility Radar</h3>
          <CompatibilityRadar data={data} />
        </div>
      </div>

      {/* ── Main results grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skills Analysis */}
        <Section icon={Target} iconBg="bg-gradient-to-br from-emerald-500 to-teal-600" title="Skills Analysis">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-4 pb-3 border-b border-white/5">
            <span>Required skill coverage</span>
            <span className={`font-bold text-base ${getScoreColor(safeNumber(data.required_skill_coverage))}`}>
              {safeNumber(data.required_skill_coverage).toFixed(1)}%
            </span>
          </div>

          {matchedSkills.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2 flex items-center gap-1.5">
                <CheckCircle2 size={11} className="text-emerald-400" /> Matched Skills ({matchedSkills.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {matchedSkills.map((s) => <SkillTag key={s} label={s} type="matched" />)}
              </div>
            </div>
          )}

          {missingRequired.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2 flex items-center gap-1.5">
                <XCircle size={11} className="text-red-400" /> Missing Required ({missingRequired.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {missingRequired.map((s) => <SkillTag key={s} label={s} type="missing" />)}
              </div>
            </div>
          )}

          {missingPreferred.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2 flex items-center gap-1.5">
                <Plus size={11} className="text-amber-400" /> Missing Preferred ({missingPreferred.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {missingPreferred.map((s) => <SkillTag key={s} label={s} type="preferred" />)}
              </div>
            </div>
          )}

          {additionalSkills.length > 0 && (
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2 flex items-center gap-1.5">
                <Plus size={11} className="text-blue-400" /> Additional Resume Skills ({additionalSkills.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {additionalSkills.map((s) => <SkillTag key={s} label={s} type="additional" />)}
              </div>
            </div>
          )}

          {matchedSkills.length === 0 && missingRequired.length === 0 && (
            <p className="text-slate-500 text-sm">No skills were detected in the documents.</p>
          )}
        </Section>

        {/* Qualifications */}
        <Section icon={Award} iconBg="bg-gradient-to-br from-violet-500 to-purple-600" title="Qualification Analysis">
          {resumeQuals.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2 flex items-center gap-1.5">
                <User size={11} className="text-violet-400" /> Identified in Your Resume
              </p>
              <div className="flex flex-wrap gap-2">
                {resumeQuals.map((q) => (
                  <span key={q} className="skill-tag bg-violet-500/15 text-violet-300 border border-violet-500/25">
                    <CheckCircle2 size={11} /> {q}
                  </span>
                ))}
              </div>
            </div>
          )}

          {jobQuals.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2 flex items-center gap-1.5">
                <BookOpen size={11} className="text-blue-400" /> Job Requirements
              </p>
              <div className="flex flex-wrap gap-2">
                {jobQuals.map((q) => (
                  <span key={q} className="skill-tag bg-blue-500/15 text-blue-300 border border-blue-500/25">
                    {q}
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.qualification_notes && (
            <div className="mt-4 p-3 rounded-xl bg-white/4 border border-white/5 text-slate-400 text-xs leading-relaxed flex gap-2">
              <Info size={13} className="flex-shrink-0 mt-0.5 text-slate-500" />
              {data.qualification_notes}
            </div>
          )}

          {resumeQuals.length === 0 && jobQuals.length === 0 && (
            <p className="text-slate-500 text-sm">No qualification information could be extracted.</p>
          )}
        </Section>

        {/* Experience */}
        <Section icon={TrendingUp} iconBg="bg-gradient-to-br from-amber-500 to-orange-600" title="Experience Analysis">
          {data.experience_notes && (
            <div className="mb-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-sm leading-relaxed">
              {data.experience_notes}
            </div>
          )}

          {resumeExp.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2">From Your Resume</p>
              <ul className="space-y-1.5">
                {resumeExp.slice(0, 5).map((e, i) => (
                  <li key={i} className="text-slate-300 text-sm flex items-start gap-2">
                    <span className="text-amber-500 mt-1 flex-shrink-0">•</span>
                    {e}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {jobExpReq.length > 0 && (
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2">Job Requirements</p>
              <ul className="space-y-1.5">
                {jobExpReq.slice(0, 5).map((e, i) => (
                  <li key={i} className="text-slate-400 text-sm flex items-start gap-2">
                    <span className="text-blue-500 mt-1 flex-shrink-0">•</span>
                    {e}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <p className="mt-4 text-slate-600 text-xs italic">
            Note: Experience is extracted from text mentions and may not be fully accurate.
          </p>
        </Section>

        {/* Keywords */}
        <Section icon={Key} iconBg="bg-gradient-to-br from-cyan-500 to-blue-600" title="Keyword Analysis">
          {keywords.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-2">
                Important Job Keywords ({keywords.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {keywords.map((kw) => {
                  const isMissing = missingKw.includes(kw)
                  return (
                    <span
                      key={kw}
                      className={`skill-tag ${isMissing
                        ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}
                    >
                      {isMissing ? <XCircle size={10} /> : <CheckCircle2 size={10} />}
                      {kw}
                    </span>
                  )
                })}
              </div>
            </div>
          )}
          <p className="text-slate-600 text-xs mt-2">
            Green = found in resume · Red = missing from resume
          </p>
        </Section>

        {/* Suggestions */}
        <Section icon={Lightbulb} iconBg="bg-gradient-to-br from-yellow-500 to-amber-600" title="Improvement Suggestions">
          {suggestions.length > 0 ? (
            <ul className="space-y-3">
              {suggestions.map((s, i) => (
                <li key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/3 border border-white/5">
                  <span className="w-6 h-6 rounded-full bg-yellow-500/20 text-yellow-400 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  <span className="text-slate-300 text-sm leading-relaxed">{s}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-slate-400 text-sm">No specific suggestions at this time.</p>
          )}
        </Section>

        {/* Limitations */}
        <Section icon={Info} iconBg="bg-gradient-to-br from-slate-500 to-slate-700" title="Important Limitations">
          {limitations.length > 0 ? (
            <ul className="space-y-2">
              {limitations.map((lim, i) => (
                <li key={i} className="flex items-start gap-2 text-slate-400 text-sm">
                  <AlertCircle size={13} className="flex-shrink-0 mt-0.5 text-slate-500" />
                  {lim}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-slate-400 text-sm">No specific limitations noted.</p>
          )}
        </Section>
      </div>

      {/* Bottom actions */}
      <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
        <a
          href={getReportUrl(data.analysis_id)}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-2xl bg-white/5 border border-white/10 text-slate-300 font-semibold hover:bg-white/10 hover:text-white transition-all"
        >
          <Download size={18} /> Download Full PDF Report
        </a>
        <Link
          to="/matcher"
          className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-bold btn-glow"
        >
          <Brain size={18} /> Analyze Another Resume
        </Link>
      </div>
    </div>
  )
}
