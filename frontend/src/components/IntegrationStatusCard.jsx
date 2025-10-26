import { useEffect, useMemo, useRef, useState } from 'react'
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
  const params = useMemo(() => new URLSearchParams(window.location.search), [])
  const isDemo = params.get('demo') === 'true'
  const isLoop = params.get('loop') === 'true'
  const [recentConnected, setRecentConnected] = useState({})

  const prevStatusRef = useRef({})
  useEffect(() => {
    // Detect transitions from false->true to trigger one-time success animation
    const prev = prevStatusRef.current || {}
    const next = status || {}
    const updates = {}
    for (const k of Object.keys(next)) {
      if (next[k] && !prev[k]) {
        updates[k] = true
        // Clear after 1.2s
        setTimeout(() => setRecentConnected((rc) => ({ ...rc, [k]: false })), 1200)
      }
    }
    if (Object.keys(updates).length) setRecentConnected((rc) => ({ ...rc, ...updates }))
    prevStatusRef.current = next
  }, [status])

  const demoWordsByTool = {
    gmail: ['Waiting for Gmail credentials...', 'Authenticating Gmail...'],
    slack: ['Connecting Slack...', 'Posting test message...'],
    sap: ['Syncing SAP Sales Cloud...', 'Fetching OAuth token...'],
    outlook: ['Connecting Outlook...', 'Refreshing token...'],
    drive: ['Connecting Google Drive...', 'Validating service account...'],
  }
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
          {keys.map(k => {
            const connected = status[k]
            const forcedPending = isLoop
            const showPending = forcedPending || !connected
            const demoWords = demoWordsByTool[k] || ['Waiting for credentials...', 'Authorizing...']
            return (
              <div
                key={k}
                className={`flex items-center justify-between border rounded px-3 py-2 ${connected && !forcedPending ? (recentConnected[k] ? 'border-green-500 shadow-lg' : 'border-gray-200') : 'border-blue-300'}`}
                title={`To connect ${k.toUpperCase()}, set ENABLE_${k.toUpperCase()}=true and fill credentials in your .env file.`}
              >
                <div className="text-sm">
                  {k.toUpperCase()}<br/>
                  {isDemo && showPending && (
                    <span className="text-xs text-gray-500">
                      <Typewriter words={demoWords} loop={true} cursor typeSpeed={60} deleteSpeed={30} />
                    </span>
                  )}
                </div>
                {showPending ? (
                  <div className="flex items-center gap-2 text-blue-500 text-sm">
                    <span className="inline-block h-3 w-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></span>
                    <span className="animate-pulse">Connecting<span className="dot-typing ml-1" /></span>
                  </div>
                ) : (
                  <div className={`text-sm text-green-500 ${recentConnected[k] ? 'animate-bounce' : ''}`}>
                    <span className="px-2 py-1 border border-green-500 rounded shadow">✅ Connected</span>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
