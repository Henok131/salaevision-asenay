import { renderHook, act } from '@testing-library/react'
import useVoiceNarration from '../../hooks/useVoiceNarration'

// Mock SpeechSynthesis API
const speak = jest.fn()
const cancel = jest.fn()

beforeAll(() => {
  Object.defineProperty(window, 'speechSynthesis', {
    writable: true,
    value: {
      speak,
      cancel,
      getVoices: () => [{ name: 'Test Voice', lang: 'en-US' }],
      onvoiceschanged: null,
    },
  })
})

describe('useVoiceNarration', () => {
  test('returns narrate function', () => {
    const { result } = renderHook(() => useVoiceNarration())
    expect(typeof result.current.narrateInsight).toBe('function')
  })

  test('narration triggers when enabled', () => {
    const { result } = renderHook(() => useVoiceNarration())
    act(() => {
      result.current.setEnabled(true)
      result.current.narrateInsight('Sales jumped due to high engagement.')
    })
    expect(speak).toHaveBeenCalled()
  })
})
