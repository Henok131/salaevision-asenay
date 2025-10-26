import { useEffect, useState } from 'react'
import FunnelChart from '../components/charts/FunnelChart'
import { useTranslation } from 'react-i18next'

export default function FunnelStats() {
  const { t } = useTranslation()
  const [stats, setStats] = useState(null)
  useEffect(() => {
    fetch('/api/funnel-stats')
      .then(r => r.json())
      .then(d => setStats({
        new: d.total_leads,
        contacted: d.leads_contacted,
        interested: d.leads_scored, // proxy for demo
        converted: Object.values(d.conversions_by_week || {}).reduce((a,b)=>a+b,0)
      }))
      .catch(()=>{})
  }, [])

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">{t('funnel_stats') || 'Funnel Stats'}</h1>
      <div className="mt-4">
        <FunnelChart data={stats || {}} />
      </div>
    </div>
  )
}
