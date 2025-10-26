import { useTranslation } from 'react-i18next'

export default function Leads() {
  const { t } = useTranslation()
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">{t('leads')}</h1>
      <p className="text-gray-600">View and score leads. (Placeholder)</p>
    </div>
  )
}
