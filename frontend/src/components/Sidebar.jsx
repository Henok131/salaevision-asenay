import { useState } from 'react'
import { motion } from 'framer-motion'
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

const navigationItems = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  { id: 'insights', label: 'Insights', icon: Brain },
  { id: 'forecast', label: 'Forecast', icon: TrendingUp },
  { id: 'sentiment', label: 'Sentiment', icon: Heart },
  { id: 'visual', label: 'Visual', icon: Eye },
  { id: 'correlation', label: 'Correlation', icon: GitBranch },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
]

export const Sidebar = ({ activeTab, setActiveTab, isOpen, setIsOpen }) => {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <motion.div
        initial={{ x: -280 }}
        animate={{ x: isOpen ? 0 : -280 }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className={`fixed left-0 top-0 h-full w-70 bg-dark-card/95 backdrop-blur-xl border-r border-dark-border z-50 lg:translate-x-0 lg:static lg:z-auto`}
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
            className="lg:hidden p-2 hover:bg-dark-hover rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-text-secondary" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navigationItems.map((item) => {
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
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-glass border border-accent-from/30 text-text-primary shadow-neon-blue'
                    : 'text-text-secondary hover:bg-dark-hover hover:text-text-primary'
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? 'text-accent-from' : ''}`} />
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="ml-auto w-2 h-2 bg-accent-from rounded-full"
                    initial={false}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
              </motion.button>
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

