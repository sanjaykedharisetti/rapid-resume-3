import { useEffect, useState } from 'react'
import {
  Bar, BarChart, CartesianGrid, Cell, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'

const COLORS = {
  matched: '#10b981',
  missing: '#ef4444',
  preferred: '#f59e0b',
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="card-glass rounded-xl p-3 text-sm shadow-xl">
      <p className="font-semibold text-white mb-1">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: <span className="font-bold">{p.value?.toFixed(1)}</span>
        </p>
      ))}
    </div>
  )
}

/**
 * Bar chart comparing component scores.
 */
export function CategoryScoreChart({ data }) {
  const chartData = [
    { name: 'Semantic', score: data?.semantic_similarity_score ?? 0 },
    { name: 'Skills', score: data?.skill_matching_score ?? 0 },
    { name: 'Qualifications', score: data?.qualification_matching_score ?? 0 },
    { name: 'Experience', score: data?.experience_relevance_score ?? 0 },
  ]

  const getColor = (score) => {
    if (score >= 75) return '#10b981'
    if (score >= 55) return '#3b82f6'
    if (score >= 35) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="score" name="Score" radius={[6, 6, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={index} fill={getColor(entry.score)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

/**
 * Skill matching summary chart.
 */
export function SkillMatchChart({ matched = [], missing = [], preferred = [] }) {
  const data = [
    { name: 'Matched Skills', value: matched.length, fill: COLORS.matched },
    { name: 'Missing Required', value: missing.length, fill: COLORS.missing },
    { name: 'Missing Preferred', value: preferred.length, fill: COLORS.preferred },
  ].filter((d) => d.value > 0)

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-sm">
        No skill data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
        <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 11 }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey="value" name="Count" radius={[0, 6, 6, 0]}>
          {data.map((entry, index) => (
            <Cell key={index} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

/**
 * Radar chart showing multi-dimensional compatibility.
 */
export function CompatibilityRadar({ data }) {
  const radarData = [
    { subject: 'Semantic', value: data?.semantic_similarity_score ?? 0 },
    { subject: 'Skills', value: data?.skill_matching_score ?? 0 },
    { subject: 'Qualifications', value: data?.qualification_matching_score ?? 0 },
    { subject: 'Experience', value: data?.experience_relevance_score ?? 0 },
    { subject: 'Keywords', value: data ? Math.min(100, (1 - (data.missing_keywords?.length || 0) / Math.max(data.important_keywords?.length || 1, 1)) * 100) : 0 },
  ]

  return (
    <ResponsiveContainer width="100%" height={260}>
      <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
        <PolarGrid stroke="rgba(255,255,255,0.08)" />
        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#94a3b8' }} />
        <Radar
          name="Score"
          dataKey="value"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.2}
          strokeWidth={2}
        />
        <Tooltip content={<CustomTooltip />} />
      </RadarChart>
    </ResponsiveContainer>
  )
}
