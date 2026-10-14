import { useState, useEffect } from 'react'
import { Brain, CheckCircle2, Cpu, FileSearch, FileText, Loader2, Sparkles } from 'lucide-react'

const STAGES = [
  { label: 'Analyzing original resume', icon: FileSearch, desc: 'Extracting sections, contact info, and current skill baseline' },
  { label: 'Identifying relevant skills', icon: Cpu, desc: 'Cross-referencing technical taxonomy with job requirements' },
  { label: 'Improving resume content', icon: Sparkles, desc: 'Enhancing action verbs, normalizing terminology, structuring layout' },
  { label: 'Checking ATS compatibility', icon: Brain, desc: 'Running iterative scoring loops across semantic, skill, and qualification weights' },
  { label: 'Generating optimized documents', icon: FileText, desc: 'Assembling clean single-column PDF and editable DOCX formats' },
]

export default function OptimizationProgress({ isRunning }) {
  const [currentStage, setCurrentStage] = useState(0)

  useEffect(() => {
    if (!isRunning) {
      setCurrentStage(0)
      return
    }

    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev))
    }, 350)

    return () => clearInterval(interval)
  }, [isRunning])

  if (!isRunning) return null

  return (
    <div className="card-glass rounded-3xl p-8 border border-cyan-500/30 bg-gradient-to-br from-cyan-950/20 via-slate-900/40 to-blue-950/20 space-y-6 animate-scale-in">
      <div className="flex items-center gap-3">
        <Loader2 className="w-6 h-6 text-cyan-400 spinner" />
        <h3 className="text-xl font-bold text-white">AI Optimization in Progress</h3>
      </div>
      <p className="text-sm text-slate-400">
        Executing algorithmic enhancement without hallucinating unearned skills or qualifications.
      </p>

      <div className="space-y-4">
        {STAGES.map((s, idx) => {
          const Icon = s.icon
          const isDone = idx < currentStage
          const isCurrent = idx === currentStage

          return (
            <div
              key={s.label}
              className={`flex items-start gap-4 p-4 rounded-2xl transition-all ${
                isCurrent
                  ? 'bg-cyan-500/10 border border-cyan-500/30'
                  : isDone
                  ? 'bg-emerald-500/5 border border-emerald-500/20 text-slate-400'
                  : 'opacity-40 border border-transparent'
              }`}
            >
              <div className="mt-0.5">
                {isDone ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-cyan-400 spinner" />
                ) : (
                  <Icon className="w-5 h-5 text-slate-500" />
                )}
              </div>
              <div>
                <p className={`text-sm font-bold ${isCurrent ? 'text-white' : isDone ? 'text-slate-300' : 'text-slate-400'}`}>
                  {s.label}
                </p>
                <p className="text-xs text-slate-400 mt-0.5">{s.desc}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
