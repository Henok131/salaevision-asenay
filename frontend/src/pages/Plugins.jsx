import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

const AVAILABLE = ['forecasting', 'embed', 'ocr', 'csv_import']

export default function Plugins() {
  const { user } = useAuth()
  const [plugins, setPlugins] = useState({})

  const load = async () => {
    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/plugins/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
    })
    const json = await res.json()
    const map = {}
    for (const p of json.plugins || []) map[p.plugin] = !!p.enabled
    setPlugins(map)
  }

  useEffect(() => { load() }, [])

  const toggle = async (plugin, enabled) => {
    await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/plugins/toggle?plugin=${plugin}&enabled=${enabled}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
    })
    load()
  }

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-2xl mx-auto bg-dark-card/95 border border-dark-border rounded-xl p-6">
        <h1 className="text-xl text-text-primary mb-4">Plugin Management</h1>
        <div className="space-y-3">
          {AVAILABLE.map(p => (
            <div key={p} className="flex items-center justify-between bg-dark-hover rounded p-3">
              <div className="text-text-primary text-sm">{p}</div>
              <label className="flex items-center space-x-2 text-sm">
                <input type="checkbox" checked={!!plugins[p]} onChange={(e) => toggle(p, e.target.checked)} />
                <span className="text-text-primary">Enabled</span>
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
