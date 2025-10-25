import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * useVoiceNarration
 * Lightweight wrapper around SpeechSynthesis for narrating AI insights.
 *
 * Usage:
 * const { enabled, setEnabled, narrateInsight, speaking } = useVoiceNarration()
 * setEnabled(true)
 * narrateInsight('Sales jumped due to high engagement.')
 */
export default function useVoiceNarration(options = {}) {
  const {
    pitch = 1.0,
    rate = 1.0,
    volume = 1.0,
    voiceName, // optional preferred voice
  } = options

  const [enabled, setEnabled] = useState(false)
  const [speaking, setSpeaking] = useState(false)
  const utterRef = useRef(null)
  const voiceRef = useRef(null)

  // Load voices (browsers load asynchronously)
  useEffect(() => {
    if (!('speechSynthesis' in window)) return

    const loadVoices = () => {
      const voices = window.speechSynthesis.getVoices()
      if (voiceName) {
        voiceRef.current = voices.find(v => v.name === voiceName) || null
      } else {
        // pick a sensible default: prefer English female voice when present
        voiceRef.current = voices.find(v => /en-/i.test(v.lang) && /female/i.test(v.name)) || voices.find(v => /en-/i.test(v.lang)) || null
      }
    }

    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices

    return () => {
      window.speechSynthesis.onvoiceschanged = null
    }
  }, [voiceName])

  const cancel = useCallback(() => {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    setSpeaking(false)
  }, [])

  const narrateInsight = useCallback((text) => {
    if (!enabled) return
    if (!('speechSynthesis' in window)) return
    if (!text || typeof text !== 'string') return

    // Cancel any ongoing speech
    window.speechSynthesis.cancel()

    const utter = new SpeechSynthesisUtterance(text)
    utter.pitch = pitch
    utter.rate = rate
    utter.volume = volume
    if (voiceRef.current) utter.voice = voiceRef.current

    utter.onstart = () => setSpeaking(true)
    utter.onend = () => setSpeaking(false)
    utter.onerror = () => setSpeaking(false)

    utterRef.current = utter
    window.speechSynthesis.speak(utter)
  }, [enabled, pitch, rate, volume])

  return { enabled, setEnabled, narrateInsight, speaking, cancel }
}
