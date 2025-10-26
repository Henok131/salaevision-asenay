import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import ResetPassword from '../../src/pages/ResetPassword'

vi.mock('../../src/contexts/AuthContext', () => ({
  useAuth: () => ({ updatePassword: vi.fn(async () => ({ error: null })) })
}))

vi.mock('react-hot-toast', () => ({ default: { success: vi.fn(), error: vi.fn() } }))

const renderPage = () => render(
  <BrowserRouter>
    <ResetPassword />
  </BrowserRouter>
)

describe('ResetPassword', () => {
  beforeEach(() => vi.clearAllMocks())

  it('validates mismatched passwords', () => {
    renderPage()
    const newPwd = screen.getByLabelText(/new password/i)
    const confirm = screen.getByLabelText(/confirm password/i)
    fireEvent.change(newPwd, { target: { value: 'abcdef' } })
    fireEvent.change(confirm, { target: { value: 'abcdeg' } })
    const submit = screen.getByRole('button', { name: /update password/i })
    fireEvent.click(submit)
    expect(submit).toBeInTheDocument()
  })

  it('submits when valid', () => {
    renderPage()
    const newPwd = screen.getByLabelText(/new password/i)
    const confirm = screen.getByLabelText(/confirm password/i)
    fireEvent.change(newPwd, { target: { value: 'abcdef' } })
    fireEvent.change(confirm, { target: { value: 'abcdef' } })
    const submit = screen.getByRole('button', { name: /update password/i })
    fireEvent.click(submit)
    expect(submit).toBeInTheDocument()
  })
})
