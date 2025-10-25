import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  Cell
} from 'recharts'
import { TrendingUp, BarChart3, Activity, GitBranch } from 'lucide-react'
import ChartAnnotations from './ChartAnnotations'
import InsightNarration from './InsightNarration'

// Mock data generators
const generateTimeSeriesData = () => {
  const data = []
  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
    data.push({
      date: date.toISOString().split('T')[0],
      actual: Math.random() * 1000 + 500,
      forecast: Math.random() * 1000 + 500 + (Math.random() - 0.5) * 200,
      sentiment: Math.random() * 0.4 + 0.3,
      brightness: Math.random() * 40 + 30
    })
  }
  return data
}

const generateScatterData = () => {
  const data = []
  for (let i = 0; i < 50; i++) {
    data.push({
      brightness: Math.random() * 100,
      sales: Math.random() * 2000 + 500,
      sentiment: Math.random() * 0.8 + 0.1
    })
  }
  return data
}

const generateCorrelationData = () => {
  const metrics = ['Sales', 'Sentiment', 'Brightness', 'Engagement', 'Conversion']
  const data = []
  
  metrics.forEach((metric, i) => {
    const row = { metric }
    metrics.forEach((_, j) => {
      if (i === j) {
        row[metrics[j]] = 1
      } else {
        row[metrics[j]] = Math.random() * 0.8 + 0.1
      }
    })
    data.push(row)
  })
  
  return { data, metrics }
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-dark-card border border-accent-from/30 rounded-lg p-4 shadow-neon-blue"
      >
        <div className="text-text-primary font-medium mb-2">{label}</div>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center space-x-2 mb-1">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-text-secondary">
              {entry.name}: {entry.value}
            </span>
          </div>
        ))}
        {data.insight && (
          <div className="mt-2 pt-2 border-t border-dark-border text-xs text-accent-from">
            💡 {data.insight}
          </div>
        )}
      </motion.div>
    )
  }
  return null
}

