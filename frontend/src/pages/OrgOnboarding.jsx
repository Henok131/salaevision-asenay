import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

export default function OrgOnboarding() {
  const { user } = useAuth()
  const [orgName, setOrgName] = useState('')
  const [inviteToken, setInviteToken] = useState('')

  const createOrg = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/orgs/create?name=${encodeURIComponent(orgName)}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json?.detail || 'Failed to create org')
      toast.success('Organization created')
    } catch (e) {
      toast.error(e.message)
    }
  }

  const joinOrgWithToken = async () => {
    if (!inviteToken) return
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/orgs/accept_invite?token=${encodeURIComponent(inviteToken)}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token') || ''}` },
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json?.detail || 'Failed to accept invite')
      toast.success('Joined organization')
    } catch (e) {
      toast.error(e.message)
    }
  }

  // Auto-accept invite if token present in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const t = params.get('token')
    if (t) {
      setInviteToken(t)
      ;(async () => {
        await joinOrgWithToken()
      })()
    }
  }, [])

  return (
    <div className="min-h-screen bg-dark-bg p-6">
      <div className="max-w-2xl mx-auto bg-dark-card/95 border border-dark-border rounded-xl p-6">
        <h1 className="text-xl text-text-primary mb-4">Welcome to SalesVision</h1>
        <p className="text-sm text-text-secondary mb-6">Create a new organization or join an existing one.</p>

        <div className="mb-6">
          <h2 className="text-lg text-text-primary mb-2">Create Organization</h2>
          <div className="flex space-x-2">
            <input value={orgName} onChange={(e) => setOrgName(e.target.value)} placeholder="Acme Inc." className="flex-1 bg-dark-hover border border-dark-border rounded px-3 py-2 text-sm text-text-primary" />
            <button onClick={createOrg} className="px-3 py-2 border border-dark-border rounded text-sm">Create</button>
          </div>
        </div>

        <div>
          <h2 className="text-lg text-text-primary mb-2">Join via Invite Token</h2>
          <div className="flex space-x-2">
            <input value={inviteToken} onChange={(e) => setInviteToken(e.target.value)} placeholder="paste token" className="flex-1 bg-dark-hover border border-dark-border rounded px-3 py-2 text-sm text-text-primary" />
            <button onClick={joinOrgWithToken} className="px-3 py-2 border border-dark-border rounded text-sm">Join</button>
          </div>
        </div>
      </div>
    </div>
  )
}
