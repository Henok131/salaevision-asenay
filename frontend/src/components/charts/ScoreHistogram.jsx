import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { useTranslation } from 'react-i18next'

function groupScores(leads = []) {
  const buckets = [0,20,40,60,80,100]
  const map = buckets.map((b, i) => ({ range: i === 0 ? '0-20' : `${b}-${b+20}`, value: 0 }))
  for (const l of leads) {
    const s = Number(l.score || 0)
    const idx = Math.min(4, Math.floor(s/20))
    map[idx].value += 1
  }
  return map
}

export default function ScoreHistogram({ leads }) {
  const { t } = useTranslation()
  const data = groupScores(leads)
  return (
    <div className="w-full h-80">
      <h3 className="text-lg font-semibold mb-2">{t('score_distribution')}</h3>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="range" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value" fill="#10b981" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
