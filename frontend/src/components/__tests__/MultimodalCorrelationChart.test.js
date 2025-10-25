import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import { MultimodalCorrelationChart } from '../../components/MultimodalCorrelationChart'

class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
window.ResizeObserver = window.ResizeObserver || ResizeObserver

const mockData = Array.from({ length: 10 }).map(() => ({
  sentiment: Math.random(),
  brightness: Math.random() * 100,
  sales: Math.random() * 2000 + 500,
  variance: (Math.random() - 0.5) * 0.6,
}))

describe('MultimodalCorrelationChart', () => {
  test('renders without crashing', () => {
    render(<MultimodalCorrelationChart data={mockData} />)
    expect(screen.getByText(/Multimodal Correlation/i)).toBeInTheDocument()
  })

  test('tooltip appears on hover over a dot', async () => {
    const user = userEvent.setup()
    const { container } = render(<MultimodalCorrelationChart data={mockData} />)
    const circle = container.querySelector('circle')
    if (circle) {
      await user.hover(circle)
      expect(await screen.findByText(/datapoint/i)).toBeInTheDocument()
    }
  })

  test('renders regression line', () => {
    const { container } = render(<MultimodalCorrelationChart data={mockData} />)
    const paths = Array.from(container.querySelectorAll('path'))
    const line = paths.find(p => (p.getAttribute('stroke') || '').toLowerCase() === '#4ade80')
    expect(line).toBeTruthy()
  })
})
