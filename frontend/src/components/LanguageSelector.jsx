import i18n from 'i18next'
import { useEffect } from 'react'

const langs = [
  { code: 'en', label: 'EN', dir: 'ltr' },
  { code: 'de', label: 'DE', dir: 'ltr' },
  { code: 'fr', label: 'FR', dir: 'ltr' },
  { code: 'es', label: 'ES', dir: 'ltr' },
  { code: 'ar', label: 'AR', dir: 'rtl' },
]

export default function LanguageSelector() {
  useEffect(() => {
    const dir = i18n.dir()
    document.documentElement.dir = dir
  }, [])

  const changeLang = async (code, dir) => {
    await i18n.changeLanguage(code)
    document.documentElement.dir = dir
    localStorage.setItem('i18nextLng', code)
  }

  return (
    <div className="text-xs text-gray-600 hidden sm:flex items-center gap-1">
      {langs.map((l, i) => (
        <button key={l.code} onClick={() => changeLang(l.code, l.dir)} className="px-1 hover:underline">
          {l.label}{i < langs.length - 1 ? ' |' : ''}
        </button>
      ))}
    </div>
  )
}
