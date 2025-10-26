import { useState } from 'react'
import { useTranslation } from 'react-i18next'

export default function SearchResults() {
  const { t } = useTranslation()
  const [q, setQ] = useState('')
  const [rows, setRows] = useState([])

  const search = async (e) => {
    e.preventDefault()
    const resp = await fetch('/api/search_leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q })
    })
    const data = await resp.json()
    setRows(data || [])
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">{t('dashboard')} - Search</h1>
      <form onSubmit={search} className="flex gap-2 mb-4">
        <input className="border rounded px-3 py-2 flex-1" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search leads" />
        <button className="px-4 py-2 bg-gray-900 text-white rounded">Search</button>
      </form>
      <div className="space-y-2">
        {rows.map((r) => (
          <div key={r.id} className="border rounded p-3 flex justify-between">
            <div>
              <div className="font-medium">{r.name}</div>
              <div className="text-sm text-gray-600">{r.email}</div>
            </div>
            <div className="text-sm">score: {r.score.toFixed(3)}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