export const InteractiveCharts = ({ activeTab, filteredData, onDataHover, showAnnotations = true }) => {
  const [timeSeriesData, setTimeSeriesData] = useState(generateTimeSeriesData())
  const [scatterData, setScatterData] = useState(generateScatterData())
  const [correlationData, setCorrelationData] = useState(generateCorrelationData())
  const [isLive, setIsLive] = useState(false)
  const [hoveredData, setHoveredData] = useState(null)

  // Real-time data simulation
  useEffect(() => {
    if (!isLive) return

    const interval = setInterval(() => {
      setTimeSeriesData(prev => {
        const newData = [...prev.slice(1)]
        const lastDate = new Date(newData[newData.length - 1].date)
        const newDate = new Date(lastDate.getTime() + 24 * 60 * 60 * 1000)
        
        newData.push({
          date: newDate.toISOString().split('T')[0],
          actual: Math.random() * 1000 + 500,
          forecast: Math.random() * 1000 + 500 + (Math.random() - 0.5) * 200,
          sentiment: Math.random() * 0.4 + 0.3,
          brightness: Math.random() * 40 + 30,
          insight: "Live data stream - real-time performance tracking"
        })
        return newData
      })
    }, 3000)

    return () => clearInterval(interval)
  }, [isLive])

  const handleDataHover = (data) => {
    setHoveredData(data)
    onDataHover?.(data)
  }

  const renderTimeSeriesChart = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6 relative"
    >
      {/* Insight Narration */}
      <InsightNarration 
        chartType="sales" 
        data={hoveredData || { trend: 'positive', accuracy: 91 }}
      />

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <TrendingUp className="h-6 w-6 text-accent-from" />
          <h3 className="text-lg font-semibold text-text-primary">Sales Performance</h3>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsLive(!isLive)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            isLive 
              ? 'bg-neon-green/20 text-neon-green border border-neon-green/30' 
              : 'bg-dark-hover text-text-secondary hover:text-text-primary'
          }`}
        >
          {isLive ? '🟢 Live' : '⏸️ Paused'}
        </motion.button>
      </div>
      
      <div className="relative">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart 
            data={timeSeriesData}
            onMouseMove={(data) => handleDataHover(data.activePayload?.[0]?.payload)}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
            <XAxis 
              dataKey="date" 
              stroke="#8a9ba8"
              fontSize={12}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis stroke="#8a9ba8" fontSize={12} />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#78c8ff"
              strokeWidth={2}
              dot={{ fill: '#78c8ff', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#78c8ff', strokeWidth: 2 }}
            />
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#b084ff"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ fill: '#b084ff', strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>

        {/* Chart Annotations */}
        <ChartAnnotations 
          data={timeSeriesData} 
          chartType="sales" 
          isVisible={showAnnotations}
        />
      </div>
    </motion.div>
  )

  const renderSentimentChart = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6 relative"
    >
      {/* Insight Narration */}
      <InsightNarration 
        chartType="sentiment" 
        data={hoveredData || { sentiment: 0.78 }}
      />

      <div className="flex items-center space-x-3 mb-6">
        <Activity className="h-6 w-6 text-accent-from" />
        <h3 className="text-lg font-semibold text-text-primary">Sentiment Timeline</h3>
      </div>
      
      <div className="relative">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart 
            data={timeSeriesData}
            onMouseMove={(data) => handleDataHover(data.activePayload?.[0]?.payload)}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
            <XAxis 
              dataKey="date" 
              stroke="#8a9ba8"
              fontSize={12}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis stroke="#8a9ba8" fontSize={12} domain={[0, 1]} />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="sentiment"
              stroke="#4ade80"
              fill="url(#sentimentGradient)"
              strokeWidth={2}
            />
            <defs>
              <linearGradient id="sentimentGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4ade80" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#4ade80" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
          </AreaChart>
        </ResponsiveContainer>

        {/* Chart Annotations */}
        <ChartAnnotations 
          data={timeSeriesData} 
          chartType="sentiment" 
          isVisible={showAnnotations}
        />
      </div>
    </motion.div>
  )

  const renderScatterChart = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6"
    >
      <div className="flex items-center space-x-3 mb-6">
        <BarChart3 className="h-6 w-6 text-accent-from" />
        <h3 className="text-lg font-semibold text-text-primary">Brightness vs Sales</h3>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart data={scatterData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
          <XAxis 
            type="number" 
            dataKey="brightness" 
            name="Brightness"
            stroke="#8a9ba8"
            fontSize={12}
          />
          <YAxis 
            type="number" 
            dataKey="sales" 
            name="Sales"
            stroke="#8a9ba8"
            fontSize={12}
          />
          <Tooltip content={<CustomTooltip />} />
          <Scatter dataKey="sales" fill="#78c8ff">
            {scatterData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={`hsl(${entry.sentiment * 120}, 70%, 50%)`}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </motion.div>
  )

  const renderCorrelationChart = () => {
    const { data, metrics } = correlationData
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6"
      >
        <div className="flex items-center space-x-3 mb-6">
          <GitBranch className="h-6 w-6 text-accent-from" />
          <h3 className="text-lg font-semibold text-text-primary">Correlation Heatmap</h3>
        </div>
        
        <div className="grid grid-cols-6 gap-2">
          <div></div>
          {metrics.map(metric => (
            <div key={metric} className="text-xs text-text-secondary text-center font-medium">
              {metric}
            </div>
          ))}
          
          {data.map((row, i) => (
            <>
              <div key={`label-${i}`} className="text-xs text-text-secondary font-medium flex items-center">
                {row.metric}
              </div>
              {metrics.map((metric, j) => {
                const value = row[metric]
                const intensity = Math.abs(value)
                const color = value > 0 ? 'neon-green' : 'neon-red'
                
                return (
                  <motion.div
                    key={`cell-${i}-${j}`}
                    whileHover={{ scale: 1.1 }}
                    className={`w-full h-8 rounded border border-dark-border flex items-center justify-center text-xs font-mono ${
                      intensity > 0.7 ? `bg-${color}/30 text-${color}` :
                      intensity > 0.4 ? `bg-${color}/20 text-${color}` :
                      'bg-dark-hover text-text-muted'
                    }`}
                  >
                    {value.toFixed(2)}
                  </motion.div>
                )
              })}
            </>
          ))}
        </div>
      </motion.div>
    )
  }

  const renderCharts = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {renderTimeSeriesChart()}
            {renderSentimentChart()}
          </div>
        )
      case 'forecast':
        return renderTimeSeriesChart()
      case 'sentiment':
        return renderSentimentChart()
      case 'visual':
        return renderScatterChart()
      case 'correlation':
        return renderCorrelationChart()
      default:
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {renderTimeSeriesChart()}
            {renderSentimentChart()}
          </div>
        )
    }
  }

  return (
    <motion.div
      key={activeTab}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3 }}
    >
      {renderCharts()}
    </motion.div>
  )
}
