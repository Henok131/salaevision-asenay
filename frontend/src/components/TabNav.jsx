import { motion } from 'framer-motion'

export const TabNav = ({ tabs, activeTab, setActiveTab }) => {
  return (
    <div className="relative flex gap-4 border-b border-dark-border">
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => setActiveTab(tab)}
          className={`relative pb-2 text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70 ${
            activeTab === tab ? 'text-accent-from' : 'text-text-secondary'
          }`}
          aria-current={activeTab === tab ? 'page' : undefined}
        >
          {tab}
          {activeTab === tab && (
            <motion.div
              layoutId="underline"
              className="absolute bottom-0 left-0 right-0 h-[2px] bg-accent-from"
            />
          )}
        </button>
      ))}
    </div>
  )
}

export default TabNav
