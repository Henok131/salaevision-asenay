import { supabase } from '../supabaseClient'
import LanguageSelector from './LanguageSelector'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function Header() {
  const { t } = useTranslation()
  const [userEmail, setUserEmail] = useState('')
  const [q, setQ] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      const email = data?.session?.user?.email ?? ''
      setUserEmail(email)
    })
  }, [])

  const logout = async () => {
    await supabase.auth.signOut()
    window.location.href = '/login'
  }

  return (
    <header className="sticky top-0 z-10 bg-white border-b border-gray-200 flex items-center justify-between px-4 py-3 md:ml-[var(--sidebar-width)]">
      <div className="font-semibold">{t('dashboard')}</div>
      <div className="flex items-center gap-4">
        <form onSubmit={(e) => { e.preventDefault(); navigate('/search?query=' + encodeURIComponent(q)) }} className="hidden sm:flex items-center">
          <input value={q} onChange={(e)=>setQ(e.target.value)} className="border rounded px-2 py-1 text-sm" placeholder="Search" />
        </form>
        <LanguageSelector />
        <div className="text-sm text-gray-600">{userEmail}</div>
        <button onClick={logout} className="px-3 py-1.5 bg-gray-900 text-white rounded-md text-sm">Logout</button>
      </div>
    </header>
  )
}
