import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

const nav = [
  { to: '/home', key: 'dashboard' },
  { to: '/leads', key: 'leads' },
  { to: '/timeline', key: 'timeline' },
  { to: '/chat', key: 'score' },
  { to: '/settings', key: 'settings' },
]

export default function Sidebar() {
  const { t } = useTranslation()
  return (
    <aside className="fixed left-0 top-0 h-full w-[var(--sidebar-width)] bg-white border-r border-gray-200 hidden md:block">
      <div className="px-5 py-4 font-semibold text-lg">CRM</div>
      <nav className="px-3 space-y-1">
        {nav.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            className={({ isActive }) =>
              `block px-4 py-2 rounded-md ${isActive ? 'bg-gray-900 text-white' : 'text-gray-700 hover:bg-gray-100'}`
            }
          >
            {t(n.key)}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
