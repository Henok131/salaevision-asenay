import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import TimelineActivityChart from '../components/charts/TimelineActivityChart'

export default function Timeline() {
  const { t } = useTranslation()
  const [events, setEvents] = useState([])
  useEffect(() => {
    // Pull recent contacts as timeline events
    fetch('/api/customer_profile/dummy') // replace with selected lead id later
      .then(r => r.json())
      .then(d => setEvents(d.timeline || []))
      .catch(()=>{})
  }, [])
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">{t('timeline')}</h1>
      <div className="mt-4">
        <TimelineActivityChart events={events} />
      </div>
    </div>
  )
}
