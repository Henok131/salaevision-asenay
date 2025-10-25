import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

export async function downloadDashboardPDF({
  chartSelector = '#multimodal-corr-chart',
  summaryText = '',
  userLabel = 'User',
}) {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' })
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()

  // Header
  const title = 'SalesVision XAI-360 — Analytics Report'
  const dateStr = new Date().toLocaleString()
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.text(title, 40, 50)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(10)
  doc.text(`Generated: ${dateStr}`, 40, 68)
  if (userLabel) doc.text(`User: ${userLabel}`, 40, 82)

  // Chart screenshot
  const chartEl = document.querySelector(chartSelector)
  if (chartEl) {
    const canvas = await html2canvas(chartEl, { backgroundColor: '#0b1020', scale: 2 })
    const imgData = canvas.toDataURL('image/png')
    const imgW = pageWidth - 80
    const imgH = (canvas.height * imgW) / canvas.width
    doc.addImage(imgData, 'PNG', 40, 100, imgW, Math.min(imgH, 350))
  } else {
    doc.setTextColor('#ff7ad9')
    doc.text('Chart not found on page.', 40, 120)
    doc.setTextColor('#000000')
  }

  // AI Summary
  const summaryTop = 480
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(12)
  doc.text('AI Summary', 40, summaryTop)
  doc.setFont('helvetica', 'normal')
  doc.setFontSize(11)
  const wrapped = doc.splitTextToSize(summaryText || 'No summary available.', pageWidth - 80)
  doc.text(wrapped, 40, summaryTop + 20)

  doc.save(`SalesVision-Report-${new Date().toISOString().slice(0, 10)}.pdf`)
}
