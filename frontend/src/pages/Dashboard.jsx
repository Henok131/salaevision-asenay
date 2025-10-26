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
import { analysisAPI } from '../api/analysis'
import MultimodalCorrelationChart from '../components/MultimodalCorrelationChart'
import { useAuth } from '../contexts/AuthContext'
import { motion } from 'framer-motion'
import CopyEmbedCode from '../components/CopyEmbedCode'

export const Dashboard = () => {
  const { user } = useAuth()
  const [uploadedFile, setUploadedFile] = useState(null)
  const [uploadedImage, setUploadedImage] = useState(null)
  const [ocrImage, setOcrImage] = useState(null)
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
  const [tokensLeft, setTokensLeft] = useState(null)
  const [weeklyDigestEnabled, setWeeklyDigestEnabled] = useState(true)
  const [weeklyDigestMode, setWeeklyDigestMode] = useState('both')
  const [upgradeModalOpen, setUpgradeModalOpen] = useState(false)
  const [rateLimitMsg, setRateLimitMsg] = useState(null)
  const [dashboardPublic, setDashboardPublic] = useState(false)
  const [dashboardPublicId, setDashboardPublicId] = useState(null)

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

  const handleOcrUpload = (event) => {
    const file = event.target.files[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file for OCR')
      return
    }
    setOcrImage(file)
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
      const result = await analysisAPI.analyzeData(uploadedFile, uploadedImage, campaignText)
      setAnalysis(result)
      toast.success('Multimodal analysis completed successfully!')
    } catch (error) {
      const msg = error?.response?.data?.detail || 'Analysis failed. Please try again.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleOcrExtract = async () => {
    if (!ocrImage) {
      toast.error('Upload an image for OCR first')
      return
    }
    try {
      setLoading(true)
      const form = new FormData()
      form.append('file', ocrImage)
      const resp = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/ocr/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
        body: form,
      })
      const json = await resp.json()
      if (!resp.ok) throw new Error(json?.detail || 'OCR failed')
      setInsights(prev => [{ id: Date.now(), text: `OCR: ${json.text?.slice(0, 300) || ''}`, timestamp: new Date().toLocaleTimeString(), type: 'ocr' }, ...prev])
      toast.success('OCR extracted successfully')
    } catch (e) {
      toast.error(e.message || 'OCR failed')
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

  useEffect(() => {
    // Fetch tokens remaining for badge if available via Supabase auth metadata
    // In a real app, fetch from backend /auth/me which now uses Supabase JWT
    const fetchTokens = async () => {
      try {
        const resp = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/auth/me`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
        })
        if (resp.ok) {
          const json = await resp.json()
          setTokensLeft(json?.user?.tokens_remaining ?? null)
        }
      } catch (_) {
        // ignore
      }
    }
    fetchTokens()
  }, [])

  // Global 402/429 handlers
  useEffect(() => {
    const onUpgrade = () => setUpgradeModalOpen(true)
    const onRate = (e) => setRateLimitMsg(`You're sending too many requests. Please wait ${e.detail?.retryAfter ?? 60} seconds.`)
    window.addEventListener('billing:upgrade_required', onUpgrade)
    window.addEventListener('rate:limited', onRate)
    return () => {
      window.removeEventListener('billing:upgrade_required', onUpgrade)
      window.removeEventListener('rate:limited', onRate)
    }
  }, [])

  const updateWeeklyDigest = async (enabled, mode) => {
    setWeeklyDigestEnabled(enabled)
    setWeeklyDigestMode(mode)
    try {
      await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/auth/me`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
      })
      // In a real implementation, add a backend endpoint to update user preferences.
    } catch (_) {}
  }

  const canShare = (user?.role === 'admin' || user?.role === 'analyst')

  const togglePublic = async () => {
    try {
      const resp = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/dashboards/toggle_public`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
        },
        body: JSON.stringify({ is_public: !dashboardPublic }),
      })
      const json = await resp.json()
      if (!resp.ok) throw new Error(json?.detail || 'Failed to update public status')
      setDashboardPublic(json.is_public)
      setDashboardPublicId(json.public_id)
    } catch (e) {
      // surface error minimal
    }
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
        {tokensLeft !== null && (
          <div className="px-6 pt-3">
            <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-lg text-xs border ${tokensLeft < 10 ? 'border-neon-red text-neon-red bg-neon-red/10' : 'border-neon-blue text-neon-blue bg-neon-blue/10'}`}>
              <span>Tokens Left:</span>
              <span className="font-semibold">{tokensLeft}</span>
              {tokensLeft < 10 && <span className="ml-1">(Low)</span>}
              <button
                className="ml-3 px-2 py-0.5 border border-dark-border rounded text-text-secondary hover:text-text-primary"
                onClick={async () => {
                  try {
                    const resp = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/auth/me`, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` } })
                    const json = await resp.json()
                    setTokensLeft(json?.user?.tokens_remaining ?? null)
                  } catch {}
                }}
              >
                Refresh
              </button>
            </div>
          </div>
        )}

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

                {/* Weekly Digest Settings */}
                <div className="mb-8 bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-text-primary">🗓️ Weekly AI Digest</h3>
                      <p className="text-sm text-text-secondary">Receive a weekly email (and optional voice clip) with your key insights.</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <label className="flex items-center space-x-2 text-sm">
                        <input type="checkbox" checked={weeklyDigestEnabled} onChange={(e) => updateWeeklyDigest(e.target.checked, weeklyDigestMode)} />
                        <span className="text-text-primary">Enable</span>
                      </label>
                      <select
                        className="bg-dark-hover border border-dark-border rounded px-2 py-1 text-sm text-text-primary"
                        value={weeklyDigestMode}
                        onChange={(e) => updateWeeklyDigest(weeklyDigestEnabled, e.target.value)}
                      >
                        <option value="text">Text Only</option>
                        <option value="voice">Voice Only</option>
                        <option value="both">Both</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Sharing / Embed */}
                {canShare && (
                  <div className="mb-8 bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-text-primary">🔗 Share Dashboard</h3>
                      <label className="flex items-center space-x-2 text-sm">
                        <input type="checkbox" checked={dashboardPublic} onChange={togglePublic} />
                        <span className="text-text-primary">Share publicly</span>
                      </label>
                    </div>
                    {dashboardPublic && dashboardPublicId && (
                      <CopyEmbedCode publicId={dashboardPublicId} />
                    )}
                  </div>
                )}

                {/* Upload Section */}
                {!analysis && renderUploadSection()}

                {/* OCR Section */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6 mb-8"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="text-text-primary font-semibold">OCR Extraction</div>
                    <button
                      onClick={handleOcrExtract}
                      className="px-4 py-2 rounded-lg bg-dark-hover text-text-secondary hover:text-text-primary border border-dark-border"
                      disabled={!ocrImage || loading}
                    >
                      {loading ? 'Extracting...' : 'Extract Text'}
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="bg-dark-hover hover:bg-dark-hover/80 text-text-primary px-4 py-2 rounded-lg cursor-pointer inline-block transition-colors">
                        <input type="file" accept="image/*" onChange={handleOcrUpload} className="hidden" />
                        Choose Image for OCR
                      </label>
                      {ocrImage && (
                        <div className="mt-2 text-xs text-neon-green">✓ {ocrImage.name}</div>
                      )}
                    </div>
                    <div className="p-3 bg-gradient-glass border border-accent-from/30 rounded-lg text-sm text-text-primary min-h-[60px]">
                      {insights.find(i => i.type === 'ocr')?.text || 'Extracted text will appear here.'}
                    </div>
                  </div>
                </motion.div>

                {/* Charts */}
                <InteractiveCharts 
                  activeTab={activeTab} 
                  filteredData={filteredData}
                  onDataHover={handleDataHover}
                  showAnnotations={true}
                />

        {/* Multimodal Correlation Section */}
        <div className="mt-8">
          <MultimodalCorrelationChart
            data={Array.from({ length: 40 }).map(() => ({
              sentiment: Math.random(),
              brightness: Math.random() * 100,
              sales: Math.random() * 2500 + 500,
              variance: (Math.random() - 0.5) * 0.6, // -0.3..0.3
            }))}
          />
        </div>
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

                {activeTab === 'insights' && (
                  <div className="mt-6 bg-dark-card/95 backdrop-blur-xl border border-dark-border rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-text-primary mb-2">Inbox Preview</h3>
                    <p className="text-sm text-text-secondary mb-4">Recent AI digests and alerts will appear here.</p>
                    <div className="space-y-3">
                      {insights.slice(0, 5).map((i) => (
                        <div key={i.id} className="p-3 bg-gradient-glass border border-accent-from/30 rounded">
                          <div className="text-xs text-text-muted">{i.timestamp}</div>
                          <div className="text-sm text-text-primary">{i.text}</div>
                        </div>
                      ))}
                      {insights.length === 0 && (
                        <div className="text-sm text-text-muted">No messages yet.</div>
                      )}
                    </div>
                  </div>
                )}
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
        {/* Upgrade Modal */}
        {upgradeModalOpen && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-dark-card border border-dark-border rounded-xl p-6 w-96">
              <h3 className="text-lg text-text-primary mb-2">Upgrade to continue</h3>
              <p className="text-sm text-text-secondary mb-4">You’ve run out of tokens. Upgrade your plan to keep analyzing.</p>
              <div className="flex justify-end space-x-2">
                <button className="px-3 py-2 text-text-secondary" onClick={() => setUpgradeModalOpen(false)}>Close</button>
                <a className="px-3 py-2 bg-gradient-accent text-white rounded" href="/pricing">Go to Pricing</a>
              </div>
            </div>
          </div>
        )}

        {/* Rate Limit Notice */}
        {rateLimitMsg && (
          <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-dark-card border border-dark-border rounded px-4 py-2 text-sm text-text-primary z-50">
            {rateLimitMsg}
            <button className="ml-2 text-text-secondary" onClick={() => setRateLimitMsg(null)}>Dismiss</button>
          </div>
        )}
      </div>
    </div>
  )
}
