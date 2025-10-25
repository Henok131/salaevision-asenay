import { motion, AnimatePresence } from 'framer-motion'
import { TrendingUp, TrendingDown, AlertTriangle, Star } from 'lucide-react'

const ChartAnnotations = ({ data, chartType, isVisible }) => {
  // Find significant peaks and valleys in the data
  const findSignificantPoints = (data) => {
    if (!data || data.length < 3) return []

    const points = []
    const threshold = 0.15 // 15% change threshold

    for (let i = 1; i < data.length - 1; i++) {
      const prev = data[i - 1]
      const current = data[i]
      const next = data[i + 1]

      // Check for peaks
      if (current.actual > prev.actual * (1 + threshold) && 
          current.actual > next.actual * (1 + threshold)) {
        points.push({
          type: 'peak',
          index: i,
          data: current,
          significance: (current.actual - prev.actual) / prev.actual
        })
      }

      // Check for valleys
      if (current.actual < prev.actual * (1 - threshold) && 
          current.actual < next.actual * (1 - threshold)) {
        points.push({
          type: 'valley',
          index: i,
          data: current,
          significance: (prev.actual - current.actual) / prev.actual
        })
      }
    }

    return points.slice(0, 3) // Limit to 3 annotations
  }

  const significantPoints = findSignificantPoints(data)

  const getAnnotationContent = (point) => {
    const { type, data, significance } = point
    const changePercent = (significance * 100).toFixed(1)
    
    return {
      icon: type === 'peak' ? TrendingUp : TrendingDown,
      color: type === 'peak' ? 'text-neon-green' : 'text-neon-red',
      bgColor: type === 'peak' ? 'bg-neon-green/20' : 'bg-neon-red/20',
      borderColor: type === 'peak' ? 'border-neon-green/30' : 'border-neon-red/30',
      title: type === 'peak' ? 'Sales Peak' : 'Sales Dip',
      value: `$${data.actual?.toLocaleString() || 'N/A'}`,
      change: `${changePercent}%`,
      insight: type === 'peak' 
        ? `Strong performance driven by ${data.sentiment > 0.7 ? 'high sentiment' : 'effective marketing'}`
        : `Performance dip may indicate ${data.sentiment < 0.4 ? 'negative sentiment' : 'market challenges'}`
    }
  }

  const getAnnotationPosition = (index, total) => {
    // Distribute annotations across the chart
    const positions = [
      { top: '20%', left: '15%' },
      { top: '60%', left: '45%' },
      { top: '30%', left: '75%' }
    ]
    return positions[index] || { top: '50%', left: '50%' }
  }

  if (!isVisible || significantPoints.length === 0) return null

  return (
    <div className="absolute inset-0 pointer-events-none">
      <AnimatePresence>
        {significantPoints.map((point, index) => {
          const content = getAnnotationContent(point)
          const position = getAnnotationPosition(index, significantPoints.length)
          const Icon = content.icon

          return (
            <motion.div
              key={`annotation-${point.index}`}
              initial={{ opacity: 0, scale: 0.8, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: -20 }}
              transition={{ delay: index * 0.2, duration: 0.5 }}
              className="absolute transform -translate-x-1/2 -translate-y-full"
              style={position}
            >
              {/* Callout bubble */}
              <motion.div
                whileHover={{ scale: 1.05 }}
                className={`${content.bgColor} ${content.borderColor} border rounded-lg p-3 shadow-lg backdrop-blur-sm min-w-48`}
              >
                {/* Header */}
                <div className="flex items-center space-x-2 mb-2">
                  <Icon className={`h-4 w-4 ${content.color}`} />
                  <span className="text-xs font-medium text-text-primary">
                    {content.title}
                  </span>
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-2 h-2 bg-accent-from rounded-full"
                  />
                </div>

                {/* Metrics */}
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-text-secondary">Value:</span>
                    <span className="text-sm font-bold text-text-primary">
                      {content.value}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-text-secondary">Change:</span>
                    <span className={`text-sm font-semibold ${content.color}`}>
                      {content.change}
                    </span>
                  </div>

                  {data.sentiment && (
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-text-secondary">Sentiment:</span>
                      <span className="text-xs text-text-primary">
                        {(data.sentiment * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}

                  {data.brightness && (
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-text-secondary">Brightness:</span>
                      <span className="text-xs text-text-primary">
                        {data.brightness.toFixed(0)}%
                      </span>
                    </div>
                  )}
                </div>

                {/* Insight */}
                <div className="mt-2 pt-2 border-t border-dark-border">
                  <p className="text-xs text-accent-from leading-relaxed">
                    💡 {content.insight}
                  </p>
                </div>
              </motion.div>

              {/* Arrow pointing to chart */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.2 + 0.3 }}
                className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent"
                style={{ borderTopColor: content.bgColor.replace('bg-', '') }}
              />
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}

export default ChartAnnotations

