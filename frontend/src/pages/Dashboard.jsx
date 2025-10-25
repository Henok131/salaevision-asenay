import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../contexts/AuthContext'
import { Upload, BarChart3, TrendingUp, Brain, FileText, Download, Image, Type, Eye, Menu } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import toast from 'react-hot-toast'
import { Sidebar } from '../components/Sidebar'
import { TopBar } from '../components/TopBar'
import { MetricCards } from '../components/MetricCards'
import { InteractiveCharts } from '../components/InteractiveCharts'
import AIInsightsPanel from '../components/AIInsightsPanel'
import ExportButton from '../components/ExportButton'

export const Dashboard = () => {
  const { user } = useAuth()
  const [uploadedFile, setUploadedFile] = useState(null)
  const [uploadedImage, setUploadedImage] = useState(null)
  const [campaignText, setCampaignText] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [filteredData, setFilteredData] = useState(null)
  const [aiInsightsOpen, setAiInsightsOpen] = useState(false)
  const [currentInsight, setCurrentInsight] = useState(null)
  const [insights, setInsights] = useState([])

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file')
      return
    }

    setUploadedFile(file)
  }

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file')
      return
    }

    setUploadedImage(file)
  }

  const handleTextChange = (event) => {
    setCampaignText(event.target.value)
  }

  const handleAnalysis = async () => {
    if (!uploadedFile) {
      toast.error('Please upload a CSV file first')
      return
    }

    setLoading(true)

    try {
      // Simulate API call with multimodal data
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      // Mock multimodal analysis results
      const mockAnalysis = {
        summary: "Your sales data shows strong growth potential with seasonal patterns. Combined with your marketing tone and visual elements, the analysis reveals both data-driven and creative drivers of success.",
        keyFactors: [
          { name: "Marketing Spend", impact: 0.35, trend: "up" },
          { name: "Customer Satisfaction", impact: 0.28, trend: "up" },
          { name: "Product Price", impact: 0.22, trend: "down" },
          { name: "Seasonal Trends", impact: 0.15, trend: "stable" }
        ],
        recommendations: [
          "Increase marketing budget by 20% for Q2",
          "Focus on customer retention strategies",
          "Optimize pricing for competitive advantage",
          "Implement seasonal marketing campaigns"
        ],
        text_insight: campaignText ? {
          tone: "The marketing text shows a confident, optimistic tone with emphasis on value and quality.",
          sentiment: "positive",
          key_themes: ["Quality", "Innovation"]
        } : null,
        visual_insight: uploadedImage ? {
          brightness: 180,
          dominant_color: "#4A90E2",
          characteristics: "Well-lit, Blue-dominant, Square format",
          dimensions: "800x600"
        } : null
      }

      setAnalysis(mockAnalysis)
      toast.success('Multimodal analysis completed successfully!')
    } catch (error) {
      toast.error('Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const generateForecast = async () => {
    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Mock forecast data
      const mockForecast = {
        historical: [
          { date: '2024-01-01', value: 1200 },
          { date: '2024-01-02', value: 1350 },
          { date: '2024-01-03', value: 1100 },
          { date: '2024-01-04', value: 1450 },
          { date: '2024-01-05', value: 1600 }
        ],
        forecast: [
          { date: '2024-01-06', value: 1700, lower: 1500, upper: 1900 },
          { date: '2024-01-07', value: 1750, lower: 1550, upper: 1950 },
          { date: '2024-01-08', value: 1800, lower: 1600, upper: 2000 }
        ]
      }
      
      setForecast(mockForecast)
      toast.success('Forecast generated successfully!')
    } catch (error) {
      toast.error('Forecast generation failed')
    } finally {
      setLoading(false)
    }
  }

  const mockChartData = [
    { name: 'Jan', sales: 12000, forecast: 13000 },
    { name: 'Feb', sales: 15000, forecast: 16000 },
    { name: 'Mar', sales: 18000, forecast: 19000 },
    { name: 'Apr', sales: 16000, forecast: 17000 },
    { name: 'May', sales: 20000, forecast: 21000 },
    { name: 'Jun', sales: 22000, forecast: 23000 }
  ]

  const handleMetricClick = (metricId) => {
    // Filter data based on selected metric
    setFilteredData(metricId)
    toast.success(`Filtering data for ${metricId}`)
  }

  const handleDataHover = (data) => {
    setCurrentInsight(data)
    if (data) {
      setAiInsightsOpen(true)
    }
  }

  const toggleAIInsights = () => {
    setAiInsightsOpen(!aiInsightsOpen)
  }

  const renderUploadSection = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-8 mb-8"
    >
      <div className="text-center mb-8">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Upload className="h-8 w-8 text-accent-from" />
          <BarChart3 className="h-8 w-8 text-accent-from" />
          <Image className="h-8 w-8 text-accent-from" />
          <Type className="h-8 w-8 text-accent-from" />
        </div>
        <h2 className="text-xl font-semibold text-text-primary mb-4">
          Multimodal Sales Analysis
        </h2>
        <p className="text-text-secondary mb-6">
          Upload your sales data, marketing images, and campaign text for comprehensive AI insights
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* CSV Upload */}
        <motion.div
          whileHover={{ scale: 1.02, y: -2 }}
          className="bg-gradient-glass border border-dark-border rounded-xl p-6"
        >
          <div className="text-center">
            <FileText className="h-8 w-8 text-accent-from mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Sales Data</h3>
            <p className="text-text-secondary text-sm mb-4">Upload CSV with sales numbers</p>
            <label className="bg-dark-hover hover:bg-dark-hover/80 text-text-primary px-4 py-2 rounded-lg cursor-pointer block transition-colors">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
              />
              Choose CSV File
            </label>
            {uploadedFile && (
              <div className="mt-2 text-xs text-neon-green">
                ✓ {uploadedFile.name}
              </div>
            )}
          </div>
        </motion.div>

        {/* Image Upload */}
        <motion.div
          whileHover={{ scale: 1.02, y: -2 }}
          className="bg-gradient-glass border border-dark-border rounded-xl p-6"
        >
          <div className="text-center">
            <Image className="h-8 w-8 text-accent-from mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Marketing Image</h3>
            <p className="text-text-secondary text-sm mb-4">Upload ad or product photo</p>
            <label className="bg-dark-hover hover:bg-dark-hover/80 text-text-primary px-4 py-2 rounded-lg cursor-pointer block transition-colors">
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
              Choose Image
            </label>
            {uploadedImage && (
              <div className="mt-2 text-xs text-neon-green">
                ✓ {uploadedImage.name}
              </div>
            )}
          </div>
        </motion.div>

        {/* Text Input */}
        <motion.div
          whileHover={{ scale: 1.02, y: -2 }}
          className="bg-gradient-glass border border-dark-border rounded-xl p-6"
        >
          <div className="text-center">
            <Type className="h-8 w-8 text-accent-from mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">Campaign Text</h3>
            <p className="text-text-secondary text-sm mb-4">Describe your marketing campaign</p>
            <textarea
              value={campaignText}
              onChange={handleTextChange}
              placeholder="Enter campaign description..."
              className="w-full h-20 px-3 py-2 bg-dark-hover border border-dark-border rounded-lg text-text-primary placeholder-text-muted text-sm resize-none focus:outline-none focus:ring-2 focus:ring-accent-from focus:border-accent-from/30"
            />
          </div>
        </motion.div>
      </div>

      <div className="text-center">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleAnalysis}
          disabled={!uploadedFile || loading}
          className="bg-gradient-accent text-white px-8 py-3 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-neon-blue transition-all duration-300"
        >
          {loading ? 'Analyzing...' : 'Start Multimodal Analysis'}
        </motion.button>
      </div>
    </motion.div>
  )

  return (
    <div className="min-h-screen bg-dark-bg flex">
      {/* Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        isOpen={sidebarOpen} 
        setIsOpen={setSidebarOpen} 
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col lg:ml-0">
        {/* Top Bar */}
        <TopBar 
          user={user} 
          plan="Pro" 
          onToggleAIInsights={toggleAIInsights}
          onExport={() => {/* Export functionality will be handled by ExportButton component */}}
          aiInsightsOpen={aiInsightsOpen}
        />

        {/* Mobile Menu Button */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-lg"
        >
          <Menu className="h-5 w-5 text-text-primary" />
        </button>

        {/* Main Content Area */}
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <AnimatePresence mode="wait">
            {activeTab === 'dashboard' && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                {/* Welcome Header */}
                <div className="mb-8">
                  <motion.h1
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-3xl font-bold text-text-primary mb-2"
                  >
                    Welcome back, {user?.email?.split('@')[0]}!
                  </motion.h1>
                  <motion.p
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-text-secondary"
                  >
                    Your multimodal explainable AI analytics dashboard
                  </motion.p>
                </div>

                {/* KPI Cards */}
                <MetricCards onCardClick={handleMetricClick} />

                {/* Upload Section */}
                {!analysis && renderUploadSection()}

                {/* Charts */}
                <InteractiveCharts 
                  activeTab={activeTab} 
                  filteredData={filteredData}
                  onDataHover={handleDataHover}
                  showAnnotations={true}
                />
              </motion.div>
            )}

            {activeTab !== 'dashboard' && (
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <InteractiveCharts 
                  activeTab={activeTab} 
                  filteredData={filteredData}
                  onDataHover={handleDataHover}
                  showAnnotations={true}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Loading State */}
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
            >
              <div className="bg-dark-card border border-dark-border rounded-xl p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-from mx-auto mb-4"></div>
                <p className="text-text-primary">Processing your multimodal data...</p>
              </div>
            </motion.div>
          )}

          {/* AI Insights Panel */}
          <AIInsightsPanel
            isOpen={aiInsightsOpen}
            onClose={() => setAiInsightsOpen(false)}
            currentInsight={currentInsight}
            chartType={activeTab}
          />

          {/* Export Button (floating) */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="fixed bottom-6 right-6 z-40"
          >
            <ExportButton
              chartData={analysis}
              insights={insights}
              user={user}
            />
          </motion.div>
        </main>
      </div>
    </div>
  )
}
