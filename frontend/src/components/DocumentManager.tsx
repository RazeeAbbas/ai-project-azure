import React, { useState, useRef, useCallback, useEffect } from 'react'
import { useStore } from '../store'
import { listDocuments, uploadDocument, deleteDocument } from '../api'
import { Document } from '../types'

const StatusBadge: React.FC<{ status: Document['status'] }> = ({ status }) => {
  const colors: Record<Document['status'], string> = {
    pending: '#f59e0b',
    processing: '#3b82f6',
    completed: '#22c55e',
    error: '#ef4444',
    failed: '#ef4444',
  }
  return (
    <span style={{
      background: colors[status] + '22',
      color: colors[status],
      border: `1px solid ${colors[status]}44`,
      borderRadius: 12,
      padding: '2px 8px',
      fontSize: 11,
      fontWeight: 600,
      textTransform: 'uppercase',
    }}>
      {status}
    </span>
  )
}

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export const DocumentManager: React.FC = () => {
  const { documents, setDocuments, addDocument, removeDocument } = useStore()
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const loadDocuments = useCallback(async () => {
    setLoading(true)
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [setDocuments])

  useEffect(() => { loadDocuments() }, [loadDocuments])

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setUploading(true)
    setError(null)
    setSuccess(null)

    for (const file of Array.from(files)) {
      try {
        const doc = await uploadDocument(file, file.name)
        addDocument(doc)
        setSuccess(`✅ "${file.name}" uploaded successfully`)
      } catch (e: unknown) {
        setError(`❌ Failed to upload "${file.name}": ${e instanceof Error ? e.message : 'Unknown error'}`)
      }
    }
    setUploading(false)
  }

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Delete "${title}"?`)) return
    try {
      await deleteDocument(id)
      removeDocument(id)
      setSuccess(`Deleted "${title}"`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to delete')
    }
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleUpload(e.dataTransfer.files)
  }

  return (
    <div style={{ padding: 16, height: '100%', overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600 }}>📄 Documents</h2>
        <button
          onClick={loadDocuments}
          style={{
            background: 'transparent',
            border: '1px solid var(--border)',
            borderRadius: 6,
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '4px 10px',
            fontSize: 12,
          }}
        >
          ↻ Refresh
        </button>
      </div>

      {/* Upload Zone */}
      <div
        onDrop={onDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onClick={() => fileRef.current?.click()}
        style={{
          border: `2px dashed ${isDragging ? 'var(--accent)' : 'var(--border)'}`,
          borderRadius: 'var(--radius)',
          padding: 32,
          textAlign: 'center',
          cursor: 'pointer',
          marginBottom: 16,
          background: isDragging ? 'var(--accent)11' : 'transparent',
          transition: 'all 0.2s',
        }}
      >
        <div style={{ fontSize: 32, marginBottom: 8 }}>📁</div>
        <p style={{ color: 'var(--text-primary)', fontWeight: 600, marginBottom: 4 }}>
          {uploading ? 'Uploading…' : 'Drop files here or click to browse'}
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
          Supported: PDF, DOCX, TXT, MD, HTML, JSON
        </p>
        <input
          ref={fileRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md,.html,.json"
          style={{ display: 'none' }}
          onChange={(e) => handleUpload(e.target.files)}
        />
      </div>

      {/* Alerts */}
      {error && (
        <div style={{ background: '#ef444422', border: '1px solid #ef4444', borderRadius: 6, padding: '8px 12px', marginBottom: 12, fontSize: 13, color: '#ef4444' }}>
          {error}
        </div>
      )}
      {success && (
        <div style={{ background: '#22c55e22', border: '1px solid #22c55e', borderRadius: 6, padding: '8px 12px', marginBottom: 12, fontSize: 13, color: '#22c55e' }}>
          {success}
        </div>
      )}

      {/* Document List */}
      {loading ? (
        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>Loading documents…</div>
      ) : documents.length === 0 ? (
        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>
          No documents yet. Upload some above!
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {documents.map((doc) => (
            <div key={doc.id} style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
              padding: '12px 14px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <span style={{ fontWeight: 600, fontSize: 14, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {doc.title}
                  </span>
                  <StatusBadge status={doc.status} />
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', gap: 12 }}>
                  <span>{doc.content_type}</span>
                  <span>{formatBytes(doc.size_bytes)}</span>
                  <span>{doc.chunk_count} chunks</span>
                  <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <button
                onClick={() => handleDelete(doc.id, doc.title)}
                style={{
                  background: 'transparent',
                  border: '1px solid #ef444466',
                  borderRadius: 6,
                  color: '#ef4444',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  fontSize: 12,
                  marginLeft: 12,
                  flexShrink: 0,
                }}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

