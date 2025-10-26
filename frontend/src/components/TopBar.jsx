import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Bell, User, Crown, Zap, Brain, Download } from 'lucide-react'
import LanguageToggle from './LanguageToggle'

export const TopBar = ({ user, plan = 'Free', onToggleAIInsights, onExport, aiInsightsOpen = false }) => {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    })
  }

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getPlanBadge = (plan) => {
    const plans = {
      'Free': { color: 'text-text-muted', bg: 'bg-gray-500/20', icon: User },
      'Pro': { color: 'text-neon-blue', bg: 'bg-neon-blue/20', icon: Zap },
      'Business': { color: 'text-neon-purple', bg: 'bg-neon-purple/20', icon: Crown }
    }
    
    return plans[plan] || plans['Free']
  }

  const planConfig = getPlanBadge(plan)
  const Icon = planConfig.icon

  return (
    <motion.div
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-dark-card/95 backdrop-blur-xl border-b border-dark-border px-6 py-4"
    >
      <div className="flex items-center justify-between">
        {/* Left side - Date/Time */}
        <div className="flex items-center space-x-6">
          <div className="text-text-primary">
            <div className="text-2xl font-mono font-bold">
              {formatTime(currentTime)}
            </div>
            <div className="text-sm text-text-secondary">
              {formatDate(currentTime)}
            </div>
          </div>
        </div>

        {/* Right side - User info and notifications */}
        <div className="flex items-center space-x-4">
          {/* AI Insights Toggle */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onToggleAIInsights}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all min-h-[44px] focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70 ${
              aiInsightsOpen 
                ? 'bg-gradient-accent text-white shadow-neon-blue' 
                : 'bg-dark-hover text-text-secondary hover:text-text-primary'
            }`}
          >
            <Brain className="h-4 w-4" />
            <span className="text-sm font-medium">
              AI Insights
            </span>
            {aiInsightsOpen && (
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 0.5, repeat: Infinity }}
                className="w-2 h-2 bg-white rounded-full"
              />
            )}
          </motion.button>

          {/* Export Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onExport}
            className="flex items-center space-x-2 px-3 py-2 bg-dark-hover text-text-secondary hover:text-text-primary rounded-lg transition-colors min-h-[44px] focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70"
          >
            <Download className="h-4 w-4" />
            <span className="text-sm font-medium">Export</span>
          </motion.button>

          {/* Plan Badge */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${planConfig.bg} border border-dark-border`}
          >
            <Icon className={`h-4 w-4 ${planConfig.color}`} />
            <span className={`text-sm font-medium ${planConfig.color}`}>
              {plan}
            </span>
          </motion.div>

          {/* Notifications */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="relative p-2 hover:bg-dark-hover rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5 text-text-secondary hover:text-text-primary" />
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 3 }}
              className="absolute -top-1 -right-1 w-3 h-3 bg-neon-red rounded-full"
            />
          </motion.button>

          {/* Language Toggle */}
          <LanguageToggle />

          {/* User Avatar */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center space-x-3 p-2 hover:bg-dark-hover rounded-lg transition-colors cursor-pointer"
          >
            <div className="w-8 h-8 bg-gradient-accent rounded-full flex items-center justify-center">
              <span className="text-sm font-bold text-white">
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </span>
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-medium text-text-primary">
                {user?.email?.split('@')[0] || 'User'}
              </p>
              <p className="text-xs text-text-muted">Analytics Dashboard</p>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}
