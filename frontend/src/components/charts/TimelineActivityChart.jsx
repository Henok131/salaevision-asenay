import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { useTranslation } from 'react-i18next'

function toDailyCounts(events = []) {
  const map = {}
  for (const e of events) {
    const d = new Date(e.date || e.sent_at || e.created_at)
    if (isNaN(d.getTime())) continue
    const key = d.toISOString().slice(0,10)
    map[key] = (map[key] || 0) + 1
  }
  return Object.entries(map).sort(([a],[b]) => a.localeCompare(b)).map(([date, count]) => ({ date, count }))
}

export default function TimelineActivityChart({ events }) {
  const { t } = useTranslation()
  const data = toDailyCounts(events)
  return (
    <div className="w-full h-80">
      <h3 className="text-lg font-semibold mb-2">{t('timeline')}</h3>
      <ResponsiveContainer>
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="colorC" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.6}/>
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Area type="monotone" dataKey="count" stroke="#6366f1" fillOpacity={1} fill="url(#colorC)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
