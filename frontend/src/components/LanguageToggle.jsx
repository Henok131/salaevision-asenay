import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'

const localeKey = 'app-locale'

export const LanguageToggle = () => {
  const { i18n } = useTranslation()

  const toggle = () => {
    const next = i18n.language === 'ar' ? 'en' : 'ar'
    i18n.changeLanguage(next)
    localStorage.setItem(localeKey, next)
  }

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('dir', i18n.dir())
      document.documentElement.setAttribute('lang', i18n.language)
    }
  }, [i18n.language])

  useEffect(() => {
    const saved = localStorage.getItem(localeKey)
    if (saved && saved !== i18n.language) {
      i18n.changeLanguage(saved)
    }
  }, [i18n.language])

  return (
    <button
      onClick={toggle}
      className="btn-primary px-3 py-2 rounded-lg text-sm"
      aria-label="Toggle language"
    >
      {i18n.language === 'ar' ? 'EN' : 'AR'}
    </button>
  )
}

export default LanguageToggle
