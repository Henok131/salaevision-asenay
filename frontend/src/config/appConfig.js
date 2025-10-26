export const appConfig = {
  apiUrl: import.meta.env.VITE_API_URL,
  appName: import.meta.env.VITE_APP_NAME,
  frontendUrl: import.meta.env.VITE_FRONTEND_URL,
  defaultLocale: import.meta.env.VITE_DEFAULT_LOCALE,
  supportedLocales: (import.meta.env.VITE_SUPPORTED_LOCALES || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean),
  stripePublishableKey: import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY,
  supabaseUrl: import.meta.env.VITE_SUPABASE_URL,
  supabaseAnonKey: import.meta.env.VITE_SUPABASE_ANON_KEY,
}

export default appConfig
