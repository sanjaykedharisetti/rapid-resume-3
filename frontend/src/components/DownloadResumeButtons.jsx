import { Download, FileText, FileDown, CheckCircle } from 'lucide-react'
import { getOptimizedPdfUrl, getOptimizedReportUrl, getOptimizedDocxUrl } from '../services/api'

export default function DownloadResumeButtons({ analysisId, disabled = false }) {
  if (!analysisId) return null

  return (
    <div className="card-glass rounded-3xl p-6 sm:p-8 space-y-4">
      <div className="border-b border-white/10 pb-4">
        <h3 className="text-xl font-bold text-white flex items-center gap-2">
          <Download className="w-5 h-5 text-emerald-400" />
          Export & Download Documents
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Selectable, ATS-ready formats suitable for applicant tracking systems and direct employer submission.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
        {/* 1. Resume PDF (Primary) */}
        <a
          href={disabled ? '#' : getOptimizedPdfUrl(analysisId)}
          target="_blank"
          rel="noopener noreferrer"
          download
          className={`flex flex-col items-center justify-center p-5 rounded-2xl border text-center transition-all ${
            disabled
              ? 'opacity-40 cursor-not-allowed bg-white/5 border-white/5'
              : 'bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border-emerald-500/30 hover:border-emerald-400 hover:scale-[1.02] shadow-lg shadow-emerald-500/10 text-white'
          }`}
        >
          <FileText className="w-7 h-7 text-emerald-400 mb-2" />
          <span className="text-sm font-bold">Optimized Resume (PDF)</span>
          <span className="text-[11px] text-slate-400 mt-1">Clean single-column ATS format for recruiters</span>
        </a>

        {/* 2. ATS Report PDF */}
        <a
          href={disabled ? '#' : getOptimizedReportUrl(analysisId)}
          target="_blank"
          rel="noopener noreferrer"
          download
          className={`flex flex-col items-center justify-center p-5 rounded-2xl border text-center transition-all ${
            disabled
              ? 'opacity-40 cursor-not-allowed bg-white/5 border-white/5'
              : 'bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border-blue-500/30 hover:border-blue-400 hover:scale-[1.02] shadow-lg shadow-blue-500/10 text-white'
          }`}
        >
          <FileDown className="w-7 h-7 text-blue-400 mb-2" />
          <span className="text-sm font-bold">ATS Analysis Report (PDF)</span>
          <span className="text-[11px] text-slate-400 mt-1">Full score metrics & change summary</span>
        </a>

        {/* 3. Word DOCX */}
        <a
          href={disabled ? '#' : getOptimizedDocxUrl(analysisId)}
          target="_blank"
          rel="noopener noreferrer"
          download
          className={`flex flex-col items-center justify-center p-5 rounded-2xl border text-center transition-all ${
            disabled
              ? 'opacity-40 cursor-not-allowed bg-white/5 border-white/5'
              : 'bg-gradient-to-br from-cyan-500/20 to-sky-500/10 border-cyan-500/30 hover:border-cyan-400 hover:scale-[1.02] shadow-lg shadow-cyan-500/10 text-white'
          }`}
        >
          <Download className="w-7 h-7 text-cyan-400 mb-2" />
          <span className="text-sm font-bold">Editable Resume (DOCX)</span>
          <span className="text-[11px] text-slate-400 mt-1">Customizable Microsoft Word format</span>
        </a>
      </div>
    </div>
  )
}
