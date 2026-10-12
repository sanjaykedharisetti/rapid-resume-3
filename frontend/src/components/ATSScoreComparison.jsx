import { Award, CheckCircle2, TrendingUp, AlertCircle, Sparkles } from 'lucide-react'
import ScoreCircle from './ScoreCircle'

export default function ATSScoreComparison({
  originalScore,
  optimizedScore,
  scoreImprovement,
  targetScore = 85,
  targetReached = false,
  statusMessage,
  componentBefore,
  componentAfter,
}) {
  const isImproved = scoreImprovement > 0

  const components = [
    { label: 'Semantic Similarity (40%)', key: 'semantic_similarity_score', color: 'from-blue-500 to-indigo-500' },
    { label: 'Skills Match (35%)', key: 'skill_matching_score', color: 'from-cyan-500 to-teal-500' },
    { label: 'Qualifications (15%)', key: 'qualification_matching_score', color: 'from-emerald-500 to-green-500' },
    { label: 'Experience Relevance (10%)', key: 'experience_relevance_score', color: 'from-amber-500 to-orange-500' },
  ]

  return (
    <div className="card-glass rounded-3xl p-6 sm:p-8 space-y-8 animate-scale-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 inline-flex items-center gap-1.5 mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            ATS Compatibility Recalculation
          </span>
          <h2 className="text-2xl sm:text-3xl font-black text-white">Before vs. After Optimization</h2>
        </div>

        <div className={`px-4 py-2 rounded-2xl flex items-center gap-2 border text-sm font-bold ${
          targetReached
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
        }`}>
          {targetReached ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
          {targetReached ? 'Target Reached (85%+)' : 'Further Gaps Remaining'}
        </div>
      </div>

      {/* Side-by-side Score Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        {/* Original Score */}
        <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 text-center space-y-4">
          <p className="text-xs uppercase tracking-wider font-semibold text-slate-400">Original ATS Score</p>
          <div className="flex justify-center">
            <ScoreCircle score={originalScore} size={150} />
          </div>
          <p className="text-xs text-slate-500">Extracted baseline without ATS formatting</p>
        </div>

        {/* Improvement Metric in Center */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-cyan-500/10 via-blue-500/5 to-purple-500/10 border border-cyan-500/20 text-center space-y-3">
          <p className="text-xs uppercase tracking-wider font-semibold text-slate-400">Score Improvement</p>
          <div className="flex items-center justify-center gap-2 text-3xl sm:text-4xl font-black text-cyan-400">
            <TrendingUp className="w-8 h-8 text-cyan-400 animate-bounce" />
            +{scoreImprovement}%
          </div>
          <div className="inline-block px-3 py-1 rounded-full bg-white/10 text-xs font-mono text-slate-300">
            Target: {targetScore}%
          </div>
          <p className="text-xs text-slate-400 italic">
            {statusMessage}
          </p>
        </div>

        {/* Optimized Score */}
        <div className="p-6 rounded-2xl bg-emerald-500/[0.04] border border-emerald-500/20 text-center space-y-4">
          <p className="text-xs uppercase tracking-wider font-semibold text-emerald-400">Optimized ATS Score</p>
          <div className="flex justify-center">
            <ScoreCircle score={optimizedScore} size={150} />
          </div>
          <p className="text-xs text-slate-400">Recalculated with genuine ATS-tailored content</p>
        </div>
      </div>

      {/* Component Level Breakdown */}
      {componentBefore && componentAfter && (
        <div className="space-y-4 pt-4 border-t border-white/10">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Component Score Progression
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {components.map((c) => {
              const beforeVal = componentBefore[c.key] || 0
              const afterVal = componentAfter[c.key] || 0
              const diff = roundOne(afterVal - beforeVal)

              return (
                <div key={c.key} className="p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300 font-medium">{c.label}</span>
                    <span className="font-mono text-cyan-400 font-bold">
                      {beforeVal}% → {afterVal}% {diff > 0 && `(+${diff}%)`}
                    </span>
                  </div>
                  <div className="h-2 bg-white/5 rounded-full overflow-hidden flex">
                    <div
                      className={`h-full bg-gradient-to-r ${c.color} transition-all duration-1000`}
                      style={{ width: `${Math.min(100, afterVal)}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

function roundOne(n) {
  return Math.round(n * 10) / 10
}
