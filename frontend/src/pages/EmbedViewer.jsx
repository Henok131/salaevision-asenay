import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts'

export default function EmbedViewer() {
  const { id } = useParams()
  const [chart, setChart] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)
        const base = import.meta.env.VITE_API_URL || ''
        const res = await fetch(`${base}/embed/${id}`)
        if (!res.ok) throw new Error('Not found')
        const json = await res.json()
        setChart(json)
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) return <div className="min-h-screen flex items-center justify-center text-text-secondary">Loading…</div>
  if (error) return <div className="min-h-screen flex items-center justify-center text-neon-red">{error}</div>
  if (!chart) return null

  const data = chart.data?.series || []

  return (
    <div className="min-h-screen bg-dark-bg p-4">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto">
        <div className="bg-dark-card/95 border border-dark-border rounded-xl p-4">
          <h1 className="text-lg text-text-primary mb-2">{chart.name || 'SalesVision Chart'}</h1>
          <div className="text-xs text-text-secondary mb-4">Public Embed • SalesVision XAI-360</div>
          <div style={{ width: '100%', height: 360 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                <XAxis dataKey="x" stroke="#8a9ba8" />
                <YAxis stroke="#8a9ba8" />
                <Tooltip />
                <Line type="monotone" dataKey="y" stroke="#78c8ff" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
