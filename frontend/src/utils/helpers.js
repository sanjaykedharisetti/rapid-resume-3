/**
 * Utility helpers for formatting and display.
 */

/** Format bytes to human-readable string */
export function formatBytes(bytes, decimals = 1) {
  if (!bytes) return '0 B'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

/** Format date string to locale string */
export function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Get color class for a score */
export function getScoreColor(score) {
  if (score >= 75) return 'text-emerald-400'
  if (score >= 55) return 'text-blue-400'
  if (score >= 35) return 'text-amber-400'
  return 'text-red-400'
}

/** Get badge color classes for match category */
export function getCategoryBadge(category) {
  const map = {
    'Strong Match': 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    'Good Match':   'bg-blue-500/20 text-blue-300 border border-blue-500/30',
    'Moderate Match': 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
    'Low Match':    'bg-red-500/20 text-red-300 border border-red-500/30',
  }
  return map[category] || 'bg-slate-500/20 text-slate-300 border border-slate-500/30'
}

/** Get stroke color for circular score SVG */
export function getScoreStrokeColor(score) {
  if (score >= 75) return '#10b981' // emerald
  if (score >= 55) return '#3b82f6' // blue
  if (score >= 35) return '#f59e0b' // amber
  return '#ef4444' // red
}

/** Clamp a number */
export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

/** Safe array accessor — returns [] if value is null/undefined */
export function safeArray(val) {
  return Array.isArray(val) ? val : []
}

/** Safe number — returns 0 if value is null/undefined/NaN */
export function safeNumber(val, fallback = 0) {
  const n = Number(val)
  return isNaN(n) ? fallback : n
}
