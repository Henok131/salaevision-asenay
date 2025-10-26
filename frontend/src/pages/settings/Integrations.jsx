import IntegrationStatusCard from '../../components/IntegrationStatusCard'
import { useTranslation } from 'react-i18next'

export default function Integrations() {
  const { t } = useTranslation()
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-2">{t('integrations') || 'Integrations'}</h1>
      <p className="text-gray-600 mb-4">{t('integrations_desc') || 'Manage tool connections driven by .env.'}</p>
      <IntegrationStatusCard />
    </div>
  )
}
