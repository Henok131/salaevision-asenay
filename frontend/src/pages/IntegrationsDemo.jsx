import React, { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useSearchParams } from 'react-router-dom'

const providerList = (import.meta.env.VITE_INTEGRATION_PROVIDERS || '').split(',').map((p) => p.trim()).filter(Boolean)
const providers = providerList.map((p) => ({ key: p, label: p }))

export function IntegrationsDemo() {
  const { t } = useTranslation()
  const [params] = useSearchParams()
  const demo = params.get('demo') === 'true'
  const [step, setStep] = useState(0)
  const [typing, setTyping] = useState('')
  const script = useMemo(
    () => [
      'Initialize integration wizard...',
      'Checking OAuth credentials...',
      'Generating webhook URL...',
      'Testing auth...',
      'Syncing sample objects...',
      'Connected successfully!',
    ],
    []
  )

  useEffect(() => {
    if (!demo) return
    let mounted = true
    let idx = 0
    let char = 0
    const loop = () => {
      if (!mounted) return
      const word = script[idx]
      if (char <= word.length) {
        setTyping(word.slice(0, char))
        char += 1
      } else {
        idx = (idx + 1) % script.length
        char = 0
      }
      setTimeout(loop, 80)
    }
    loop()
    return () => {
      mounted = false
    }
  }, [demo, script])

  useEffect(() => {
    if (!demo) return
    const id = setInterval(() => setStep((s) => (s + 1) % providers.length), 2500)
    return () => clearInterval(id)
  }, [demo])

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">{t('Integrations')}</h1>
      <div className="grid grid-cols-2 gap-4">
        {providers.map((p, i) => (
          <div
            key={p.key}
            className={`rounded-lg border p-4 transition-all ${step === i && demo ? 'border-blue-400 shadow-lg' : 'border-slate-700'}`}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium">{p.label}</span>
              <span className={`text-xs px-2 py-1 rounded ${demo ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-500/10 text-slate-300'}`}>
                {demo ? t('Connecting') : t('Disconnected')}
              </span>
            </div>
            <div className="text-sm mt-2 text-slate-300">
              {demo ? typing : t('Disconnected')}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
