import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { supabase } from '../contexts/AuthContext'
import { useAuth } from '../contexts/AuthContext'
import { Link, useNavigate } from 'react-router-dom'

const CONSENT_KEY = 'asenay-consent-given'

export default function ConsentGate({ children }) {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [show, setShow] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const checkConsent = async () => {
      try {
        // Try session/local fallback first for speed
        const local = sessionStorage.getItem(CONSENT_KEY) || localStorage.getItem(CONSENT_KEY)
        if (local === 'true') {
          setShow(false)
          setLoading(false)
          return
        }
        if (!user) {
          setShow(true)
          setLoading(false)
          return
        }
        // Check Supabase profile/metadata
        const { data, error } = await supabase.from('users').select('consent_given').eq('id', user.id).single()
        if (!error && data?.consent_given) {
          sessionStorage.setItem(CONSENT_KEY, 'true')
          setShow(false)
        } else {
          setShow(true)
        }
      } catch {
        setShow(true)
      } finally {
        setLoading(false)
      }
    }
    checkConsent()
  }, [user])

  const accept = async () => {
    try {
      sessionStorage.setItem(CONSENT_KEY, 'true')
      if (user) {
        await supabase.from('users').update({ consent_given: true }).eq('id', user.id)
      }
      setShow(false)
    } catch {
      setShow(false)
    }
  }

  const reject = () => {
    sessionStorage.removeItem(CONSENT_KEY)
    navigate('/')
  }

  return (
    <>
      {children}
      <AnimatePresence>
        {!loading && show && (
          <motion.div className="fixed inset-0 z-[100]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="absolute inset-0 backdrop-blur-xl bg-black/60" />
            <div className="relative mx-auto max-w-lg mt-24 p-0">
              <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 20, opacity: 0 }} className="glass-card p-6 md:p-6 lg:p-8">
                <h2 className="text-2xl md:text-3xl font-semibold mb-2">Consent Required</h2>
                <p className="text-text-secondary text-sm md:text-base">We use data to provide services. Please review and accept to continue.</p>
                <div className="mt-4 flex gap-2">
                  <button onClick={accept} className="btn-primary px-4">Accept</button>
                  <button onClick={reject} className="glass-button-secondary px-4">Reject</button>
                </div>
                <div className="mt-4 text-xs text-text-muted flex flex-wrap gap-3">
                  <Link to="/legal/consent" className="underline">Consent</Link>
                  <Link to="/legal/privacy" className="underline">Privacy Policy</Link>
                  <Link to="/legal/terms" className="underline">Terms of Service</Link>
                  <Link to="/legal/impressum" className="underline">Impressum</Link>
                  <Link to="/legal/cookies" className="underline">Cookies Policy</Link>
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
