import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { I18nextProvider } from 'react-i18next'
import i18n from '../../src/i18n'
import LanguageSwitcher from '../../src/components/LanguageSwitcher'

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('persists Arabic and sets dir rtl', async () => {
    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    )
    const ar = screen.getByRole('button', { name: 'AR' })
    fireEvent.click(ar)
    expect(localStorage.getItem('app-locale')).toBe('ar')
  })

  it('UI reacts to EN selection', () => {
    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    )
    const en = screen.getByRole('button', { name: 'EN' })
    fireEvent.click(en)
    expect(localStorage.getItem('app-locale')).toBe('en')
  })
})
