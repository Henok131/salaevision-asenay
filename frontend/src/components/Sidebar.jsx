import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  BarChart3, 
  Brain, 
  TrendingUp, 
  Heart, 
  Eye, 
  GitBranch, 
  FileText, 
  Settings,
  Menu,
  X
} from 'lucide-react'

import sidebarConfig from '../config/sidebar.config'

const collapseKey = 'sidebar-collapsed'
const sectionStateKey = 'sidebar-section-state'

export const Sidebar = ({ activeTab, setActiveTab, isOpen, setIsOpen }) => {
  const [collapsed, setCollapsed] = useState(false)
  const [sectionOpen, setSectionOpen] = useState({})

  // load persisted states
  useEffect(() => {
    const savedCollapsed = localStorage.getItem(collapseKey)
    const savedSection = localStorage.getItem(sectionStateKey)
    if (savedCollapsed != null) setCollapsed(savedCollapsed === 'true')
    if (savedSection) {
      try { setSectionOpen(JSON.parse(savedSection)) } catch {}
    }
  }, [])

  useEffect(() => {
    localStorage.setItem(collapseKey, String(collapsed))
  }, [collapsed])

  useEffect(() => {
    localStorage.setItem(sectionStateKey, JSON.stringify(sectionOpen))
  }, [sectionOpen])

  const toggleSection = (id) => {
    setSectionOpen(prev => ({ ...prev, [id]: !prev[id] }))
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed left-0 right-0 top-16 bottom-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <motion.div
        initial={{ x: -280 }}
        animate={{ x: isOpen ? 0 : -280 }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className={`fixed left-0 top-16 h-[calc(100vh-4rem)] ${collapsed ? 'w-20' : 'w-72'} bg-dark-card/95 backdrop-blur-xl border-r border-dark-border z-40 lg:top-0 lg:h-full lg:z-auto lg:static lg:translate-x-0`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-border">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-accent rounded-lg flex items-center justify-center">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-text-primary">SalesVision</h1>
              <p className="text-xs text-text-muted">XAI-360</p>
            </div>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="lg:hidden p-2 hover:bg-dark-hover rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5 text-text-secondary" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          <div className="flex items-center justify-between mb-2">
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-2 rounded-lg hover:bg-dark-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70"
              aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              <Menu className="h-5 w-5 text-text-secondary" />
            </button>
          </div>

          {sidebarConfig.map((section) => {
            const SectionIcon = section.icon
            const open = sectionOpen[section.id] ?? true
            return (
              <div key={section.id} className="mb-2">
                <button
                  onClick={() => toggleSection(section.id)}
                  className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-dark-hover text-text-secondary hover:text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70"
                  aria-expanded={open}
                  aria-controls={`section-${section.id}`}
                >
                  <SectionIcon className="h-5 w-5 flex-shrink-0" />
                  {!collapsed && <span className="font-semibold text-left">{section.label}</span>}
                </button>
                <AnimatePresence initial={false}>
                  {open && (
                    <motion.div
                      id={`section-${section.id}`}
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ type: 'tween', duration: 0.2 }}
                      className="pl-2 mt-1"
                    >
                      {section.items.map((item) => {
                        const Icon = item.icon
                        const isActive = activeTab === item.id
                        return (
                          <motion.button
                            key={item.id}
                            onClick={() => {
                              setActiveTab(item.id)
                              setIsOpen(false)
                            }}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className={`w-full flex items-center space-x-3 px-4 py-2 rounded-lg transition-all duration-200 ${
                              isActive
                                ? 'bg-gradient-glass border border-accent-from/30 text-text-primary shadow-neon-blue'
                                : 'text-text-secondary hover:bg-dark-hover hover:text-text-primary'
                            }`}
                            title={collapsed ? item.label : undefined}
                          >
                            <Icon className={`h-5 w-5 ${isActive ? 'text-accent-from' : ''}`} />
                            {!collapsed && <span className="font-medium text-left truncate">{item.label}</span>}
                            {isActive && !collapsed && (
                              <motion.div
                                layoutId="activeTab"
                                className="ml-auto w-2 h-2 bg-accent-from rounded-full"
                                initial={false}
                                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                              />
                            )}
                          </motion.button>
                        )
                      })}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-gradient-glass p-4 rounded-lg border border-dark-border">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-accent rounded-full flex items-center justify-center">
                <span className="text-xs font-bold text-white">AT</span>
              </div>
              <div>
                <p className="text-sm font-medium text-text-primary">Asenay Tech</p>
                <p className="text-xs text-text-muted">Professional Plan</p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </>
  )
}

