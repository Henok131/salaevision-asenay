#!/usr/bin/env node
const required = [
  'VITE_APP_NAME',
  'VITE_FRONTEND_URL',
  'VITE_DEFAULT_LOCALE',
  'VITE_SUPPORTED_LOCALES',
  'VITE_API_URL',
  'VITE_SUPABASE_URL',
  'VITE_SUPABASE_ANON_KEY'
]

const missing = required.filter(k => !process.env[k])
if (missing.length) {
  console.error('Missing required environment variables:', missing.join(', '))
  process.exit(1)
} else {
  console.log('All required VITE_ env variables are set.')
}
