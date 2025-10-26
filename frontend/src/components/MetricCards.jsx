import { motion } from 'framer-motion'
import { TrendingUp, Heart, Eye, Target, Zap } from 'lucide-react'

const metricCards = [
  {
    id: 'sales',
    title: 'Total Sales',
    value: '$2.4M',
    change: '+8.3%',
    trend: 'up',
    icon: TrendingUp,
    color: 'neon-green',
    insight: 'Sales spike likely due to positive campaign sentiment (+0.76)'
  },
  {
    id: 'sentiment',
    title: 'Sentiment Score',
    value: '0.78',
    change: 'Positive',
    trend: 'up',
    icon: Heart,
    color: 'neon-blue',
    insight: 'Marketing tone shows strong confidence and optimism'
  },
  {
    id: 'brightness',
    title: 'Avg Brightness',
    value: '62%',
    change: '+12%',
    trend: 'up',
    icon: Eye,
    color: 'neon-purple',
    insight: 'Well-lit visuals correlate with higher engagement'
  },
  {
    id: 'accuracy',
    title: 'Forecast Accuracy',
    value: '91%',
    change: '+3.2%',
    trend: 'up',
    icon: Target,
    color: 'neon-blue',
    insight: 'AI predictions align closely with actual performance'
  }
]

export const MetricCards = ({ onCardClick }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {metricCards.map((metric, index) => {
        const Icon = metric.icon
        
        return (
          <motion.div
            key={metric.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ 
              scale: 1.02,
              y: -2,
              transition: { duration: 0.2 }
            }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onCardClick?.(metric.id)}
            className="group relative bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6 cursor-pointer transition-all duration-300 hover:border-accent-from/30 hover:shadow-neon-blue"
          >
            {/* Glow effect on hover */}
            <div className="absolute inset-0 bg-gradient-accent opacity-0 group-hover:opacity-5 rounded-xl transition-opacity duration-300" />
            
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
            <div className={`p-2 rounded-lg bg-${metric.color}/20`}>
                <Icon className={`h-5 w-5 text-${metric.color}`} />
              </div>
              <motion.div
                animate={{ 
                  scale: metric.trend === 'up' ? [1, 1.1, 1] : [1, 0.9, 1],
                  rotate: metric.trend === 'up' ? [0, 5, 0] : [0, -5, 0]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity, 
                  repeatDelay: 3 
                }}
                className={`text-sm font-medium ${
                  metric.trend === 'up' ? 'text-neon-green' : 'text-neon-red'
                }`}
              >
                {metric.change}
              </motion.div>
            </div>

            {/* Value */}
            <div className="mb-2">
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 + 0.2 }}
                className="text-2xl font-bold text-text-primary"
              >
                {metric.value}
              </motion.div>
              <div className="text-sm text-text-secondary">
                {metric.title}
              </div>
            </div>

            {/* Trend indicator */}
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ delay: index * 0.1 + 0.5, duration: 0.8 }}
              className={`h-1 bg-gradient-to-r from-${metric.color} to-transparent rounded-full`}
            />

            {/* Hover insight tooltip */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              whileHover={{ opacity: 1, y: 0 }}
              className="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-dark-card border border-dark-border rounded-lg px-3 py-2 text-xs text-text-primary whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10"
            >
              {metric.insight}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-dark-card" />
            </motion.div>
          </motion.div>
        )
      })}
    </div>
  )
}

