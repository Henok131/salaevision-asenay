export default function InvoiceViewer({ fileUrl, parsed }) {
  return (
    <div className="space-y-3">
      <div className="border rounded p-3">
        <h3 className="font-semibold mb-2">Preview</h3>
        {fileUrl?.endsWith('.pdf') ? (
          <iframe src={fileUrl} className="w-full h-96" title="invoice" />
        ) : (
          // Image fallback
          <img src={fileUrl} alt="invoice" className="max-h-96" />
        )}
      </div>
      <div className="border rounded p-3">
        <h3 className="font-semibold mb-2">Parsed Data</h3>
        <pre className="text-sm bg-gray-50 p-2 rounded overflow-auto">{JSON.stringify(parsed, null, 2)}</pre>
      </div>
    </div>
  )
}
