import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { useTranslation } from 'react-i18next'

export default function FunnelChart({ data }) {
  const { t } = useTranslation()
  const chartData = [
    { name: t('new'), value: data?.new || 0 },
    { name: t('contacted'), value: data?.contacted || 0 },
    { name: t('interested'), value: data?.interested || 0 },
    { name: t('converted'), value: data?.converted || 0 },
  ]
  return (
    <div className="w-full h-80">
      <h3 className="text-lg font-semibold mb-2">{t('funnel_stats')}</h3>
      <ResponsiveContainer>
        <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" tick={{ fontSize: 12 }} />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={100} />
          <Tooltip formatter={(v) => [v, t('leads')]} />
          <Bar dataKey="value" fill="#0ea5e9" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
