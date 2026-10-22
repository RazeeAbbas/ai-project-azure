import React, { useState, useEffect, useCallback } from 'react'
import { getHealth } from '../api'
import { HealthStatus } from '../types'

const CheckRow: React.FC<{ name: string; value: string }> = ({ name, value }) => {
  const isOk = value === 'healthy' || value === 'configured'
  const isWarn = value.startsWith('warn')
  const color = isOk ? 'var(--success)' : isWarn ? 'var(--warning)' : 'var(--error)'
  const icon = isOk ? '✅' : isWarn ? '⚠️' : '❌'
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '8px 0',
      borderBottom: '1px solid var(--border)',
      fontSize: 13,
    }}>
      <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{name.replace(/_/g, ' ')}</span>
      <span style={{ color, fontWeight: 600 }}>{icon} {value}</span>
    </div>
  )
}

export const HealthDashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [lastCheck, setLastCheck] = useState<string | null>(null)

  const check = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const h = await getHealth()
      setHealth(h)
      setLastCheck(new Date().toLocaleTimeString())
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to reach backend')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    check()
    const interval = setInterval(check, 30000) // auto-refresh every 30s
    return () => clearInterval(interval)
  }, [check])

  const overallColor =
    health?.status === 'healthy' ? 'var(--success)' :
    health?.status === 'degraded' ? 'var(--error)' :
    'var(--warning)'

  return (
    <div style={{ padding: 16, height: '100%', overflowY: 'auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600 }}>🩺 Health Dashboard</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {lastCheck && <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Last: {lastCheck}</span>}
          <button
            onClick={check}
            disabled={loading}
            style={{
              background: 'var(--accent)',
              border: 'none',
              borderRadius: 6,
              color: 'white',
              cursor: loading ? 'wait' : 'pointer',
              padding: '4px 12px',
              fontSize: 12,
              fontWeight: 600,
            }}
          >
            {loading ? 'Checking…' : '↻ Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          background: '#ef444422',
          border: '1px solid #ef4444',
          borderRadius: 'var(--radius)',
          padding: '12px 16px',
          color: '#ef4444',
          marginBottom: 16,
        }}>
          ❌ Backend unreachable: {error}
        </div>
      )}

      {health && (
        <>
          {/* Overall Status */}
          <div style={{
            background: 'var(--bg-card)',
            border: `2px solid ${overallColor}`,
            borderRadius: 'var(--radius)',
            padding: 20,
            marginBottom: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 16,
          }}>
            <div style={{ fontSize: 48 }}>
              {health.status === 'healthy' ? '🟢' : health.status === 'degraded' ? '🔴' : '🟡'}
            </div>
            <div>
              <p style={{ fontSize: 22, fontWeight: 700, color: overallColor, textTransform: 'uppercase' }}>
                {health.status}
              </p>
              <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                {health.service} v{health.version}
              </p>
            </div>
          </div>

          {/* Checks */}
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '0 16px',
          }}>
            <p style={{ fontWeight: 600, fontSize: 13, padding: '12px 0', borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
              Component Checks
            </p>
            {Object.entries(health.checks).map(([k, v]) => (
              <CheckRow key={k} name={k} value={v} />
            ))}
          </div>

          {/* Info */}
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: 16,
            marginTop: 12,
            fontSize: 13,
            color: 'var(--text-muted)',
          }}>
            <p>Auto-refreshes every 30 seconds. This page shows the live status of all backend components.</p>
          </div>
        </>
      )}

      {!health && !error && !loading && (
        <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>
          Click Refresh to check backend health
        </div>
      )}
    </div>
  )
}

