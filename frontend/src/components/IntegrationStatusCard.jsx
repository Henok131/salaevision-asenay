import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

export default function IntegrationStatusCard() {
  const { t } = useTranslation()
  const [status, setStatus] = useState({})
  const [loading, setLoading] = useState(true)

  const fetchStatus = async () => {
    setLoading(true)
    const r = await fetch('/api/integrations/status')
    const data = await r.json()
    setStatus(data)
    setLoading(false)
  }

  useEffect(() => { fetchStatus() }, [])

  const keys = Object.keys(status)
  return (
    <div className="border rounded p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold">{t('integrations') || 'Integrations'}</h3>
        <button onClick={fetchStatus} className="px-3 py-1.5 border rounded text-sm">{t('refresh') || 'Refresh'}</button>
      </div>
      {loading ? (
        <div className="text-sm text-gray-600">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {keys.map(k => (
            <div key={k} className="flex items-center justify-between border rounded px-3 py-2">
              <div className="text-sm">{k.toUpperCase()}</div>
              <div className={`text-sm ${status[k] ? 'text-green-600' : 'text-red-600'}`}>{status[k] ? '🟢 Connected' : '🔴 Not Connected'}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
