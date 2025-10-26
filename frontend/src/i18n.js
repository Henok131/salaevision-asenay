import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import en from './i18n/en.json'
import de from './i18n/de.json'
import fr from './i18n/fr.json'
import es from './i18n/es.json'
import ar from './i18n/ar.json'

const resources = { en: { translation: en }, de: { translation: de }, fr: { translation: fr }, es: { translation: es }, ar: { translation: ar } }

const defaultLng = import.meta.env.VITE_DEFAULT_LANGUAGE || 'en'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    lng: defaultLng,
    detection: { order: ['querystring', 'localStorage', 'navigator'], caches: ['localStorage'] },
    interpolation: { escapeValue: false },
    returnEmptyString: false,
  })

export default i18n
