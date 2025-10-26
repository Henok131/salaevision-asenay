import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

const MIN_LEN = 6

export const ResetPassword = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { updatePassword } = useAuth()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!password || password.length < MIN_LEN) {
      toast.error(t('auth.password_length', `Password must be at least ${MIN_LEN} characters`))
      return
    }
    if (password !== confirm) {
      toast.error(t('auth.password_mismatch', 'Passwords do not match'))
      return
    }
    setLoading(true)
    const { error } = await updatePassword(password)
    setLoading(false)
    if (error) {
      toast.error(error.message || t('auth.reset_failed', 'Password reset failed'))
      return
    }
    toast.success(t('auth.reset_success', 'Password updated successfully'))
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-dark-bg pt-16">
      <div className="max-w-screen-2xl 2xl:max-w-[1440px] mx-auto px-4 md:px-6 lg:px-8 py-4 md:py-6 lg:py-8">
        <div className="mx-auto max-w-md">
          <div className="glass-card p-6 md:p-6 lg:p-8">
            <h1 className="text-2xl md:text-3xl font-semibold mb-4">{t('auth.reset_password', 'Reset your password')}</h1>
            <p className="text-text-secondary text-sm md:text-base mb-6">{t('auth.reset_instructions', 'Enter and confirm your new password')}</p>
            <form onSubmit={onSubmit} className="space-y-4" aria-label="Reset password form">
              <div>
                <label htmlFor="new-password" className="block text-sm font-medium text-white mb-2">{t('auth.new_password', 'New password')}</label>
                <input
                  id="new-password"
                  name="new-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full px-3 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent-from focus:border-transparent"
                  placeholder={t('auth.enter_new_password', 'Enter new password')}
                  minLength={MIN_LEN}
                  required
                />
              </div>
              <div>
                <label htmlFor="confirm-password" className="block text-sm font-medium text-white mb-2">{t('auth.confirm_password', 'Confirm password')}</label>
                <input
                  id="confirm-password"
                  name="confirm-password"
                  type="password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  className="block w-full px-3 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent-from focus:border-transparent"
                  placeholder={t('auth.confirm_password_placeholder', 'Confirm new password')}
                  minLength={MIN_LEN}
                  required
                />
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center">
                {loading ? t('auth.saving', 'Saving...') : t('auth.update_password', 'Update password')}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResetPassword
