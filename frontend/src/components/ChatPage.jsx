import { useState, useEffect } from 'react'
import { getDocuments, ingestDocument, deleteDocument } from '../api/documents.js'
import { askQuestion } from '../api/query.js'
import Header from './Header.jsx'
import MessageList from './MessageList.jsx'
import InputBar from './InputBar.jsx'

export default function ChatPage({ username, onLogout }) {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [currentFile, setCurrentFile] = useState(null)
  const [currentDocId, setCurrentDocId] = useState(null)
  const [dbReady, setDbReady] = useState(false)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    getDocuments().then(({ ok, data }) => {
      if (ok && data.length > 0) {
        setDbReady(true)
        setCurrentFile(data[0].filename)
        setCurrentDocId(data[0].id)
      }
    })
  }, [])

  const handleFileSelect = async (file) => {
    if (!file) return
    setUploading(true)
    setUploadStatus(null)

    const { ok, data } = await ingestDocument(file)

    setUploading(false)
    if (ok) {
      setUploadStatus({ ok: true, text: `"${file.name}" ingested — ${data.chunks} chunks stored` })
      setCurrentFile(file.name)
      setCurrentDocId(data.document_id)
      setDbReady(true)
      setMessages([])
    } else {
      setUploadStatus({ ok: false, text: data.error })
    }
  }

  const handleDeleteDocument = async () => {
    if (!currentDocId || deleting) return
    setDeleting(true)

    const { ok, data } = await deleteDocument(currentDocId)

    setDeleting(false)
    if (ok) {
      setMessages([])
      setUploadStatus(null)
      // Reload remaining documents — user may have had more than one
      const { ok: docsOk, data: docs } = await getDocuments()
      if (docsOk && docs.length > 0) {
        setCurrentFile(docs[0].filename)
        setCurrentDocId(docs[0].id)
        setDbReady(true)
      } else {
        setCurrentFile(null)
        setCurrentDocId(null)
        setDbReady(false)
      }
    } else {
      setUploadStatus({ ok: false, text: data.error || 'Failed to remove document' })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const q = question.trim()
    if (!q || loading) return

    setMessages(prev => [...prev, { id: crypto.randomUUID(), role: 'user', text: q }])
    setQuestion('')
    setLoading(true)

    const { ok, data } = await askQuestion(q)

    setLoading(false)
    setMessages(prev => [...prev, ok
      ? { id: crypto.randomUUID(), role: 'assistant', text: data.answer, sources: data.sources, pages: data.pages }
      : { id: crypto.randomUUID(), role: 'error', text: data.error }
    ])
  }

  const emptyHint = dbReady
    ? `Knowledge base ready — ask anything about "${currentFile}"`
    : 'Upload a PDF to get started.'

  return (
    <div className="app">
      <Header
        username={username}
        uploading={uploading}
        onFileSelect={handleFileSelect}
        onLogout={onLogout}
      />

      {uploadStatus && (
        <div className={`banner ${uploadStatus.ok ? 'ok' : 'err'}`}>
          {uploadStatus.text}
        </div>
      )}
      {!uploadStatus && currentFile && (
        <div className="banner ok doc-banner">
          <span>📎 Active document: <strong>{currentFile}</strong></span>
          <button
            className="remove-doc-btn"
            onClick={handleDeleteDocument}
            disabled={deleting}
            title="Remove this document"
          >
            {deleting ? '…' : '🗑 Remove'}
          </button>
        </div>
      )}

      <MessageList
        messages={messages}
        loading={loading}
        emptyHint={emptyHint}
      />

      <InputBar
        value={question}
        onChange={setQuestion}
        onSubmit={handleSubmit}
        disabled={!dbReady || loading}
      />
    </div>
  )
}
