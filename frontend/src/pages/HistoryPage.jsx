import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  AlertCircle, Brain, Clock, Eye, History, Loader2,
  RefreshCw, Target, Trash2
} from 'lucide-react'
import { deleteHistory, getHistory } from '../services/api'
import { formatDate, getCategoryBadge, getScoreColor, safeNumber } from '../utils/helpers'

export default function HistoryPage() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState(null)

  const load = () => {
    setLoading(true)
    setError('')
    getHistory()
      .then(setRecords)
      .catch((e) => setError(e.message || 'Failed to load history.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (id) => {
    if (!confirm('Delete this analysis record? This cannot be undone.')) return
    setDeletingId(id)
    try {
      await deleteHistory(id)
      setRecords((prev) => prev.filter((r) => r.analysis_id !== id))
    } catch (e) {
      setError(e.message || 'Failed to delete record.')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-10 flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
              <History size={20} className="text-white" />
            </div>
            <h1 className="text-2xl font-black text-white">Analysis History</h1>
          </div>
          <p className="text-slate-400 text-sm ml-13">
            Review and compare your previous resume analyses.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={load}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-slate-300 text-sm hover:bg-white/10 transition-colors"
          >
            <RefreshCw size={14} /> Refresh
          </button>
          <Link
            to="/matcher"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 text-white text-sm font-semibold btn-glow"
          >
            <Brain size={14} /> New Analysis
          </Link>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 flex items-center gap-3 p-4 rounded-2xl bg-red-500/10 border border-red-500/20 animate-fade-in">
          <AlertCircle size={18} className="text-red-400 flex-shrink-0" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Loading */}
      {loading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={36} className="spinner text-blue-500" />
        </div>
      ) : records.length === 0 ? (
        /* Empty state */
        <div className="text-center py-24">
          <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-5">
            <History size={28} className="text-slate-500" />
          </div>
          <h3 className="text-white font-bold text-xl mb-2">No analyses yet</h3>
          <p className="text-slate-400 text-sm mb-8 max-w-sm mx-auto">
            Upload your first resume and analyze it against a job description to get started.
          </p>
          <Link
            to="/matcher"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-bold btn-glow"
          >
            <Brain size={18} /> Analyze My First Resume
          </Link>
        </div>
      ) : (
        /* Records table */
        <div className="space-y-4">
          <p className="text-slate-500 text-sm">{records.length} record{records.length !== 1 ? 's' : ''}</p>
          {records.map((r) => {
            const score = safeNumber(r.overall_score)
            return (
              <div
                key={r.analysis_id}
                className="card-glass rounded-2xl p-5 feature-card animate-fade-in-up"
              >
                <div className="flex items-center gap-4 flex-wrap">
                  {/* Score badge */}
                  <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-white/5 flex flex-col items-center justify-center border border-white/5">
                    <span className={`text-xl font-black ${getScoreColor(score)}`}>
                      {score.toFixed(0)}
                    </span>
                    <span className="text-slate-500 text-xs">/ 100</span>
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <p className="text-white font-semibold truncate">{r.filename}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${getCategoryBadge(r.match_category)}`}>
                        {r.match_category}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-500 flex-wrap">
                      <span className="flex items-center gap-1">
                        <Clock size={11} />
                        {formatDate(r.created_at)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Target size={11} />
                        {r.matched_skill_count} / {r.required_skill_count} skills matched
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Link
                      to={`/results/${r.analysis_id}`}
                      className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-blue-500/15 text-blue-300 border border-blue-500/20 text-sm font-medium hover:bg-blue-500/25 transition-colors"
                    >
                      <Eye size={13} /> View Report
                    </Link>
                    <button
                      onClick={() => handleDelete(r.analysis_id)}
                      disabled={deletingId === r.analysis_id}
                      className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                      title="Delete record"
                    >
                      {deletingId === r.analysis_id ? (
                        <Loader2 size={14} className="spinner" />
                      ) : (
                        <Trash2 size={14} />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
