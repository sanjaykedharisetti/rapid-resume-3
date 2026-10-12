import { CheckCircle2, AlertTriangle, HelpCircle, Key, Layers, Sparkles } from 'lucide-react'

export default function MissingSkillsPanel({
  matchedSkills = [],
  newlyMatchedSkills = [],
  missingRequired = [],
  missingPreferred = [],
  missingKeywords = [],
}) {
  return (
    <div className="card-glass rounded-3xl p-6 sm:p-8 space-y-6">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            Skills & Keyword Breakdown
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Genuine skills elevated by the optimizer vs. remaining unearned skills.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 1. Verified Matched Skills */}
        <div className="p-5 rounded-2xl bg-emerald-500/[0.04] border border-emerald-500/20 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              Verified Matched Skills ({matchedSkills.length})
            </h4>
            {newlyMatchedSkills.length > 0 && (
              <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                +{newlyMatchedSkills.length} Elevated
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-2 pt-1">
            {matchedSkills.length > 0 ? (
              matchedSkills.map((s) => {
                const isNew = newlyMatchedSkills.includes(s)
                return (
                  <span
                    key={s}
                    className={`text-xs px-2.5 py-1 rounded-lg border font-medium transition-all ${
                      isNew
                        ? 'bg-cyan-500/20 border-cyan-500/40 text-cyan-200'
                        : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    }`}
                  >
                    {s} {isNew && '★'}
                  </span>
                )
              })
            ) : (
              <p className="text-xs text-slate-500">No overlapping skills found in candidate text.</p>
            )}
          </div>
        </div>

        {/* 2. Remaining Missing Required Skills */}
        <div className="p-5 rounded-2xl bg-red-500/[0.04] border border-red-500/20 space-y-3">
          <h4 className="text-sm font-bold text-red-400 flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4" />
            Remaining Missing Required Skills ({missingRequired.length})
          </h4>
          <p className="text-xs text-slate-400">
            These skills were not verified in your original resume and were not hallucinated.
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            {missingRequired.length > 0 ? (
              missingRequired.map((s) => (
                <span
                  key={s}
                  className="text-xs px-2.5 py-1 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 font-medium"
                >
                  {s}
                </span>
              ))
            ) : (
              <p className="text-xs text-emerald-400 font-medium">All required skills identified!</p>
            )}
          </div>
        </div>

        {/* 3. Missing Preferred Skills */}
        {missingPreferred.length > 0 && (
          <div className="p-5 rounded-2xl bg-amber-500/[0.04] border border-amber-500/20 space-y-3">
            <h4 className="text-sm font-bold text-amber-400 flex items-center gap-1.5">
              <HelpCircle className="w-4 h-4" />
              Missing Preferred / Nice-to-Have ({missingPreferred.length})
            </h4>
            <div className="flex flex-wrap gap-2 pt-1">
              {missingPreferred.map((s) => (
                <span
                  key={s}
                  className="text-xs px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 font-medium"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 4. Missing Keywords */}
        {missingKeywords.length > 0 && (
          <div className="p-5 rounded-2xl bg-purple-500/[0.04] border border-purple-500/20 space-y-3">
            <h4 className="text-sm font-bold text-purple-400 flex items-center gap-1.5">
              <Key className="w-4 h-4" />
              Job Description Keywords to Consider ({missingKeywords.length})
            </h4>
            <div className="flex flex-wrap gap-2 pt-1">
              {missingKeywords.map((k) => (
                <span
                  key={k}
                  className="text-xs px-2.5 py-1 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-300 font-medium"
                >
                  {k}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
