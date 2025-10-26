import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Home from './pages/Home'
import Leads from './pages/Leads'
import Timeline from './pages/Timeline'
import Chat from './pages/Chat'
import Settings from './pages/Settings'
import { supabase } from './supabaseClient'

function ProtectedRoute({ children }) {
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState(null)
  const location = useLocation()

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setUser(data?.session?.user || null)
      setLoading(false)
    })
  }, [])

  if (loading) return <div className="p-6">Loading...</div>
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />
  return children
}

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const signInWithEmail = async (e) => {
    e.preventDefault()
    await supabase.auth.signInWithPassword({ email, password })
    window.location.href = '/home'
  }

  const signInWithGoogle = async () => {
    await supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: window.location.origin + '/home' } })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white border border-gray-200 rounded-lg p-6 w-full max-w-sm">
        <h1 className="text-xl font-semibold mb-4">Login</h1>
        <form onSubmit={signInWithEmail} className="space-y-3">
          <input className="w-full border border-gray-300 rounded px-3 py-2" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input className="w-full border border-gray-300 rounded px-3 py-2" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button className="w-full bg-gray-900 text-white rounded py-2">Sign in</button>
        </form>
        <button onClick={signInWithGoogle} className="mt-3 w-full border border-gray-300 rounded py-2">Sign in with Google</button>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <div className="min-h-screen">
      <Sidebar />
      <Header />
      <main className="md:ml-[var(--sidebar-width)] pt-[64px]">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/leads" element={<ProtectedRoute><Leads /></ProtectedRoute>} />
          <Route path="/timeline" element={<ProtectedRoute><Timeline /></ProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </main>
    </div>
  )
}
