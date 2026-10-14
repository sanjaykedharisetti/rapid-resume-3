import { useCallback, useRef, useState } from 'react'
import { File, FileText, Trash2, Upload, X } from 'lucide-react'
import { formatBytes } from '../utils/helpers'

const ACCEPTED = '.pdf,.docx,.doc,.txt,.text,.rtf,.odt,.html,.htm,.md,.markdown,.pages,.png,.jpg,.jpeg,.webp,*'
const MAX_SIZE_MB = 10

export default function DropZone({ file, onFileChange, onFileRemove, error }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  const validate = (f) => {
    if (!f) return 'No file selected.'
    if (f.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File is too large (${formatBytes(f.size)}). Maximum size is ${MAX_SIZE_MB} MB.`
    }
    return null
  }

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault()
      setDragging(false)
      const dropped = e.dataTransfer.files[0]
      if (dropped) {
        const err = validate(dropped)
        onFileChange(dropped, err)
      }
    },
    [onFileChange]
  )

  const handleChange = (e) => {
    const selected = e.target.files?.[0]
    if (selected) {
      const err = validate(selected)
      onFileChange(selected, err)
    }
  }

  const getFileIcon = (fileName) => {
    const ext = fileName?.split('.').pop()?.toLowerCase() || ''
    if (ext === 'pdf') return <FileText size={22} className="text-red-400" />
    if (['docx', 'doc'].includes(ext)) return <File size={22} className="text-blue-400" />
    if (['txt', 'rtf', 'odt', 'md', 'html', 'htm'].includes(ext)) return <FileText size={22} className="text-emerald-400" />
    return <File size={22} className="text-cyan-400" />
  }

  if (file) {
    return (
      <div className="card-glass rounded-2xl p-6 border border-emerald-500/20 bg-emerald-500/5 animate-scale-in">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
            {getFileIcon(file.name)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-white font-semibold truncate">{file.name}</p>
            <p className="text-slate-400 text-sm mt-0.5">{formatBytes(file.size)}</p>
            <div className="flex items-center gap-2 mt-3">
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/20">
                ✓ Ready to analyze
              </span>
            </div>
          </div>
          <button
            onClick={onFileRemove}
            className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors flex-shrink-0"
            title="Remove file"
          >
            <Trash2 size={16} />
          </button>
        </div>
        <button
          onClick={() => inputRef.current?.click()}
          className="mt-4 w-full py-2 rounded-xl border border-white/10 text-slate-400 text-sm hover:text-white hover:border-white/20 transition-all"
        >
          Replace file
        </button>
        <input ref={inputRef} type="file" accept={ACCEPTED} className="hidden" onChange={handleChange} />
      </div>
    )
  }

  return (
    <div>
      <div
        className={`drop-zone rounded-2xl p-10 text-center cursor-pointer transition-all ${dragging ? 'drag-over' : ''} ${error ? 'border-red-500/50 bg-red-500/5' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        aria-label="Upload resume file"
      >
        <div className={`mx-auto w-16 h-16 rounded-2xl flex items-center justify-center mb-4 transition-all ${dragging ? 'bg-blue-500/20 scale-110' : 'bg-white/5'}`}>
          <Upload size={28} className={dragging ? 'text-blue-400' : 'text-slate-500'} />
        </div>
        <p className="text-white font-semibold mb-1">
          {dragging ? 'Drop your resume here' : 'Drag & drop your resume'}
        </p>
        <p className="text-slate-400 text-sm mb-3">or click to browse any resume file</p>
        <div className="flex items-center justify-center flex-wrap gap-2 text-xs text-slate-400">
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-slate-300">PDF</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-slate-300">Word (DOCX/DOC)</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-slate-300">TXT / RTF</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-slate-300">ODT / HTML / MD</span>
          <span className="text-slate-500 font-mono">Max {MAX_SIZE_MB} MB</span>
        </div>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        className="hidden"
        onChange={handleChange}
        id="resume-upload"
      />
      {error && (
        <div className="mt-3 flex items-center gap-2 text-red-400 text-sm animate-fade-in">
          <X size={14} />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
