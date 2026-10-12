import { CheckCircle2, AlertCircle, HelpCircle, Sparkles, Wrench, FileCheck } from 'lucide-react'

export default function OptimizationSummary({
  summaryOfChanges = [],
  formattingIssues = [],
  unansweredQuestions = [],
  remainingGaps = [],
}) {
  return (
    <div className="card-glass rounded-3xl p-6 sm:p-8 space-y-6">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-400" />
            Optimization Summary & Transparency Log
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Exact algorithmic modifications applied to enhance readability and ATS compatibility.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Changes Made */}
        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
          <h4 className="text-sm font-bold text-cyan-400 flex items-center gap-1.5">
            <FileCheck className="w-4 h-4" />
            Content & Structural Enhancements ({summaryOfChanges.length})
          </h4>
          <ul className="space-y-2.5 text-xs text-slate-300">
            {summaryOfChanges.map((change, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>{change}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Formatting Issues Addressed */}
        <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4">
          <h4 className="text-sm font-bold text-purple-400 flex items-center gap-1.5">
            <Wrench className="w-4 h-4" />
            Detected Formatting Weaknesses ({formattingIssues.length})
          </h4>
          <ul className="space-y-2.5 text-xs text-slate-300">
            {formattingIssues.map((issue, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <AlertCircle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <span>{issue}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Candidate Questions / Next Steps */}
      {unansweredQuestions.length > 0 && (
        <div className="p-5 rounded-2xl bg-blue-500/10 border border-blue-500/20 space-y-3">
          <h4 className="text-sm font-bold text-blue-300 flex items-center gap-1.5">
            <HelpCircle className="w-4 h-4 text-blue-400" />
            Recommendations Before Final Submission
          </h4>
          <ul className="space-y-2 text-xs text-blue-200/90">
            {unansweredQuestions.map((q, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="font-bold text-blue-400">•</span>
                <span>{q}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
