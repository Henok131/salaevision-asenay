import { useTranslation } from 'react-i18next'

export default function Timeline() {
  const { t } = useTranslation()
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">{t('timeline')}</h1>
      <p className="text-gray-600">Interaction history. (Placeholder)</p>
    </div>
  )
}
