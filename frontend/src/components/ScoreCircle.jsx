import { useEffect, useRef, useState } from 'react'
import { getScoreStrokeColor } from '../utils/helpers'

/**
 * Animated circular progress indicator for the overall score.
 * Uses SVG with a stroke-dashoffset animation driven by a useEffect count-up.
 */
export default function ScoreCircle({ score = 0, size = 200 }) {
  const [displayScore, setDisplayScore] = useState(0)
  const [mounted, setMounted] = useState(false)
  const animRef = useRef(null)

  const radius = size * 0.38
  const circumference = 2 * Math.PI * radius
  const strokeColor = getScoreStrokeColor(score)

  useEffect(() => {
    setMounted(true)
    const duration = 1400
    const start = performance.now()
    const startScore = 0

    const animate = (now) => {
      const elapsed = now - start
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplayScore(Math.round(startScore + eased * score))
      if (progress < 1) {
        animRef.current = requestAnimationFrame(animate)
      }
    }

    animRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animRef.current)
  }, [score])

  const dashOffset = circumference - (displayScore / 100) * circumference

  return (
    <div
      className="score-circle flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="absolute"
        style={{ transform: 'rotate(-90deg)' }}
      >
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={size * 0.075}
        />
        {/* Progress arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth={size * 0.075}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={mounted ? dashOffset : circumference}
          style={{ transition: 'stroke-dashoffset 0.05s linear' }}
          filter="url(#glow)"
        />
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      </svg>

      {/* Center content */}
      <div className="relative z-10 flex flex-col items-center justify-center">
        <span
          className="font-black tabular-nums leading-none"
          style={{ fontSize: size * 0.22, color: strokeColor }}
        >
          {displayScore}
        </span>
        <span className="text-slate-400 font-medium" style={{ fontSize: size * 0.08 }}>
          out of 100
        </span>
      </div>
    </div>
  )
}
