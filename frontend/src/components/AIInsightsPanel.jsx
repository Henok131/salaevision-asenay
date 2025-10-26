import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, X, Sparkles, TrendingUp, Heart, Eye, Zap } from 'lucide-react'

const AIInsightsPanel = ({ isOpen, onClose, currentInsight, chartType }) => {
  const [insights, setInsights] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)

  // Generate AI insights based on current data
  const generateInsight = (data, type) => {
    const insights = {
      sales: [
        "Sales performance shows strong upward trajectory with seasonal patterns",
        "Revenue growth correlates with marketing campaign effectiveness",
        "Peak sales periods align with high sentiment scores",
        "Forecast accuracy indicates reliable predictive modeling"
      ],
      sentiment: [
        "Customer sentiment remains consistently positive across campaigns",
        "Emotional engagement drives higher conversion rates",
        "Sentiment spikes correlate with successful product launches",
        "Brand perception shows steady improvement over time"
      ],
      visual: [
        "Bright, vibrant visuals generate higher engagement rates",
        "Color psychology impacts customer purchasing decisions",
        "Visual consistency across campaigns improves brand recognition",
        "Image brightness correlates with campaign success metrics"
      ],
      correlation: [
        "Strong positive correlation between sentiment and sales performance",
        "Visual elements significantly impact customer engagement",
        "Multi-modal analysis reveals hidden performance patterns",
        "Integrated insights provide comprehensive business intelligence"
      ]
    }

    return insights[type]?.[Math.floor(Math.random() * insights[type].length)] || 
           "AI analysis reveals significant patterns in your data"
  }

  // Generate contextual insight based on hover data
  const generateContextualInsight = (data) => {
    if (!data) return "Hover over chart elements to see AI-generated insights"

    const { date, actual, forecast, sentiment, brightness, sales } = data

    if (sales && sentiment && brightness) {
      return `Sales surge of $${sales.toLocaleString()} on ${date} driven by positive sentiment (${(sentiment * 100).toFixed(0)}%) and bright visuals (${brightness.toFixed(0)}% brightness). This combination typically results in 15-25% higher conversion rates.`
    }

    if (actual && forecast) {
      const variance = ((actual - forecast) / forecast * 100).toFixed(1)
      return `Forecast accuracy: ${variance > 0 ? '+' : ''}${variance}% variance. ${variance > 5 ? 'Higher than expected performance suggests strong market conditions.' : 'Performance aligns closely with predictions.'}`
    }

    if (sentiment) {
      const sentimentPercent = (sentiment * 100).toFixed(0)
      return `Sentiment score of ${sentimentPercent}% indicates ${sentiment > 0.7 ? 'highly positive' : sentiment > 0.4 ? 'moderately positive' : 'neutral'} customer engagement. This level typically correlates with ${sentiment > 0.7 ? '15-20%' : '5-10%'} higher retention rates.`
    }

    return "AI analysis reveals significant patterns in your data"
  }

  // Add insight to history
  const addInsight = (insight) => {
    setInsights(prev => [
      {
        id: Date.now(),
        text: insight,
        timestamp: new Date().toLocaleTimeString(),
        type: 'ai'
      },
      ...prev.slice(0, 9) // Keep last 10 insights
    ])
  }

  // Generate insight when data changes
  useEffect(() => {
    if (currentInsight) {
      setIsGenerating(true)
      setTimeout(() => {
        const insight = generateContextualInsight(currentInsight)
        addInsight(insight)
        setIsGenerating(false)
      }, 800) // Simulate AI processing time
    }
  }, [currentInsight])

  // Generate chart summary when panel opens
  useEffect(() => {
    if (isOpen && chartType) {
      const summary = generateInsight(null, chartType)
      addInsight(summary)
    }
  }, [isOpen, chartType])

  const getInsightIcon = (type) => {
    switch (type) {
      case 'sales': return TrendingUp
      case 'sentiment': return Heart
      case 'visual': return Eye
      case 'correlation': return Zap
      default: return Brain
    }
  }

  const InsightIcon = getInsightIcon(chartType)

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Panel */}
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-16 lg:top-0 h-[calc(100vh-4rem)] lg:h-full w-96 bg-dark-card/95 backdrop-blur-xl border-l border-dark-border z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-dark-border">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-accent rounded-lg flex items-center justify-center">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-text-primary">AI Insights</h2>
                  <p className="text-xs text-text-muted">Intelligent Analysis</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-text-secondary" />
              </button>
            </div>

            {/* Current Insight */}
            <div className="p-6 border-b border-dark-border">
              <div className="flex items-center space-x-2 mb-3">
                <InsightIcon className="h-5 w-5 text-accent-from" />
                <span className="text-sm font-medium text-text-primary">Live Analysis</span>
                {isGenerating && (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-4 h-4 border-2 border-accent-from border-t-transparent rounded-full"
                  />
                  )}
              </div>
              
              <motion.div
                key={currentInsight?.date || 'default'}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-glass border border-accent-from/30 rounded-lg p-4"
              >
                <p className="text-sm text-text-primary leading-relaxed">
                  {isGenerating ? (
                    <span className="flex items-center space-x-2">
                      <Sparkles className="h-4 w-4 text-accent-from animate-pulse" />
                      <span>Analyzing data patterns...</span>
                    </span>
                  ) : (
                    generateContextualInsight(currentInsight)
                  )}
                </p>
              </motion.div>
            </div>

            {/* Insight History */}
            <div className="flex-1 overflow-auto p-6">
              <h3 className="text-sm font-medium text-text-primary mb-4">Recent Insights</h3>
              <div className="space-y-3">
                {insights.map((insight) => (
                  <motion.div
                    key={insight.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-dark-hover/50 border border-dark-border rounded-lg p-3"
                  >
                    <div className="flex items-start space-x-2">
                      <div className="w-2 h-2 bg-accent-from rounded-full mt-2 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="text-xs text-text-secondary leading-relaxed">
                          {insight.text}
                        </p>
                        <p className="text-xs text-text-muted mt-1">
                          {insight.timestamp}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-dark-border">
              <div className="flex items-center space-x-2 text-xs text-text-muted">
                <Sparkles className="h-4 w-4 text-accent-from" />
                <span>Powered by SalesVision XAI-360</span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default AIInsightsPanel

