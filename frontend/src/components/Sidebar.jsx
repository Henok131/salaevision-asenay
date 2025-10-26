import { NavLink } from 'react-router-dom'

const nav = [
  { to: '/home', label: 'Home' },
  { to: '/leads', label: 'Leads' },
  { to: '/timeline', label: 'Timeline' },
  { to: '/chat', label: 'Chat' },
  { to: '/settings', label: 'Settings' },
]

export default function Sidebar() {
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
            {n.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
