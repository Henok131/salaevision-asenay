import { useState } from 'react'
import { Check, Star, Zap } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export const Pricing = () => {
  const { user } = useAuth()
  const [billingCycle, setBillingCycle] = useState('monthly')

  const plans = [
    {
      name: 'Free',
      price: { monthly: 0, yearly: 0 },
      description: 'Perfect for getting started',
      features: [
        '2 analyses per month',
        'Basic insights',
        'CSV upload',
        'Email support',
        '7-day data retention'
      ],
      limitations: [
        'Limited to 1,000 data points',
        'Basic forecasting',
        'No advanced analytics'
      ],
      popular: false,
      buttonText: 'Get Started Free',
      buttonStyle: 'glass-button-secondary'
    },
    {
      name: 'Pro',
      price: { monthly: 19, yearly: 190 },
      description: 'For growing businesses',
      features: [
        '100 analyses per month',
        'Advanced AI insights',
        'CSV & Google Sheets',
        'Priority support',
        '30-day data retention',
        'Custom dashboards',
        'Export reports',
        'API access'
      ],
      limitations: [],
      popular: true,
      buttonText: 'Start Pro Trial',
      buttonStyle: 'glass-button'
    },
    {
      name: 'Business',
      price: { monthly: 49, yearly: 490 },
      description: 'For enterprise teams',
      features: [
        'Unlimited analyses',
        'Premium AI insights',
        'All data sources',
        '24/7 support',
        'Unlimited data retention',
        'Custom dashboards',
        'Advanced reporting',
        'Full API access',
        'Team collaboration',
        'White-label options'
      ],
      limitations: [],
      popular: false,
      buttonText: 'Contact Sales',
      buttonStyle: 'glass-button'
    }
  ]

  const handlePlanSelect = (plan) => {
    if (plan.name === 'Free') {
      // Redirect to signup
      window.location.href = '/signup'
    } else if (plan.name === 'Pro') {
      // Redirect to Stripe checkout
      window.location.href = '/checkout/pro'
    } else {
      // Contact sales
      const salesEmail = import.meta.env.VITE_SALES_EMAIL || 'sales@example.com'
      window.location.href = `mailto:${salesEmail}`
    }
  }

  return (
    <div className="min-h-screen bg-dark-bg py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-white mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Start with our free plan and upgrade as you grow
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4">
            <span className={`text-sm ${billingCycle === 'monthly' ? 'text-white' : 'text-gray-400'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-accent-from focus:ring-offset-2 focus:ring-offset-dark-bg"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-sm ${billingCycle === 'yearly' ? 'text-white' : 'text-gray-400'}`}>
              Yearly
            </span>
            {billingCycle === 'yearly' && (
              <span className="ml-2 px-2 py-1 bg-accent-from text-white text-xs rounded-full">
                Save 20%
              </span>
            )}
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`glass-card p-8 relative ${
                plan.popular ? 'ring-2 ring-accent-from' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-accent text-white px-4 py-1 rounded-full text-sm font-semibold flex items-center space-x-1">
                    <Star className="h-4 w-4" />
                    <span>Most Popular</span>
                  </div>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <p className="text-gray-300 mb-4">{plan.description}</p>
                <div className="mb-4">
                  <span className="text-4xl font-bold text-white">
                    ${plan.price[billingCycle]}
                  </span>
                  <span className="text-gray-400">
                    /{billingCycle === 'monthly' ? 'month' : 'year'}
                  </span>
                </div>
                {billingCycle === 'yearly' && plan.price.yearly > 0 && (
                  <p className="text-sm text-gray-400">
                    ${Math.round(plan.price.yearly / 12)}/month billed annually
                  </p>
                )}
              </div>

              <button
                onClick={() => handlePlanSelect(plan)}
                className={`w-full ${plan.buttonStyle} mb-6`}
              >
                {plan.buttonText}
              </button>

              <div className="space-y-3">
                <h4 className="text-white font-semibold">Features:</h4>
                {plan.features.map((feature, featureIndex) => (
                  <div key={featureIndex} className="flex items-start space-x-2">
                    <Check className="h-5 w-5 text-accent-from flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300 text-sm">{feature}</span>
                  </div>
                ))}
              </div>

              {plan.limitations.length > 0 && (
                <div className="mt-6 pt-6 border-t border-white/20">
                  <h4 className="text-white font-semibold mb-3">Limitations:</h4>
                  {plan.limitations.map((limitation, limitIndex) => (
                    <div key={limitIndex} className="flex items-start space-x-2">
                      <div className="h-5 w-5 flex-shrink-0 mt-0.5">
                        <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                      </div>
                      <span className="text-gray-400 text-sm">{limitation}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="glass-card p-8">
          <h2 className="text-2xl font-bold text-white mb-8 text-center">
            Frequently Asked Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                What data formats do you support?
              </h3>
              <p className="text-gray-300">
                We support CSV files and Google Sheets integration. More formats coming soon.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                How accurate are the forecasts?
              </h3>
              <p className="text-gray-300">
                Our AI models achieve 85-95% accuracy depending on data quality and historical patterns.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Can I cancel anytime?
              </h3>
              <p className="text-gray-300">
                Yes, you can cancel your subscription at any time. No long-term contracts.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Is my data secure?
              </h3>
              <p className="text-gray-300">
                Absolutely. We use enterprise-grade security and never share your data with third parties.
              </p>
            </div>
          </div>
        </div>

        {/* Enterprise CTA */}
        <div className="text-center mt-16">
          <div className="glass-card p-8 max-w-2xl mx-auto">
            <Zap className="h-12 w-12 text-accent-from mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-white mb-4">
              Need a Custom Solution?
            </h3>
            <p className="text-gray-300 mb-6">
              We offer custom enterprise solutions with dedicated support, custom integrations, and advanced features.
            </p>
            <button className="glass-button">
              Contact Enterprise Sales
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

