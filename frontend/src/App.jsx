import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './contexts/AuthContext'
import { Dashboard } from './pages/Dashboard'
import { Pricing } from './pages/Pricing'
import { Login } from './pages/Login'
import { Signup } from './pages/Signup'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Navbar } from './components/Navbar'
import { Footer } from './components/Footer'
import EmbedViewer from './pages/EmbedViewer'
import AdminPanel from './pages/AdminPanel'
import OrgOnboarding from './pages/OrgOnboarding'
import Plugins from './pages/Plugins'
import InsightTemplateBuilder from './pages/InsightTemplateBuilder'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/embed/:id" element={<EmbedViewer />} />
              <Route path="/admin" element={<ProtectedRoute><AdminPanel /></ProtectedRoute>} />
              <Route path="/onboarding" element={<ProtectedRoute><OrgOnboarding /></ProtectedRoute>} />
              <Route path="/plugins" element={<ProtectedRoute><Plugins /></ProtectedRoute>} />
              <Route path="/insight-templates" element={<ProtectedRoute><InsightTemplateBuilder /></ProtectedRoute>} />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </main>
          <Footer />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1a1f3a',
                color: '#fff',
                border: '1px solid rgba(255, 255, 255, 0.2)',
              },
            }}
          />
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App

