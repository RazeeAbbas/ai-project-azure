import React from 'react'
import { BrowserRouter } from 'react-router-dom'
import { useStore } from './store'
import { ChatInterface } from './components/ChatInterface'
import { DocumentManager } from './components/DocumentManager'
import { HealthDashboard } from './components/HealthDashboard'

const tabs = [
  { id: 'chat', label: '💬 Chat', icon: '💬' },
  { id: 'documents', label: '📄 Documents', icon: '📄' },
  { id: 'health', label: '🩺 Health', icon: '🩺' },
] as const

export default function App() {
  const { activeTab, setActiveTab } = useStore()

  return (
    <BrowserRouter>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        background: 'var(--bg)',
        color: 'var(--text-primary)',
      }}>
        {/* Top Nav */}
        <header style={{
          background: 'var(--bg-card)',
          borderBottom: '1px solid var(--border)',
          padding: '0 20px',
          display: 'flex',
          alignItems: 'center',
          gap: 24,
          height: 56,
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 24 }}>🤖</span>
            <span style={{ fontWeight: 700, fontSize: 16 }}>AI Knowledge Copilot</span>
            <span style={{
              background: 'var(--accent)22',
              color: 'var(--accent)',
              border: '1px solid var(--accent)44',
              borderRadius: 12,
              padding: '2px 8px',
              fontSize: 11,
              fontWeight: 600,
            }}>
              RAG
            </span>
          </div>

          <nav style={{ display: 'flex', gap: 4, marginLeft: 'auto' }}>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  background: activeTab === tab.id ? 'var(--accent)' : 'transparent',
                  border: `1px solid ${activeTab === tab.id ? 'var(--accent)' : 'var(--border)'}`,
                  borderRadius: 6,
                  color: activeTab === tab.id ? 'white' : 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: '6px 14px',
                  fontSize: 13,
                  fontWeight: 600,
                  transition: 'all 0.15s',
                }}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          <div style={{ marginLeft: 16, fontSize: 12, color: 'var(--text-muted)' }}>
            Azure DevOps Capstone
          </div>
        </header>

        {/* Main Content */}
        <main style={{ flex: 1, minHeight: 0 }}>
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'documents' && <DocumentManager />}
          {activeTab === 'health' && <HealthDashboard />}
        </main>

        {/* Footer */}
        <footer style={{
          background: 'var(--bg-card)',
          borderTop: '1px solid var(--border)',
          padding: '6px 16px',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: 11,
          color: 'var(--text-muted)',
          flexShrink: 0,
        }}>
          <span>AI Knowledge Copilot — Azure AKS + App Service Deployment</span>
          <span>Terraform + Docker + GitHub Actions + AKS</span>
        </footer>
      </div>
    </BrowserRouter>
  )
}

