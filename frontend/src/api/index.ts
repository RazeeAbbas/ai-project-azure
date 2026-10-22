import api from './client'
import { Document, RAGResponse, QuestionRequest, HealthStatus } from '../types'

// ──────────────────────────── Health ────────────────────────────
export const getHealth = (): Promise<HealthStatus> =>
  api.get('/health').then((r) => r.data)

// ──────────────────────────── Documents ────────────────────────────
export const listDocuments = (params?: { status?: string; content_type?: string }): Promise<Document[]> =>
  api.get('/documents', { params }).then((r) => r.data)

export const uploadDocument = (file: File, title?: string): Promise<Document> => {
  const form = new FormData()
  form.append('file', file)
  if (title) form.append('title', title)
  return api.post('/documents', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data)
}

export const getDocument = (id: string): Promise<Document> =>
  api.get(`/documents/${id}`).then((r) => r.data)

export const deleteDocument = (id: string): Promise<{ message: string }> =>
  api.delete(`/documents/${id}`).then((r) => r.data)

// ──────────────────────────── Q&A / RAG ────────────────────────────
export const askQuestion = (body: QuestionRequest): Promise<RAGResponse> =>
  api.post('/questions', body).then((r) => r.data)

