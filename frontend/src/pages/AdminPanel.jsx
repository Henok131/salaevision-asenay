import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

export default function AdminPanel() {
  const { user } = useAuth()
  const [members, setMembers] = useState([])
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('viewer')

  const fetchMembers = async () => {
    try {
      const orgId = user?.org_id
      if (!orgId) return
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/orgs/members?org_id=${orgId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
      })
      const json = await res.json()
      setMembers(json.members || [])
    } catch (e) {
      toast.error('Failed to load members')
    }
  }

  useEffect(() => {
    fetchMembers()
  }, [])

  const invite = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/orgs/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
        },
        body: JSON.stringify({ email: inviteEmail, role: inviteRole, org_id: user?.org_id }),
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json?.detail || 'Invite failed')
      toast.success('Invitation created')
      setInviteEmail('')
    } catch (e) {
      toast.error(e.message)
    }
  }

  const changeRole = async (memberId, role) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/orgs/assign_role?user_id=${memberId}&role=${role}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json?.detail || 'Update failed')
      toast.success('Role updated')
      fetchMembers()
    } catch (e) {
      toast.error(e.message)
    }
  }

  const isAdmin = user?.role === 'admin'

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-4xl mx-auto bg-dark-card/95 border border-dark-border rounded-xl p-6">
        <h1 className="text-xl text-text-primary mb-4">Admin Panel</h1>

        <div className="mb-6">
          <h2 className="text-lg text-text-primary mb-2">Members</h2>
          <div className="space-y-2">
            {members.map(m => (
              <div key={m.id} className="flex items-center justify-between bg-dark-hover rounded p-2">
                <div>
                  <div className="text-text-primary text-sm">{m.email}</div>
                  <div className="text-text-muted text-xs">Role: {m.role}</div>
                </div>
                {isAdmin && (
                  <div className="space-x-2">
                    <button onClick={() => changeRole(m.id, 'viewer')} className="text-xs px-2 py-1 border border-dark-border rounded">Viewer</button>
                    <button onClick={() => changeRole(m.id, 'analyst')} className="text-xs px-2 py-1 border border-dark-border rounded">Analyst</button>
                    <button onClick={() => changeRole(m.id, 'admin')} className="text-xs px-2 py-1 border border-dark-border rounded">Admin</button>
                  </div>
                )}
              </div>
            ))}
            {members.length === 0 && <div className="text-sm text-text-muted">No members yet.</div>}
          </div>
        </div>

        {isAdmin && (
          <div className="mb-6">
            <h2 className="text-lg text-text-primary mb-2">Invite Member</h2>
            <div className="flex space-x-2">
              <input value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} placeholder="email@company.com" className="flex-1 bg-dark-hover border border-dark-border rounded px-3 py-2 text-sm text-text-primary" />
              <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value)} className="bg-dark-hover border border-dark-border rounded px-2 text-sm text-text-primary">
                <option value="viewer">Viewer</option>
                <option value="analyst">Analyst</option>
                <option value="admin">Admin</option>
              </select>
              <button onClick={invite} className="px-3 py-2 border border-dark-border rounded text-sm">Send Invite</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
