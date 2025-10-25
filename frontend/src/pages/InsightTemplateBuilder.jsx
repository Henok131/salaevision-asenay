import { useState } from 'react'
import toast from 'react-hot-toast'

export default function InsightTemplateBuilder() {
  const [name, setName] = useState('High-performing campaign')
  const [rules, setRules] = useState([{ field: 'sentiment', op: '>', value: 0.7 }])

  const updateRule = (idx, key, val) => {
    const copy = [...rules]
    copy[idx] = { ...copy[idx], [key]: val }
    setRules(copy)
  }

  const addRule = () => setRules([...rules, { field: '', op: '==', value: '' }])
  const removeRule = (idx) => setRules(rules.filter((_, i) => i !== idx))

  const save = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/insights/templates`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
        },
        body: JSON.stringify({ name, rules, active: true }),
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json?.detail || 'Failed to save template')
      toast.success('Template saved')
    } catch (e) {
      toast.error(e.message)
    }
  }

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-3xl mx-auto bg-dark-card/95 border border-dark-border rounded-xl p-6">
        <h1 className="text-xl text-text-primary mb-4">Insight Template Builder</h1>

        <div className="mb-4">
          <label className="block text-sm text-text-secondary mb-1">Insight Label</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="w-full bg-dark-hover border border-dark-border rounded px-3 py-2 text-sm text-text-primary" />
        </div>

        <div className="mb-3 text-sm text-text-secondary">Rules (all must match):</div>
        <div className="space-y-2 mb-4">
          {rules.map((r, idx) => (
            <div key={idx} className="flex items-center space-x-2">
              <input placeholder="field" value={r.field} onChange={(e) => updateRule(idx, 'field', e.target.value)} className="flex-1 bg-dark-hover border border-dark-border rounded px-3 py-2 text-sm text-text-primary" />
              <select value={r.op} onChange={(e) => updateRule(idx, 'op', e.target.value)} className="bg-dark-hover border border-dark-border rounded px-2 text-sm text-text-primary">
                <option value=">">&gt;</option>
                <option value=">=">&gt;=</option>
                <option value="<">&lt;</option>
                <option value="<=">&lt;=</option>
                <option value="==">==</option>
                <option value="contains">contains</option>
              </select>
              <input placeholder="value" value={r.value} onChange={(e) => updateRule(idx, 'value', e.target.value)} className="flex-1 bg-dark-hover border border-dark-border rounded px-3 py-2 text-sm text-text-primary" />
              <button onClick={() => removeRule(idx)} className="px-2 py-2 border border-dark-border rounded text-xs">Remove</button>
            </div>
          ))}
        </div>
        <button onClick={addRule} className="px-3 py-2 border border-dark-border rounded text-sm mr-2">Add Rule</button>
        <button onClick={save} className="px-3 py-2 border border-dark-border rounded text-sm">Save Template</button>
      </div>
    </div>
  )
}
