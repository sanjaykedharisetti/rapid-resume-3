import { Link } from 'react-router-dom'
import {
  Brain, Cpu, Database, FileText, CheckCircle2, AlertTriangle,
  Layers, ArrowRight, ShieldCheck, Sparkles, BookOpen, GitBranch
} from 'lucide-react'

export default function AboutPage() {
  const steps = [
    {
      num: '01',
      title: 'Document Ingestion & Text Parsing',
      desc: 'Resumes in PDF or DOCX format are parsed using PyMuPDF (fitz) and python-docx. Raw text is normalized, stripped of artifacts, and segmented into sections (Skills, Experience, Education).',
      icon: FileText,
      color: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400'
    },
    {
      num: '02',
      title: 'Dense Semantic Vectorization',
      desc: 'Using the sentence-transformers all-MiniLM-L6-v2 transformer model, 384-dimensional dense semantic embeddings are computed for both the resume and the job description to capture contextual intent beyond exact words.',
      icon: Brain,
      color: 'from-purple-500/20 to-pink-500/20 border-purple-500/30 text-purple-400'
    },
    {
      num: '03',
      title: 'Skills & Entity Extraction',
      desc: 'A curated technical and domain taxonomy (1,000+ skills) runs lexical boundary pattern matching to identify exact matched skills, missing mandatory skills, and qualification indicators.',
      icon: Cpu,
      color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30 text-emerald-400'
    },
    {
      num: '04',
      title: 'Composite Weighted Scoring',
      desc: 'Scores are mathematically weighted across 4 key dimensions: Semantic Alignment (40%), Technical Skills (35%), Qualifications & Experience (15%), and Keyword Density (10%).',
      icon: Layers,
      color: 'from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-400'
    }
  ]

  const weights = [
    { label: 'Semantic Similarity', weight: '40%', desc: 'Sentence-BERT cosine similarity', color: 'bg-indigo-500' },
    { label: 'Technical Skills Match', weight: '35%', desc: 'Jaccard & overlap of explicit skills', color: 'bg-cyan-500' },
    { label: 'Experience & Qualifications', weight: '15%', desc: 'Degree & seniority requirements', color: 'bg-emerald-500' },
    { label: 'Keyword Overlap', weight: '10%', desc: 'TF-IDF n-gram lexical density', color: 'bg-amber-500' }
  ]

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-16">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold tracking-wider uppercase">
            <Sparkles className="w-3.5 h-3.5" />
            Methodology & Technology
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
            How Matchly Works
          </h1>
          <p className="max-w-2xl mx-auto text-slate-400 text-base sm:text-lg">
            A production-ready NLP matching engine designed to help candidates optimize their resumes and understand recruitment algorithms.
          </p>
        </div>

        {/* Pipeline Steps */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <GitBranch className="w-6 h-6 text-cyan-400" />
            4-Stage Matching Pipeline
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {steps.map((s) => {
              const Icon = s.icon
              return (
                <div
                  key={s.num}
                  className={`p-6 rounded-2xl border bg-gradient-to-br ${s.color} backdrop-blur-md transition-all hover:scale-[1.01]`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-md bg-white/10 text-white">
                      Stage {s.num}
                    </span>
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{s.title}</h3>
                  <p className="text-sm text-slate-300 leading-relaxed">{s.desc}</p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Scoring Breakdown */}
        <div className="p-8 rounded-2xl bg-white/[0.03] border border-white/10 space-y-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Layers className="w-6 h-6 text-purple-400" />
            Scoring Formula & Weights
          </h2>
          <p className="text-sm text-slate-400">
            Unlike basic keyword counters, Matchly prevents keyword-stuffing by blending deep contextual sentence embeddings with explicit skill extraction.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {weights.map((w) => (
              <div key={w.label} className="p-4 rounded-xl bg-black/30 border border-white/5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">{w.label}</span>
                  <span className="text-sm font-bold text-cyan-400">{w.weight}</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                  <div className={`h-full rounded-full ${w.color}`} style={{ width: w.weight }} />
                </div>
                <p className="text-[11px] text-slate-500">{w.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Technology Stack Grid */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-6 h-6 text-emerald-400" />
            Technology Architecture
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/10 space-y-3">
              <h3 className="font-semibold text-cyan-400 text-sm uppercase tracking-wider">Frontend</h3>
              <ul className="text-sm text-slate-300 space-y-2">
                <li>• React 18 & Vite</li>
                <li>• Tailwind CSS & Glassmorphism</li>
                <li>• Recharts (Radar & Bar Visuals)</li>
                <li>• Lucide React Icons</li>
                <li>• Axios HTTP Client</li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/10 space-y-3">
              <h3 className="font-semibold text-purple-400 text-sm uppercase tracking-wider">Backend API</h3>
              <ul className="text-sm text-slate-300 space-y-2">
                <li>• FastAPI (Python Async)</li>
                <li>• SQLAlchemy + SQLite/PostgreSQL</li>
                <li>• PyMuPDF (PDF Parser)</li>
                <li>• python-docx (DOCX Parser)</li>
                <li>• ReportLab (PDF Generator)</li>
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/10 space-y-3">
              <h3 className="font-semibold text-emerald-400 text-sm uppercase tracking-wider">NLP Engine</h3>
              <ul className="text-sm text-slate-300 space-y-2">
                <li>• Sentence-Transformers</li>
                <li>• all-MiniLM-L6-v2 (Dense Vectors)</li>
                <li>• Scikit-learn (TF-IDF & Cosine)</li>
                <li>• spaCy (Tokenization & NER)</li>
                <li>• Custom 1,000+ Skills Lexicon</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Methodology & Disclaimer */}
        <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-4">
          <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1 text-sm">
            <h4 className="font-bold text-amber-200">Algorithmic Transparency & Limitations</h4>
            <p className="text-amber-300/80 leading-relaxed">
              Matchly provides automated heuristic guidance based on text comparison. Matching scores do not guarantee interview invites or hiring outcomes. Scores are intended to highlight missing keywords, gaps, and areas for improvement.
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center pt-4">
          <Link
            to="/matcher"
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl font-bold bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25 transition-all transform hover:-translate-y-0.5"
          >
            Launch Resume Analyzer
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  )
}
