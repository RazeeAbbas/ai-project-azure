import { create } from 'zustand'
import { ChatMessage, Document } from '../types'
import { nanoid } from 'nanoid'

interface AppState {
  // Chat
  messages: ChatMessage[]
  conversationId: string | null
  addUserMessage: (text: string) => string
  addAssistantMessage: (id: string, content: string, sources?: ChatMessage['sources']) => void
  setMessageLoading: (id: string, loading: boolean) => void
  clearChat: () => void

  // Documents
  documents: Document[]
  setDocuments: (docs: Document[]) => void
  addDocument: (doc: Document) => void
  removeDocument: (id: string) => void
  updateDocument: (id: string, partial: Partial<Document>) => void

  // UI
  activeTab: 'chat' | 'documents' | 'health'
  setActiveTab: (tab: AppState['activeTab']) => void
  sidebarOpen: boolean
  toggleSidebar: () => void
}

export const useStore = create<AppState>((set) => ({
  // Chat
  messages: [],
  conversationId: null,
  addUserMessage: (text) => {
    const id = nanoid()
    const msg: ChatMessage = {
      id,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }
    set((s) => ({ messages: [...s.messages, msg] }))
    return id
  },
  addAssistantMessage: (id, content, sources) =>
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, content, sources, isLoading: false } : m
      ),
    })),
  setMessageLoading: (id, isLoading) =>
    set((s) => ({
      messages: s.messages.map((m) => (m.id === id ? { ...m, isLoading } : m)),
    })),
  clearChat: () => set({ messages: [], conversationId: null }),

  // Documents
  documents: [],
  setDocuments: (documents) => set({ documents }),
  addDocument: (doc) => set((s) => ({ documents: [doc, ...s.documents] })),
  removeDocument: (id) =>
    set((s) => ({ documents: s.documents.filter((d) => d.id !== id) })),
  updateDocument: (id, partial) =>
    set((s) => ({
      documents: s.documents.map((d) => (d.id === id ? { ...d, ...partial } : d)),
    })),

  // UI
  activeTab: 'chat',
  setActiveTab: (activeTab) => set({ activeTab }),
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}))

