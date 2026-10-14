import { Link } from 'react-router-dom'
import {
  ArrowRight, Brain, ChevronRight, Code2, Database, FileSearch,
  Layers, Rocket, Shield, Sparkles, Target, TrendingUp, Zap
} from 'lucide-react'

const features = [
  {
    icon: Brain,
    color: 'from-blue-500 to-cyan-500',
    title: 'Advanced Analysis',
    desc: 'Uses Sentence-BERT embeddings and TF-IDF to measure real semantic similarity between your resume and job requirements.',
  },
  {
    icon: Target,
    color: 'from-violet-500 to-purple-600',
    title: 'Skill Gap Detection',
    desc: 'Identifies exactly which skills are matched, missing, or preferred — so you know precisely what to work on.',
  },
  {
    icon: TrendingUp,
    color: 'from-emerald-500 to-teal-500',
    title: 'Actionable Suggestions',
    desc: 'Get honest, data-driven improvement suggestions based on actual differences — never fabricated claims.',
  },
  {
    icon: FileSearch,
    color: 'from-orange-500 to-amber-500',
    title: 'Universal Format Support',
    desc: 'Upload any resume format: PDF, Word (DOCX/DOC), TXT, RTF, ODT, HTML, Markdown, and more. Clean text is instantly extracted.',
  },
  {
    icon: Shield,
    color: 'from-red-500 to-pink-500',
    title: 'Privacy First',
    desc: 'Resume files are processed in memory and deleted immediately. Only analysis metadata is stored.',
  },
  {
    icon: Database,
    color: 'from-slate-400 to-slate-600',
    title: 'Analysis History',
    desc: 'Review and compare your previous analyses. Track your improvement over multiple job applications.',
  },
]

const steps = [
  { n: '01', title: 'Upload Your Resume', desc: 'Drag & drop or click to upload your resume file in any format.' },

  { n: '02', title: 'Paste Job Description', desc: 'Copy the complete job description from any job board or company website.' },
  { n: '03', title: 'Click Analyze', desc: 'Our NLP pipeline processes both documents and computes a compatibility score.' },
  { n: '04', title: 'Review & Improve', desc: 'Study matched skills, gaps, and suggestions. Download your PDF report.' },
]

const techStack = [
  { icon: Code2, name: 'React + Vite', desc: 'Fast modern frontend' },
  { icon: Rocket, name: 'FastAPI', desc: 'High-performance backend' },
  { icon: Brain, name: 'Sentence-BERT', desc: 'Semantic similarity' },
  { icon: Layers, name: 'scikit-learn', desc: 'TF-IDF & scoring' },
  { icon: Sparkles, name: 'spaCy', desc: 'NLP processing' },
  { icon: Database, name: 'SQLite/PostgreSQL', desc: 'Data persistence' },
]

export default function HomePage() {
  return (
    <div className="gradient-bg-hero">
      {/* ── Hero ─────────────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden">
        {/* Background blobs */}
        <div className="absolute top-0 left-1/4 w-96 h-96 rounded-full bg-blue-600/10 blur-3xl pointer-events-none" />
        <div className="absolute top-1/4 right-1/4 w-80 h-80 rounded-full bg-violet-600/10 blur-3xl pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-28 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm font-medium mb-8 animate-fade-in">
            <Zap size={13} className="text-blue-400" />
            Advanced Resume Analysis · NLP + Matching Engine
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white leading-tight mb-6 animate-slide-up">
            Find Out How Well Your{' '}
            <span className="gradient-text">Resume Matches</span>{' '}
            Your Dream Job
          </h1>

          <p className="max-w-2xl mx-auto text-lg text-slate-400 leading-relaxed mb-10 animate-slide-up animation-delay-100">
            Upload your resume, paste a job description, and discover your compatibility score with
            detailed resume analysis — including skill gaps, qualification insights, and actionable improvement suggestions.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up animation-delay-200">
            <Link
              to="/matcher"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-bold text-lg btn-glow hover:scale-105 transition-transform"
              id="start-matching-btn"
            >
              Start Matching
              <ArrowRight size={20} />
            </Link>
            <Link
              to="/about"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-white/5 border border-white/10 text-slate-300 font-semibold text-lg hover:bg-white/10 transition-colors"
            >
              How it works
              <ChevronRight size={18} />
            </Link>
          </div>

          {/* Score preview pills */}
          <div className="mt-14 flex flex-wrap items-center justify-center gap-3 animate-fade-in animation-delay-400">
            {[
              { label: 'Strong Match', range: '75–100', color: 'emerald' },
              { label: 'Good Match',   range: '55–74',  color: 'blue' },
              { label: 'Moderate',     range: '35–54',  color: 'amber' },
              { label: 'Low Match',    range: '0–34',   color: 'red' },
            ].map(({ label, range, color }) => (
              <div
                key={label}
                className={`px-4 py-2 rounded-full border text-sm font-medium
                  bg-${color}-500/10 border-${color}-500/20 text-${color}-300`}
              >
                {label} <span className="opacity-60">({range})</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold text-white mb-3">Everything You Need to Stand Out</h2>
          <p className="text-slate-400 max-w-xl mx-auto">
            A complete resume intelligence platform built with production-grade NLP.
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, color, title, desc }) => (
            <div key={title} className="card-glass rounded-2xl p-6 feature-card">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-5 shadow-lg`}>
                <Icon size={22} className="text-white" />
              </div>
              <h3 className="text-white font-bold text-lg mb-2">{title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ─────────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold text-white mb-3">How It Works</h2>
          <p className="text-slate-400">Four simple steps to resume clarity.</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map(({ n, title, desc }, idx) => (
            <div key={n} className="relative card-glass rounded-2xl p-6 feature-card text-center">
              {idx < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                  <ChevronRight size={20} className="text-slate-600" />
                </div>
              )}
              <div className="text-5xl font-black gradient-text mb-4 leading-none">{n}</div>
              <h3 className="text-white font-bold mb-2">{title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Tech stack ───────────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-3">Built with Industry-Grade Tech</h2>
          <p className="text-slate-400">Modern, scalable, and production-ready.</p>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {techStack.map(({ icon: Icon, name, desc }) => (
            <div key={name} className="card-glass rounded-2xl p-5 text-center feature-card">
              <Icon size={24} className="mx-auto text-blue-400 mb-3" />
              <p className="text-white font-semibold text-sm">{name}</p>
              <p className="text-slate-500 text-xs mt-1">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA Banner ───────────────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
        <div className="rounded-3xl bg-gradient-to-r from-blue-600/20 to-violet-600/20 border border-blue-500/20 p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to find your match score?</h2>
          <p className="text-slate-400 mb-8 max-w-lg mx-auto">
            Upload your resume and paste any job description to get started in seconds.
          </p>
          <Link
            to="/matcher"
            className="inline-flex items-center gap-2 px-10 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-violet-600 text-white font-bold text-lg btn-glow"
            id="cta-start-btn"
          >
            Analyze My Resume
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>
    </div>
  )
}
