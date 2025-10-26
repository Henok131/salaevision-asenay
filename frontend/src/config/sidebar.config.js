import { BarChart3, Brain, TrendingUp, Heart, Eye, GitBranch, FileText, Settings, Users, CreditCard } from 'lucide-react'

export const sidebarConfig = [
  {
    id: 'workspace',
    label: 'Workspace',
    icon: Users,
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
      { id: 'insights', label: 'Insights', icon: Brain },
    ],
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: TrendingUp,
    items: [
      { id: 'forecast', label: 'Forecast', icon: TrendingUp },
      { id: 'sentiment', label: 'Sentiment', icon: Heart },
      { id: 'visual', label: 'Visual', icon: Eye },
      { id: 'correlation', label: 'Correlation', icon: GitBranch },
    ],
  },
  {
    id: 'reports',
    label: 'Reports',
    icon: FileText,
    items: [
      { id: 'reports', label: 'Reports', icon: FileText },
    ],
  },
  {
    id: 'billing',
    label: 'Billing',
    icon: CreditCard,
    items: [
      { id: 'settings', label: 'Settings', icon: Settings },
    ],
  },
]

export default sidebarConfig
