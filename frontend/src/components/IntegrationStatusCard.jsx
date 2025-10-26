import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Typewriter } from 'react-simple-typewriter'

export default function IntegrationStatusCard() {
  const { t } = useTranslation()
  const [status, setStatus] = useState({})
  const [loading, setLoading] = useState(true)

  const fetchStatus = async () => {
    setLoading(true)
    const r = await fetch('/api/integrations/status')
    const data = await r.json()
    // Simulate delay for realism
    setTimeout(() => {
      setStatus(data)
      setLoading(false)
    }, 1200)
  }

  useEffect(() => { fetchStatus() }, [])

  const keys = Object.keys(status)
  const isDemo = useMemo(() => new URLSearchParams(window.location.search).get('demo') === 'true', [])
  const demoWords = ['Authenticating Gmail...', 'Syncing SAP Sales Cloud...', 'Connecting Slack...']
  return (
    <div className="border rounded p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-semibold">{t('integrations') || 'Integrations'}</h3>
        <button onClick={fetchStatus} className="px-3 py-1.5 border rounded text-sm">{t('refresh') || 'Refresh'}</button>
      </div>
      {loading ? (
        <div className="text-sm text-blue-500 animate-pulse flex items-center">
          <span>Connecting</span>
          <span className="dot-typing ml-1" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {keys.map(k => (
            <div key={k} className={`flex items-center justify-between border rounded px-3 py-2 ${status[k] ? 'border-green-500 shadow-lg animate-pulse' : ''}`}>
              <div className="text-sm">
                {k.toUpperCase()}<br/>
                {isDemo && (
                  <span className="text-xs text-gray-500">
                    <Typewriter words={demoWords} loop={false} cursor typeSpeed={60} deleteSpeed={30} />
                  </span>
                )}
              </div>
              <div className={`text-sm ${status[k] ? 'text-green-500 animate-bounce' : 'text-red-600'}`}>
                {status[k] ? '✅ Connected' : '🔴 Not Connected'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
