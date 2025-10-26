import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import ScoreHistogram from '../components/charts/ScoreHistogram'

export default function Leads() {
  const { t } = useTranslation()
  const [leads, setLeads] = useState([])
  useEffect(() => {
    fetch('/api/leads')
      .then(r => r.json())
      .then(d => setLeads(d.leads || []))
      .catch(()=>{})
  }, [])
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">{t('leads')}</h1>
      <div className="mt-4">
        <ScoreHistogram leads={leads} />
      </div>
    </div>
  )
}
