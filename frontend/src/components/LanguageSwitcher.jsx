import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'

const localeKey = 'app-locale'

export const LanguageSwitcher = ({ className = '' }) => {
  const { i18n } = useTranslation()

  const setLocale = (lng) => {
    i18n.changeLanguage(lng)
    localStorage.setItem(localeKey, lng)
  }

  useEffect(() => {
    const saved = localStorage.getItem(localeKey)
    if (saved && saved !== i18n.language) {
      i18n.changeLanguage(saved)
    }
  }, [])

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('dir', i18n.dir())
      document.documentElement.setAttribute('lang', i18n.language)
    }
  }, [i18n.language])

  return (
    <div className={`inline-flex rounded-lg border border-dark-border overflow-hidden ${className}`} role="group" aria-label="Language switcher">
      <button
        onClick={() => setLocale('en')}
        className={`px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 ${i18n.language === 'en' ? 'bg-dark-hover text-text-primary' : 'text-text-secondary'}`}
        aria-pressed={i18n.language === 'en'}
      >
        EN
      </button>
      <button
        onClick={() => setLocale('ar')}
        className={`px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 ${i18n.language === 'ar' ? 'bg-dark-hover text-text-primary' : 'text-text-secondary'}`}
        aria-pressed={i18n.language === 'ar'}
      >
        AR
      </button>
    </div>
  )
}

export default LanguageSwitcher
