import { useState } from 'react'
import { Check, Copy, FileText, Sparkles, Eye } from 'lucide-react'

export default function ResumePreview({
  originalText,
  optimizedText,
  originalScore,
  optimizedScore,
  originalSections = {},
  optimizedSections = {},
}) {
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState('full') // 'full' or 'sections'

  const handleCopy = () => {
    navigator.clipboard.writeText(optimizedText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Top Toggle & Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Eye className="w-5 h-5 text-cyan-400" />
            Side-by-Side Content Comparison
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Compare original text against the ATS-enhanced structure in real time.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-white/5 border border-white/10 rounded-xl p-1 flex text-xs">
            <button
              onClick={() => setActiveTab('full')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === 'full' ? 'bg-cyan-500 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Full Text View
            </button>
            <button
              onClick={() => setActiveTab('sections')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeTab === 'sections' ? 'bg-cyan-500 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              Section Breakdown
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 border border-white/10 text-slate-300 hover:text-white text-xs font-medium transition-all"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? 'Copied!' : 'Copy Text'}
          </button>
        </div>
      </div>

      {/* Side-by-side Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* LEFT CARD: Original Resume */}
        <div className="card-glass rounded-2xl p-6 border border-white/10 flex flex-col space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-slate-400" />
              <h4 className="font-bold text-slate-200 text-sm uppercase tracking-wider">Original Resume</h4>
            </div>
            <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-md bg-white/10 text-slate-300">
              Score: {originalScore}%
            </span>
          </div>

          <div className="flex-1 overflow-y-auto max-h-[550px] custom-scrollbar pr-2 space-y-4 font-mono text-xs leading-relaxed text-slate-400">
            {activeTab === 'full' ? (
              <pre className="whitespace-pre-wrap font-sans text-slate-300">
                {originalText || 'No original resume text available.'}
              </pre>
            ) : (
              <div className="space-y-4 font-sans">
                {Object.entries(originalSections).map(([sec, txt]) => (
                  <div key={sec} className="p-3 rounded-xl bg-white/[0.02] border border-white/5 space-y-1">
                    <p className="text-xs font-bold text-slate-300 uppercase">{sec}</p>
                    <p className="text-xs text-slate-400 whitespace-pre-wrap">{txt}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT CARD: Optimized Resume */}
        <div className="card-glass rounded-2xl p-6 border border-cyan-500/30 bg-cyan-950/10 flex flex-col space-y-4">
          <div className="flex items-center justify-between border-b border-cyan-500/20 pb-4">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
              <h4 className="font-bold text-white text-sm uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                ATS-Optimized Resume
              </h4>
            </div>
            <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Score: {optimizedScore}%
            </span>
          </div>

          <div className="flex-1 overflow-y-auto max-h-[550px] custom-scrollbar pr-2 space-y-4 font-mono text-xs leading-relaxed text-slate-200">
            {activeTab === 'full' ? (
              <pre className="whitespace-pre-wrap font-sans text-slate-100 selection:bg-cyan-500/30">
                {optimizedText || 'Optimized text will appear here.'}
              </pre>
            ) : (
              <div className="space-y-4 font-sans">
                {Object.entries(optimizedSections).map(([sec, txt]) => (
                  <div key={sec} className="p-3 rounded-xl bg-cyan-500/5 border border-cyan-500/20 space-y-1">
                    <p className="text-xs font-bold text-cyan-300 uppercase">{sec}</p>
                    <p className="text-xs text-slate-200 whitespace-pre-wrap">{txt}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
