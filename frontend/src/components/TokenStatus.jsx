import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import apiClient from '../api/client'

export default function TokenStatus() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchStatus = async () => {
    setLoading(true)
    setError('')
    try {
      const { data } = await apiClient.get('/tokens/status')
      setStatus(data)
    } catch (e) {
      setError('Unable to load tokens')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  if (loading) return <div className="text-xs text-text-muted">Loading tokens…</div>
  if (error) return <div className="text-xs text-neon-red">{error}</div>
  if (!status) return null

  const { remaining_tokens, total_tokens } = status
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4">
      <div className="text-xs text-text-secondary">Tokens left: <span className="text-text-primary font-semibold">{remaining_tokens}</span> / {total_tokens}</div>
      <div className="w-full h-1 bg-dark-hover rounded mt-1">
        <div className="h-1 bg-accent-from rounded" style={{ width: `${Math.max(0, (remaining_tokens / total_tokens) * 100)}%` }} />
      </div>
    </motion.div>
  )
}
