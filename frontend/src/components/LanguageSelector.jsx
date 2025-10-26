const langs = ['EN', 'DE', 'FR', 'ES', 'AR']

export default function LanguageSelector() {
  return (
    <div className="text-xs text-gray-600 hidden sm:block">
      {langs.map((l, i) => (
        <span key={l} className="px-1">
          {l}{i < langs.length - 1 ? ' |' : ''}
        </span>
      ))}
    </div>
  )
}
