import { useMemo } from 'react'

const CopyEmbedCode = ({ publicId }) => {
  const src = useMemo(() => {
    const base = import.meta.env.VITE_PUBLIC_APP_URL || window.location.origin
    return `${base}/embed/${publicId}`
  }, [publicId])

  const embedCode = `<iframe src="${src}" width="600" height="400" frameborder="0"></iframe>`

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(embedCode)
    } catch {}
  }

  return (
    <div className="p-4 bg-gradient-glass border border-accent-from/30 rounded-lg">
      <div className="text-xs text-text-secondary mb-2">Embed Code</div>
      <code className="block text-xs text-text-primary break-all mb-3">{embedCode}</code>
      <button onClick={handleCopy} className="px-3 py-2 bg-dark-hover border border-dark-border rounded text-sm text-text-primary hover:text-white">Copy</button>
    </div>
  )
}

export default CopyEmbedCode
