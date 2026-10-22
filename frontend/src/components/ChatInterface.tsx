import React, { useState, useRef, useEffect } from 'react'
import { useStore } from '../store'
import { askQuestion } from '../api'
import { nanoid } from 'nanoid'
import { ChatMessage } from '../types'

const ChatBubble: React.FC<{ msg: ChatMessage }> = ({ msg }) => {
  const isUser = msg.role === 'user'
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 16,
    }}>
      <div style={{
        maxWidth: '80%',
        background: isUser ? 'var(--accent)' : 'var(--bg-card)',
        border: `1px solid ${isUser ? 'transparent' : 'var(--border)'}`,
        borderRadius: 'var(--radius)',
        padding: '10px 14px',
        color: 'var(--text-primary)',
        fontSize: 14,
        lineHeight: 1.6,
        whiteSpace: 'pre-wrap',
      }}>
        {msg.isLoading ? (
          <span style={{ opacity: 0.6 }}>⏳ Thinking…</span>
        ) : (
          msg.content
        )}
      </div>

      {msg.sources && msg.sources.length > 0 && (
        <div style={{ maxWidth: '80%', marginTop: 8 }}>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>
            📚 Sources ({msg.sources.length})
          </p>
          {msg.sources.map((s) => (
            <div key={s.id} style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 6,
              padding: '6px 10px',
              fontSize: 12,
              marginBottom: 4,
              color: 'var(--text-muted)',
            }}>
              <strong style={{ color: 'var(--text-primary)' }}>
                {s.title || 'Unknown'}
              </strong>{' '}
              (score: {s.score.toFixed(2)})
              <br />
              {s.content.slice(0, 150)}…
            </div>
          ))}
        </div>
      )}

      <span style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
        {new Date(msg.timestamp).toLocaleTimeString()}
      </span>
    </div>
  )
}

export const ChatInterface: React.FC = () => {
  const { messages, addUserMessage, addAssistantMessage, setMessageLoading, clearChat } = useStore()
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | undefined>()
  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async () => {
    const q = input.trim()
    if (!q || isLoading) return
    setInput('')
    setIsLoading(true)

    const msgId = nanoid()
    addUserMessage(q)

    // Add placeholder assistant message
    const aId = nanoid()
    const placeholder: ChatMessage = {
      id: aId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isLoading: true,
    }
    useStore.setState((s) => ({ messages: [...s.messages, placeholder] }))

    try {
      const res = await askQuestion({ question: q, conversation_id: conversationId })
      setConversationId(res.conversation_id ?? undefined)
      addAssistantMessage(aId, res.answer, res.sources)
    } catch (e: unknown) {
      const errMsg = e instanceof Error ? e.message : 'Failed to get answer'
      addAssistantMessage(aId, `❌ Error: ${errMsg}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <h2 style={{ fontSize: 16, fontWeight: 600 }}>💬 AI Knowledge Chat</h2>
        <button
          onClick={clearChat}
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
          Clear
        </button>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            color: 'var(--text-muted)',
            marginTop: 80,
          }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
            <p style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>AI Knowledge Copilot</p>
            <p style={{ fontSize: 14 }}>
              Upload documents, then ask questions. I'll find relevant context and give grounded answers.
            </p>
            <div style={{ marginTop: 24, display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
              {[
                'What are the main topics in the uploaded docs?',
                'Summarize the key points',
                'What is the policy on data retention?',
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => { setInput(q); textareaRef.current?.focus() }}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    borderRadius: 6,
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    padding: '6px 12px',
                    fontSize: 13,
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m) => <ChatBubble key={m.id} msg={m} />)}
        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: 12,
        borderTop: '1px solid var(--border)',
        display: 'flex',
        gap: 8,
      }}>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question (Shift+Enter for newline, Enter to send)…"
          rows={2}
          disabled={isLoading}
          style={{
            flex: 1,
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            color: 'var(--text-primary)',
            padding: '8px 12px',
            fontSize: 14,
            resize: 'none',
            outline: 'none',
            fontFamily: 'inherit',
          }}
        />
        <button
          onClick={handleSubmit}
          disabled={isLoading || !input.trim()}
          style={{
            background: isLoading || !input.trim() ? 'var(--border)' : 'var(--accent)',
            border: 'none',
            borderRadius: 'var(--radius)',
            color: 'white',
            cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
            padding: '0 20px',
            fontSize: 14,
            fontWeight: 600,
            transition: 'background 0.2s',
          }}
        >
          {isLoading ? '…' : 'Send'}
        </button>
      </div>
    </div>
  )
}

