import { Link } from 'react-router-dom'
import { Brain, Github, Linkedin, Zap } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-[#080d1a] mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                <Brain size={16} className="text-white" />
              </div>
              <span className="font-bold text-white">Matchly</span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              Intelligent resume analysis to help you land your dream job. 
              Built with NLP and modern web technologies.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider">Navigation</h4>
            <ul className="space-y-2">
              {[
                { to: '/', label: 'Home' },
                { to: '/matcher', label: 'Resume Analyzer' },
                { to: '/history', label: 'Analysis History' },
                { to: '/about', label: 'About' },
              ].map(({ to, label }) => (
                <li key={to}>
                  <Link to={to} className="text-sm text-slate-400 hover:text-blue-400 transition-colors">
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Tech stack */}
          <div>
            <h4 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider">Powered By</h4>
            <div className="flex flex-wrap gap-2">
              {['FastAPI', 'React', 'Sentence-BERT', 'scikit-learn', 'spaCy', 'SQLite'].map((tech) => (
                <span
                  key={tech}
                  className="text-xs px-2 py-1 rounded-md bg-white/5 text-slate-400 border border-white/5"
                >
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-500">
            © {new Date().getFullYear()} Matchly. This tool provides an estimate of resume-to-job compatibility, not a hiring guarantee.
          </p>
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <Zap size={12} className="text-blue-500" />
            <span>Fast & Secure</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
