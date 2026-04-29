import React, { useEffect, useState } from 'react'
import api from '../services/api'

const riskStyles = {
  high: { badge: 'bg-error-container text-on-error-container border-error/10', dot: 'bg-error animate-pulse' },
  medium: { badge: 'bg-tertiary-container text-on-tertiary-container border-tertiary/10', dot: 'bg-tertiary' },
  low: { badge: 'bg-secondary-container text-on-secondary-container border-secondary/10', dot: 'bg-secondary' },
}

function scoreToRisk(score) {
  if (score >= 71) return 'high'
  if (score >= 41) return 'medium'
  return 'low'
}

const SessionHistory = () => {
  const [sessions, setSessions] = useState(null)

  useEffect(() => {
    let mounted = true
    api.getSessions().then((list) => {
      if (!mounted) return
      setSessions(list)
    }).catch(() => {
      if (!mounted) return
      setSessions([])
    })
    return () => { mounted = false }
  }, [])

  const display = sessions || [
    { session_id: '#SW-8892-A', timestamp: 'Oct 24, 2023 • 14:32', risk_score: 84 },
    { session_id: '#SW-8891-B', timestamp: 'Oct 24, 2023 • 11:15', risk_score: 12 },
    { session_id: '#SW-8890-C', timestamp: 'Oct 23, 2023 • 18:45', risk_score: 45 },
    { session_id: '#SW-8889-D', timestamp: 'Oct 23, 2023 • 09:20', risk_score: 5 },
  ]

  return (
    <div className="max-w-[1200px] mx-auto space-y-8">
      <div>
        <h2 className="font-display-sm text-display-sm text-on-surface">Session History</h2>
        <p className="font-body-md text-body-md text-on-surface-variant mt-2">Review historical monitoring sessions and associated risk assessments.</p>
      </div>

      <div className="bg-white/70 backdrop-blur-[20px] rounded-[24px] border border-white/50 shadow-[0_20px_40px_rgba(0,0,0,0.03)] overflow-hidden">
        <div className="grid grid-cols-12 gap-4 px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low/50">
          <div className="col-span-3 font-label-md text-label-md text-on-surface-variant">Session ID</div>
          <div className="col-span-3 font-label-md text-label-md text-on-surface-variant">Timestamp</div>
          <div className="col-span-3 font-label-md text-label-md text-on-surface-variant">Risk Assessment</div>
          <div className="col-span-3 font-label-md text-label-md text-on-surface-variant text-right">Action</div>
        </div>

        <div className="divide-y divide-outline-variant/20">
          {display.map((s) => {
            const id = s.session_id || s.id || '#-'
            const ts = s.timestamp ? new Date(s.timestamp).toLocaleString() : '—'
            const score = s.risk_score != null ? s.risk_score : s.score
            const risk = scoreToRisk(score || 0)
            const st = riskStyles[risk]
            return (
              <div key={id} className="grid grid-cols-12 gap-4 px-6 py-5 items-center hover:bg-surface-container-low/50 transition-colors duration-200">
                <div className="col-span-3 font-body-md text-body-md text-on-surface font-medium">{id}</div>
                <div className="col-span-3 font-body-md text-body-md text-on-surface-variant">{ts}</div>
                <div className="col-span-3">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full font-label-sm text-label-sm gap-1.5 border ${st.badge}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`}></span>
                    Score: {String(score || 0).padStart(2, '0')}
                  </span>
                </div>
                <div className="col-span-3 text-right">
                  <button className="px-4 py-2 rounded-lg bg-surface-container hover:bg-surface-container-highest text-primary font-label-md text-label-md transition-all border border-primary/10">View Full Chat</button>
                </div>
              </div>
            )
          })}
        </div>

        <div className="px-6 py-4 border-t border-outline-variant/30 flex justify-between items-center bg-surface-container-low/30">
          <span className="font-label-sm text-label-sm text-outline">Showing {display.length} sessions</span>
          <div className="flex gap-2">
            <button className="p-2 rounded-lg bg-surface text-outline border border-outline-variant/50 opacity-50 cursor-not-allowed">
              <span className="material-symbols-outlined text-sm">chevron_left</span>
            </button>
            <button className="p-2 rounded-lg bg-surface hover:bg-surface-variant text-on-surface border border-outline-variant/50">
              <span className="material-symbols-outlined text-sm">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SessionHistory;
