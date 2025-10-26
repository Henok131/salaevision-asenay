import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { useTranslation } from 'react-i18next'

function toMonthlyAmounts(invoices = []) {
  const map = {}
  for (const inv of invoices) {
    const d = new Date(inv.created_at)
    if (isNaN(d.getTime())) continue
    const key = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2, '0')
    const amt = parseFloat(inv.parsed_json?.amount || '0') || 0
    map[key] = (map[key] || 0) + amt
  }
  return Object.entries(map).sort(([a],[b]) => a.localeCompare(b)).map(([month, amount]) => ({ month, amount }))
}

export default function InvoiceTrendChart({ invoices }) {
  const { t } = useTranslation()
  const data = toMonthlyAmounts(invoices)
  return (
    <div className="w-full h-80">
      <h3 className="text-lg font-semibold mb-2">{t('invoice_trend') || 'Invoice Trend'}</h3>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="amount" stroke="#ef4444" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
