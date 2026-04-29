import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const riskStyles = {
  high: { badge: 'bg-error-container text-on-error-container border-error/10', dot: 'bg-error animate-pulse' },
  medium: { badge: 'bg-tertiary-container text-on-tertiary-container border-tertiary/10', dot: 'bg-tertiary' },
  low: { badge: 'bg-secondary-container text-on-secondary-container border-secondary/10', dot: 'bg-secondary' },
}

const recStyles = {
  escalate_platform: { text: 'Escalate', className: 'bg-red-100 text-red-800' },
  alert_parent: { text: 'Alert Parent', className: 'bg-amber-100 text-amber-800' },
  monitor: { text: 'Monitor', className: 'bg-blue-100 text-blue-800' },
}

function scoreToRisk(score) {
  if (score >= 71) return 'high'
  if (score >= 41) return 'medium'
  return 'low'
}

const PAGE_SIZE = 10

const SessionHistory = () => {
  const navigate = useNavigate()
  const [sessions, setSessions] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    api.getSessions(PAGE_SIZE, page * PAGE_SIZE).then((list) => {
      if (!mounted) return
      setSessions(list)
      setHasMore(list.length >= PAGE_SIZE)
      setLoading(false)
    }).catch((err) => {
      if (!mounted) return
      setError(err.message || 'Failed to load sessions')
      setSessions([])
      setLoading(false)
    })
    return () => { mounted = false }
  }, [page])

  const handleViewSession = (sessionId) => {
    navigate(`/dashboard/${sessionId}`)
  }

  const display = sessions || []

  return (
    <div className="max-w-[1200px] mx-auto space-y-8">
      <div>
        <h2 className="font-display-sm text-display-sm text-on-surface">Session History</h2>
        <p className="font-body-md text-body-md text-on-surface-variant mt-2">Review historical monitoring sessions and associated risk assessments.</p>
      </div>

      <div className="glass-card rounded-[24px] overflow-hidden">
        {/* Table header */}
        <div className="grid grid-cols-12 gap-4 px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low/50">
          <div className="col-span-3 font-label-md text-label-md text-on-surface-variant">Session ID</div>
          <div className="col-span-2 font-label-md text-label-md text-on-surface-variant">Platform</div>
          <div className="col-span-2 font-label-md text-label-md text-on-surface-variant">Timestamp</div>
          <div className="col-span-2 font-label-md text-label-md text-on-surface-variant">Risk Assessment</div>
          <div className="col-span-1 font-label-md text-label-md text-on-surface-variant">Recommendation</div>
          <div className="col-span-2 font-label-md text-label-md text-on-surface-variant text-right">Action</div>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="px-6 py-16 text-center">
            <span className="material-symbols-outlined text-3xl text-outline animate-spin mb-3 block">progress_activity</span>
            <span className="font-label-md text-on-surface-variant">Loading sessions…</span>
          </div>
        )}

        {/* Error state */}
        {!loading && error && (
          <div className="px-6 py-12 text-center">
            <span className="material-symbols-outlined text-3xl text-error mb-3 block" style={{ fontVariationSettings: "'FILL' 1" }}>error</span>
            <span className="font-label-md text-error">{error}</span>
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && display.length === 0 && (
          <div className="px-6 py-16 text-center">
            <span className="material-symbols-outlined text-4xl text-outline mb-3 block">inbox</span>
            <span className="font-label-md text-on-surface-variant">No sessions found. Upload a chat log or audio to get started.</span>
          </div>
        )}

        {/* Table rows */}
        {!loading && display.length > 0 && (
          <div className="divide-y divide-outline-variant/20">
            {display.map((s) => {
              const id = s.session_id || '—'
              const shortId = typeof id === 'string' && id.length > 12 ? id.slice(0, 8) + '…' : id
              const ts = s.timestamp ? new Date(s.timestamp).toLocaleString() : '—'
              const score = s.risk_score != null ? s.risk_score : 0
              const risk = scoreToRisk(score)
              const st = riskStyles[risk]
              const rec = recStyles[s.recommendation] || recStyles.monitor
              const platform = s.platform || '—'
              return (
                <div key={id} className="grid grid-cols-12 gap-4 px-6 py-5 items-center hover:bg-surface-container-low/50 transition-colors duration-200">
                  <div className="col-span-3 font-body-md text-body-md text-on-surface font-medium font-mono text-sm truncate" title={id}>
                    {shortId}
                  </div>
                  <div className="col-span-2 font-body-md text-body-md text-on-surface-variant capitalize">
                    {platform.replace(/_/g, ' ')}
                  </div>
                  <div className="col-span-2 font-body-md text-body-md text-on-surface-variant text-sm">{ts}</div>
                  <div className="col-span-2">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full font-label-sm text-label-sm gap-1.5 border ${st.badge}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`}></span>
                      Score: {String(score).padStart(2, '0')}
                    </span>
                  </div>
                  <div className="col-span-1">
                    <span className={`inline-flex px-2 py-0.5 rounded-md font-label-sm text-label-sm ${rec.className}`}>
                      {rec.text}
                    </span>
                  </div>
                  <div className="col-span-2 text-right">
                    <button
                      onClick={() => handleViewSession(id)}
                      className="px-4 py-2 rounded-lg bg-surface-container hover:bg-surface-container-highest text-primary font-label-md text-label-md transition-all border border-primary/10 inline-flex items-center gap-1.5"
                    >
                      <span className="material-symbols-outlined text-[16px]">visibility</span>
                      View Details
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Pagination footer */}
        <div className="px-6 py-4 border-t border-outline-variant/30 flex justify-between items-center bg-surface-container-low/30">
          <span className="font-label-sm text-label-sm text-outline">
            {loading ? '…' : `Showing ${display.length} session${display.length !== 1 ? 's' : ''} (page ${page + 1})`}
          </span>
          <div className="flex gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage(p => Math.max(0, p - 1))}
              className={`p-2 rounded-lg bg-surface border border-outline-variant/50 transition-all ${page === 0 ? 'text-outline opacity-50 cursor-not-allowed' : 'text-on-surface hover:bg-surface-variant'}`}
            >
              <span className="material-symbols-outlined text-sm">chevron_left</span>
            </button>
            <button
              disabled={!hasMore}
              onClick={() => setPage(p => p + 1)}
              className={`p-2 rounded-lg bg-surface border border-outline-variant/50 transition-all ${!hasMore ? 'text-outline opacity-50 cursor-not-allowed' : 'text-on-surface hover:bg-surface-variant'}`}
            >
              <span className="material-symbols-outlined text-sm">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SessionHistory;
