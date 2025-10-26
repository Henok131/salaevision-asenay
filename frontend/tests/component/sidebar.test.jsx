import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Sidebar } from '../../src/components/Sidebar'

const Wrapper = ({ children }) => <div>{children}</div>

describe('Sidebar', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('toggles collapsed state and persists', () => {
    render(
      <Wrapper>
        <Sidebar activeTab="dashboard" setActiveTab={() => {}} isOpen={true} setIsOpen={() => {}} />
      </Wrapper>
    )
    const toggle = screen.getByRole('button', { name: /collapse sidebar|expand sidebar/i })
    fireEvent.click(toggle)
    expect(localStorage.getItem('sidebar-collapsed')).toBeDefined()
  })
})
