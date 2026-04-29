import React, { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'

const STAGES = [
  { key: 'trust_building', label: 'Trust building' },
  { key: 'isolation', label: 'Isolation' },
  { key: 'secrecy', label: 'Secrecy' },
  { key: 'escalation', label: 'Escalation' },
]

const severityBadge = (severity) => {
  if (!severity) return 'bg-gray-300 text-gray-800'
  if (severity.toLowerCase() === 'high') return 'bg-red-500 text-white'
  if (severity.toLowerCase() === 'medium') return 'bg-amber-500 text-white'
  return 'bg-blue-500 text-white'
}

const recommendationMeta = (rec) => {
  switch (rec) {
    case 'alert_parent':
      return { className: 'bg-amber-50 border-amber-200 text-amber-800', text: 'Unusual patterns detected. Recommended: speak with your child.' }
    case 'escalate':
    case 'escalate_platform':
      return { className: 'bg-red-50 border-red-200 text-red-800', text: 'High-risk behaviour detected. Report to platform and authorities.' }
    default:
      return { className: 'bg-blue-50 border-blue-200 text-blue-800', text: 'Continue monitoring. No immediate action needed.' }
  }
}

const getRiskBadge = (score) => {
  if (score >= 71) return { title: 'High risk — act now', className: 'bg-red-100 text-red-800 border-red-300' }
  if (score >= 41) return { title: 'Medium risk — review', className: 'bg-amber-100 text-amber-800 border-amber-300' }
  return { title: 'Low risk — monitor', className: 'bg-green-100 text-green-800 border-green-300' }
}

const Dashboard = () => {
  const { sessionId: routeSessionId } = useParams()
  const navigate = useNavigate()
  const [sessions, setSessions] = useState([])
  const [session, setSession] = useState(null)
  const [loadingSessions, setLoadingSessions] = useState(false)
  const [loadingSession, setLoadingSession] = useState(false)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

  const WS_URL = import.meta.env.VITE_WS_URL || ((import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/^http/, 'ws') + '/ws/alerts')

  useEffect(() => { loadSessions() }, [])

  useEffect(() => {
    if (routeSessionId) fetchSession(routeSessionId)
    else if (sessions.length > 0 && !session) setSession(sessions[0])
  }, [routeSessionId, sessions])

  useEffect(() => {
    let ws
    try {
      ws = new WebSocket(WS_URL)
      wsRef.current = ws
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data)
          if (msg && msg.event === 'analysis_complete' && msg.session_id) {
            fetchSession(msg.session_id)
          }
        } catch (e) { }
      }
    } catch (e) {
      // WebSocket might not be available in some dev environments
    }
    return () => { if (wsRef.current) { wsRef.current.close(); wsRef.current = null } }
  }, [WS_URL])

  async function loadSessions() {
    setLoadingSessions(true)
    try {
      const list = await api.getSessions()
      list.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      setSessions(list)
      setLoadingSessions(false)
      if (!routeSessionId && list.length > 0) setSession(list[0])
    } catch (e) {
      setError('Failed to load sessions')
      setLoadingSessions(false)
    }
  }

  async function fetchSession(id) {
    setLoadingSession(true)
    try {
      const s = await api.getSession(id)
      if (s) {
        setSession(s)
        setSessions(prev => {
          const exists = prev.some(p => p.session_id === s.session_id)
          const updated = exists ? prev.map(p => p.session_id === s.session_id ? s : p) : [s, ...prev]
          updated.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          return updated
        })
      }
    } catch (e) {
      setError('Failed to load session')
    } finally { setLoadingSession(false) }
  }

  const s = session || {
    session_id: 'demo-session-1',
    risk_score: 0,
    confidence: 0,
    grooming_stage: 'trust_building',
    flags: [],
    stage_progression: {},
    drift_signals: {},
    recommendation: 'monitor',
    timestamp: new Date().toISOString(),
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display-sm text-display-sm text-on-surface mb-2">Overview</h1>
        <p className="font-body-lg text-body-lg text-on-surface-variant">Latest analysis for session {s.session_id}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Sidebar: Past sessions */}
        <aside className="md:col-span-3">
          <div className="glass-card rounded-2xl p-4 h-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-headline-sm">Past sessions</h3>
              <button className="text-sm text-primary" onClick={loadSessions}>Refresh</button>
            </div>
            {loadingSessions ? (
              <div className="text-sm text-on-surface-variant">Loading sessions…</div>
            ) : (
              <ul className="flex flex-col gap-2">
                {sessions.length === 0 && <li className="text-sm text-on-surface-variant">No sessions</li>}
                {sessions.map(sess => (
                  <li key={sess.session_id} className={`p-2 rounded-lg cursor-pointer hover:bg-surface/50 ${session && session.session_id === sess.session_id ? 'ring-2 ring-primary' : ''}`} onClick={() => { setSession(sess); navigate(`/dashboard/${sess.session_id}`) }}>
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-on-surface-variant">{new Date(sess.timestamp).toLocaleString()}</div>
                      <div className="font-display-sm">{sess.risk_score}</div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>

        {/* Main content */}
        <main className="md:col-span-9 flex flex-col gap-6">
          {/* Recommendation banner */}
          <div className={`rounded-xl border p-4 ${recommendationMeta(s.recommendation).className}`}>
            <div className="flex items-center justify-between">
              <div className="font-medium">{recommendationMeta(s.recommendation).text}</div>
              <div className="text-sm text-on-surface-variant">Updated: {new Date(s.timestamp).toLocaleString()}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Risk Score + Stage */}
            <div className="lg:col-span-4 glass-card rounded-2xl p-6 flex flex-col items-center">
              <div className="w-full flex items-center justify-between mb-4">
                <div className="text-sm text-on-surface-variant uppercase tracking-widest">Risk Score</div>
                <div className="text-sm text-on-surface-variant">Confidence: {Math.round((s.confidence || 0) * 100)}%</div>
              </div>
              <div className={`w-40 h-40 rounded-full flex items-center justify-center border-2 ${getRiskBadge(s.risk_score).className}`}>
                <div className="text-center">
                  <div className="font-display-xl text-4xl">{s.risk_score}</div>
                  <div className="text-sm mt-1">/ 100</div>
                </div>
              </div>
              <div className="mt-4 text-center text-sm text-on-surface-variant">{getRiskBadge(s.risk_score).title}</div>

              <div className="mt-6 w-full">
                <div className="text-sm mb-2">Grooming Stage</div>
                <div className="flex gap-2">
                  {STAGES.map(st => {
                    const done = s.stage_progression && s.stage_progression[st.key]
                    const active = s.grooming_stage === st.key
                    const base = done ? 'bg-purple-600 text-white' : active ? 'bg-purple-200 text-purple-900 ring-2 ring-purple-600' : 'bg-gray-100 text-gray-400'
                    return (
                      <div key={st.key} className={`${base} px-3 py-1 rounded-full text-sm`}>{st.label}</div>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Center: Flagged snippets & details */}
            <div className="lg:col-span-5 glass-card rounded-2xl p-6 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-headline-md">Flagged snippets</h3>
                <div className="text-sm text-on-surface-variant">{s.flags ? s.flags.length : 0} flags</div>
              </div>
              <div className="flex flex-col gap-3 overflow-y-auto max-h-[340px] pr-2">
                {s.flags && s.flags.length > 0 ? s.flags.map((f, idx) => (
                  <div key={idx} className="p-3 rounded-xl border border-outline-variant/30 bg-surface/50">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className={`${severityBadge(f.severity)} px-2 py-0.5 rounded-md text-xs font-medium`}>{f.type.replace(/_/g, ' ')}</span>
                        <div className="text-sm text-on-surface-variant">{f.message_index != null ? `#${f.message_index}` : ''}</div>
                      </div>
                      <div className="text-xs text-on-surface-variant uppercase">{(f.severity || '').toUpperCase()}</div>
                    </div>
                    <div className="font-body-md text-body-md text-on-surface">"{f.snippet}"</div>
                  </div>
                )) : (
                  <div className="text-sm text-on-surface-variant">No flagged snippets</div>
                )}
              </div>
            </div>

            {/* Right: Drift signals */}
            <div className="lg:col-span-3 glass-card rounded-2xl p-6 flex flex-col">
              <h3 className="font-headline-md mb-4">Drift signals</h3>
              <div className="flex flex-col gap-3">
                {[
                  { key: 'late_night_messages', label: 'Late-night messages' },
                  { key: 'new_unknown_contact', label: 'New unknown contact' },
                  { key: 'message_frequency_spike', label: 'Message frequency spike' },
                ].map(signal => {
                  const present = s.drift_signals && !!s.drift_signals[signal.key]
                  return (
                    <div key={signal.key} className="flex items-center justify-between p-3 rounded-lg bg-surface/50 border border-outline-variant/20">
                      <div className="text-sm">{signal.label}</div>
                      <div className={`text-xl ${present ? 'text-green-600' : 'text-red-600'}`}>
                        <span className="material-symbols-outlined">{present ? 'check_circle' : 'cancel'}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </main>
      </div>

      {error && <div className="mt-4 text-sm text-red-600">{error}</div>}
    </div>
  )
}

export default Dashboard
