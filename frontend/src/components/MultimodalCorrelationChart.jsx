import { useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell
} from 'recharts'

// Map variance [0..1+] to a neon blue -> purple -> pink gradient
function interpolateColor(color1, color2, t) {
  const c1 = {
    r: parseInt(color1.slice(1, 3), 16),
    g: parseInt(color1.slice(3, 5), 16),
    b: parseInt(color1.slice(5, 7), 16),
  }
  const c2 = {
    r: parseInt(color2.slice(1, 3), 16),
    g: parseInt(color2.slice(3, 5), 16),
    b: parseInt(color2.slice(5, 7), 16),
  }
  const r = Math.round(c1.r + (c2.r - c1.r) * t)
  const g = Math.round(c1.g + (c2.g - c1.g) * t)
  const b = Math.round(c1.b + (c2.b - c1.b) * t)
  return `#${r.toString(16).padStart(2, '0')}${g
    .toString(16)
    .padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
}

function getVarianceColor(varianceRaw) {
  const low = '#78c8ff' // neon blue used in other charts
  const mid = '#b084ff' // purple used in other charts
  const high = '#ff7ad9' // pink accent

  const v = Math.min(1, Math.max(0, Math.abs(Number(varianceRaw) || 0)))
  if (v <= 0.5) {
    const t = v / 0.5
    return interpolateColor(low, mid, t)
  } else {
    const t = (v - 0.5) / 0.5
    return interpolateColor(mid, high, t)
  }
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null
  const p = payload[0].payload
  const sentimentPercent = (p.sentiment * 100).toFixed(0)
  const brightnessPercent = (p.brightness ?? 0).toFixed(0)
  const variancePercent = Math.round(Math.abs((p.variance ?? 0) * 100))

  const descriptor = (() => {
    const sHigh = p.sentiment >= 0.8
    const bHigh = (p.brightness ?? 0) >= 70
    if (sHigh && bHigh) return 'Positive sentiment and high brightness → higher sales'
    if (sHigh) return 'Positive sentiment → uplift in sales'
    if (bHigh) return 'Bright visuals → increased engagement'
    return 'Neutral conditions'
  })()

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-dark-card border border-accent-from/30 rounded-lg p-4 shadow-neon-blue"
    >
      <div className="text-text-primary font-medium mb-2">Multimodal datapoint</div>
      <div className="text-text-secondary text-sm space-y-1">
        <div>Sentiment: {sentimentPercent}%</div>
        <div>Brightness: {brightnessPercent}%</div>
        <div>Sales: ${Math.round(p.sales || 0).toLocaleString()}</div>
        <div>Forecast variance: {variancePercent}%</div>
      </div>
      <div className="mt-2 pt-2 border-t border-dark-border text-xs text-accent-from">
        💡 {descriptor}
      </div>
    </motion.div>
  )
}

// Custom dot with hover pulse/scale
const DotShape = (props) => {
  const { cx, cy, size, payload } = props
  const r = Math.max(6, Math.sqrt(size || 64))
  const fill = getVarianceColor(payload?.variance)

  return (
    <motion.circle
      cx={cx}
      cy={cy}
      r={r}
      fill={fill}
      initial={{ scale: 1, filter: 'drop-shadow(0 0 0px rgba(120,200,255,0))' }}
      whileHover={{ scale: 1.2, filter: 'drop-shadow(0 0 8px rgba(120,200,255,0.8))' }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    />
  )
}

export const MultimodalCorrelationChart = ({ data = [] }) => {
  const prepared = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) return []
    return data
      .map(d => ({
        sentiment: Number(d.sentiment ?? 0),
        brightness: Number(d.brightness ?? 0),
        sales: Number(d.sales ?? 0),
        variance: Number(d.variance ?? 0),
      }))
      .filter(d => !Number.isNaN(d.sentiment) && !Number.isNaN(d.brightness))
  }, [data])

  const sizeDomain = useMemo(() => {
    if (prepared.length === 0) return [0, 1]
    const values = prepared.map(d => d.sales)
    const min = Math.min(...values)
    const max = Math.max(...values)
    return [min || 0, max || 1]
  }, [prepared])

  const insightSummary = useMemo(() => {
    if (prepared.length === 0) return 'No data available to summarize.'
    const top = prepared.reduce((a, b) => (a.sales > b.sales ? a : b))
    // Heuristic thresholds
    const bright = top.brightness >= 70
    const pos = top.sentiment >= 0.8
    const segCount = prepared.filter(p => p.brightness >= 70 && p.sentiment >= 0.8).length
    const segText = segCount > 1 ? `${segCount} points also align` : 'This pattern recurs across samples'
    return `Highest sales observed at brightness ${bright ? '>' : '<='} 70 and sentiment ${pos ? '>' : '<='} 0.8. ${segText}.`
  }, [prepared])

  // Linear regression y = a*x + b for brightness vs sentiment
  const regression = useMemo(() => {
    if (prepared.length < 2) return null
    const n = prepared.length
    const sumX = prepared.reduce((s, d) => s + d.sentiment, 0)
    const sumY = prepared.reduce((s, d) => s + d.brightness, 0)
    const sumXY = prepared.reduce((s, d) => s + d.sentiment * d.brightness, 0)
    const sumXX = prepared.reduce((s, d) => s + d.sentiment * d.sentiment, 0)
    const denom = n * sumXX - sumX * sumX
    if (denom === 0) return null
    const a = (n * sumXY - sumX * sumY) / denom
    const b = (sumY - a * sumX) / n
    return { a, b }
  }, [prepared])

  const regPoints = useMemo(() => {
    if (!regression) return []
    const clamp = (y) => Math.max(0, Math.min(100, y))
    const y0 = clamp(regression.a * 0 + regression.b)
    const y1 = clamp(regression.a * 1 + regression.b)
    return [
      { sentiment: 0, brightness: y0 },
      { sentiment: 1, brightness: y1 },
    ]
  }, [regression])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6 shadow-neon-blue"
      id="multimodal-corr-chart"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-text-primary mb-2">
          Multimodal Correlation — Sentiment × Brightness × Sales
        </h3>
        <p className="text-sm text-text-secondary">
          Each bubble represents a combined datapoint: the X-axis shows customer sentiment, the Y-axis shows
          visual brightness, bubble size encodes sales amount, and bubble color reflects forecast variance
          (blue = low variance/accurate, purple = moderate, pink = high variance/less certain).
        </p>
      </div>

      <div className="w-full">
        <ResponsiveContainer width="100%" height={360}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
            <XAxis
              type="number"
              dataKey="sentiment"
              name="Sentiment"
              domain={[0, 1]}
              tickFormatter={(v) => `${Math.round(v * 100)}%`}
              stroke="#8a9ba8"
              fontSize={12}
              label={{ value: 'Sentiment', position: 'insideBottomRight', offset: -5, fill: '#8a9ba8' }}
            />
            <YAxis
              type="number"
              dataKey="brightness"
              name="Brightness"
              domain={[0, 100]}
              tickFormatter={(v) => `${Math.round(v)}%`}
              stroke="#8a9ba8"
              fontSize={12}
              label={{ value: 'Brightness', angle: -90, position: 'insideLeft', fill: '#8a9ba8' }}
            />
            <ZAxis dataKey="sales" range={[60, 360]} domain={sizeDomain} name="Sales" />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#394867', strokeDasharray: '3 3' }} />
            <Legend />
            <Scatter data={prepared} shape={<DotShape />} isAnimationActive animationDuration={600}>
              {prepared.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getVarianceColor(entry.variance)} />
              ))}
            </Scatter>
            {regPoints.length === 2 && (
              <Scatter
                data={regPoints}
                line={{ stroke: '#4ade80', strokeWidth: 2, strokeDasharray: '6 4' }}
                shape={() => null}
              />
            )}
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 p-4 bg-gradient-glass border border-accent-from/30 rounded-lg">
        <p className="text-sm text-text-primary">
          {insightSummary}
        </p>
      </div>
    </motion.div>
  )
}

export default MultimodalCorrelationChart
