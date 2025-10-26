import { useTranslation } from 'react-i18next'

export default function Home() {
  const { t } = useTranslation()
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">{t('dashboard')}</h1>
      <p className="text-gray-600">Modular CRM dashboard scaffold. i18n ready.</p>
    </div>
  )
}
