import React from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import Home from './pages/Home'
import Leads from './pages/Leads'
import Timeline from './pages/Timeline'
import Chat from './pages/Chat'
import Settings from './pages/Settings'
import SearchResults from './pages/SearchResults'
import FunnelStats from './pages/FunnelStats'
import Integrations from './pages/settings/Integrations'

export const routes = [
  { path: '/', element: <Navigate to="/home" replace /> },
  { path: '/home', element: <Home /> },
  { path: '/leads', element: <Leads /> },
  { path: '/timeline', element: <Timeline /> },
  { path: '/chat', element: <Chat /> },
  { path: '/settings', element: <Settings /> },
  { path: '/settings/integrations', element: <Integrations /> },
  { path: '/search', element: <SearchResults /> },
  { path: '/funnel-stats', element: <FunnelStats /> },
]
