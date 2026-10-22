// API types matching backend schemas

export interface Document {
  id: string
  title: string
  content_type: string
  file_name: string | null
  size_bytes: number
  status: 'pending' | 'processing' | 'completed' | 'error' | 'failed'
  chunk_count: number
  created_at: string
  updated_at: string
  metadata: Record<string, unknown> | null
}

export interface SourceChunk {
  id: string
  document_id: string
  content: string
  score: number
  title: string | null
  source_url: string | null
}

export interface RAGResponse {
  answer: string
  sources: SourceChunk[]
  question: string
  conversation_id: string | null
  retrieved_at: string
  grounding_score: number
}

export interface QuestionRequest {
  question: string
  conversation_id?: string
  context?: Record<string, unknown>
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'partial'
  service: string
  version: string
  checks: Record<string, string>
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: SourceChunk[]
  timestamp: string
  isLoading?: boolean
}

