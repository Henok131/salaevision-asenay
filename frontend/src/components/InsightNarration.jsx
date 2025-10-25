import { motion } from 'framer-motion'
import { Brain, TrendingUp, Heart, Eye, GitBranch } from 'lucide-react'

const InsightNarration = ({ chartType, data }) => {
  const generateNarration = (type, data) => {
    const narrations = {
      sales: {
        title: "Sales Performance Analysis",
        icon: TrendingUp,
        content: data ? 
          `Forecast accuracy remains stable at 91%, with minor volatility driven by ad campaign brightness variations. Recent performance shows a ${data.trend || 'positive'} trajectory with seasonal patterns indicating strong market positioning.` :
          "Sales performance analysis reveals consistent growth patterns with forecast accuracy maintaining 91% reliability. Seasonal trends and campaign effectiveness drive performance metrics."
      },
      sentiment: {
        title: "Sentiment Intelligence",
        icon: Heart,
        content: data ?
          `Customer sentiment analysis shows ${data.sentiment > 0.7 ? 'highly positive' : data.sentiment > 0.4 ? 'moderately positive' : 'neutral'} engagement levels at ${(data.sentiment * 100).toFixed(0)}%. This correlates with ${data.sentiment > 0.7 ? '15-20%' : '5-10%'} higher retention rates.` :
          "Sentiment analysis reveals customer engagement patterns and emotional responses to marketing campaigns. Positive sentiment correlates with higher conversion rates and brand loyalty."
      },
      visual: {
        title: "Visual Impact Assessment",
        icon: Eye,
        content: data ?
          `Visual analysis indicates ${data.brightness > 70 ? 'high brightness' : data.brightness > 40 ? 'moderate brightness' : 'low brightness'} levels at ${data.brightness?.toFixed(0) || 'N/A'}%. Color psychology and visual appeal significantly impact customer engagement and conversion rates.` :
          "Visual element analysis shows how image characteristics, color schemes, and brightness levels influence customer perception and purchasing decisions."
      },
      correlation: {
        title: "Multi-Modal Correlation",
        icon: GitBranch,
        content: data ?
          `Cross-modal analysis reveals ${data.correlation > 0.7 ? 'strong' : data.correlation > 0.4 ? 'moderate' : 'weak'} correlations between sales performance, sentiment scores, and visual elements. Integrated insights provide comprehensive business intelligence.` :
          "Multi-modal correlation analysis reveals hidden patterns between sales data, customer sentiment, and visual marketing elements. This integrated approach provides deeper business insights."
      },
      forecast: {
        title: "Predictive Analytics",
        icon: TrendingUp,
        content: data ?
          `Forecasting models show ${data.accuracy > 90 ? 'high' : data.accuracy > 80 ? 'moderate' : 'variable'} accuracy at ${data.accuracy?.toFixed(0) || '91'}%. Predictive trends indicate ${data.trend || 'positive'} market conditions with seasonal adjustments.` :
          "Predictive analytics utilize advanced machine learning models to forecast future performance based on historical data, sentiment patterns, and visual marketing effectiveness."
      }
    }

    return narrations[type] || narrations.sales
  }

  const narration = generateNarration(chartType, data)
  const Icon = narration.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mb-6"
    >
      <div className="bg-gradient-glass border border-dark-border rounded-xl p-4">
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 bg-gradient-accent rounded-lg flex items-center justify-center flex-shrink-0">
            <Icon className="h-4 w-4 text-white" />
          </div>
          
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-sm font-semibold text-text-primary">
                {narration.title}
              </h3>
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-2 h-2 bg-accent-from rounded-full"
              />
            </div>
            
            <p className="text-sm text-text-secondary leading-relaxed">
              {narration.content}
            </p>
            
            <div className="flex items-center space-x-4 mt-3 text-xs text-text-muted">
              <span className="flex items-center space-x-1">
                <Brain className="h-3 w-3 text-accent-from" />
                <span>AI-Generated Insight</span>
              </span>
              <span>•</span>
              <span>Updated {new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default InsightNarration

