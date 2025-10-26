import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Eye, EyeOff, Mail, Lock, BarChart3, Github, Phone, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'
import asenayLogo from '../assets/asenay-logo.svg'

export const Login = () => {
  const { t } = useTranslation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { signIn, signInWithOAuth, resetPassword } = useAuth()
  const navigate = useNavigate()
  const [phone, setPhone] = useState('')
  const [otpRequested, setOtpRequested] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const { error } = await signIn(email, password)
      if (error) {
        toast.error(error.message)
      } else {
        toast.success(t('auth.welcome_back', 'Welcome back!'))
        navigate('/dashboard')
      }
    } catch (error) {
      toast.error(t('auth.login_failed', 'Login failed. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    toast.loading(t('auth.redirecting', 'Redirecting to Google...'), { id: 'oauth' })
    await signInWithOAuth('google')
  }

  const handleGithubLogin = async () => {
    toast.loading(t('auth.redirecting', 'Redirecting to GitHub...'), { id: 'oauth' })
    await signInWithOAuth('github')
  }

  const handleRequestOtp = async (e) => {
    e.preventDefault()
    if (!phone) {
      toast.error(t('auth.enter_phone', 'Please enter your phone number'))
      return
    }
    setOtpRequested(true)
    toast.success(t('auth.otp_sent', 'OTP sent to your phone'))
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <div className="pt-16">
        <div className="max-w-screen-2xl 2xl:max-w-[1440px] mx-auto px-4 md:px-6 lg:px-8 py-4 md:py-6 lg:py-8 flex items-center justify-center">
      <div className="max-w-md w-full">
        {/* Centered logo + heading */}
        <div className="text-center mb-8" role="banner">
          <img src={asenayLogo} alt="Asenay Tech" className="h-12 w-12 mx-auto mb-3" />
          <h1 className="text-3xl md:text-4xl font-bold text-white">{t('auth.sign_in_to', 'Sign in to Asenay')}</h1>
          <p className="text-gray-300 text-sm md:text-base leading-relaxed mt-2">{t('auth.use_company_account', 'Use your company account to continue')}</p>
        </div>

        {/* Login Form */}
        <div className="glass-card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
                Email address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-3 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent-from focus:border-transparent"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-white mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-10 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent-from focus:border-transparent"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70 rounded-md"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-white" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-white" />
                  )}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-accent-from focus:ring-accent-from border-gray-300 rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-300">
                  Remember me
                </label>
              </div>

              <div className="text-sm">
            <button
              type="button"
              onClick={async () => {
                if (!email) {
                  toast.error(t('auth.enter_email_reset', 'Enter your email to reset password'))
                  return
                }
                const { error } = await resetPassword(email)
                if (error) toast.error(error.message)
                else toast.success(t('auth.reset_sent', 'Password reset email sent'))
              }}
              className="text-accent-from hover:text-accent-to transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-from/70 rounded"
            >
              {t('auth.forgot_password', 'Forgot your password?')}
            </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full glass-button btn-primary flex items-center justify-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/20" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-dark-bg text-gray-400">Or continue with</span>
              </div>
            </div>

            <div className="mt-6 grid grid-cols-3 gap-3">
              <button onClick={handleGoogleLogin} className="w-full glass-button-secondary flex items-center justify-center" aria-label="Continue with Google">
                <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Google
              </button>
              <button onClick={handleGithubLogin} className="w-full glass-button-secondary flex items-center justify-center" aria-label="Continue with GitHub">
                <Github className="h-5 w-5 mr-2" />
                GitHub
              </button>
              <button disabled className="w-full glass-button-secondary opacity-60 cursor-not-allowed flex items-center justify-center" aria-label="Continue with Facebook">
                <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12c0 4.84 3.44 8.86 7.93 9.8v-6.93H7.9v-2.87h2.03V9.41c0-2 1.2-3.1 3.03-3.1.88 0 1.8.16 1.8.16v1.98h-1.02c-1 0-1.31.62-1.31 1.26v1.51h2.23l-.36 2.87h-1.87V21.8C18.56 20.86 22 16.84 22 12c0-5.52-4.48-10-10-10z"/></svg>
                Facebook
              </button>
            </div>
          </div>

          {/* Phone login (OTP) intentionally removed per requirements */}

          <div className="mt-6 text-center">
            <p className="text-gray-300">
              {t('auth.no_account', "Don't have an account?")} {' '}
              <Link to="/signup" className="text-accent-from hover:text-accent-to transition-colors">
                {t('auth.sign_up_free', 'Sign up for free')}
              </Link>
            </p>
          </div>
      </div>
        </div>
      </div>
    </div>
  )
}
