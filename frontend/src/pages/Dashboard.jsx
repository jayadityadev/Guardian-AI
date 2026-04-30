import { useEffect, useState, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api, { getWsAlertsUrl } from '../services/api'

const STAGES = [
  { key: 'trust_building', label: 'Trust building' },
  { key: 'isolation', label: 'Isolation' },
  { key: 'secrecy', label: 'Secrecy' },
  { key: 'escalation', label: 'Escalation' },
]

const severityBadge = (severity) => {
  if (!severity) return 'bg-muted text-muted-foreground'
  if (severity.toLowerCase() === 'high') return 'bg-red-500 text-white'
  if (severity.toLowerCase() === 'medium') return 'bg-amber-500 text-white'
  return 'bg-blue-500 text-white'
}

const recommendationMeta = (rec) => {
  switch (rec) {
    case 'alert_parent':
      return { className: 'bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-900/20 dark:border-amber-800 dark:text-amber-300', text: 'Unusual patterns detected. Recommended: speak with your child.' }
    case 'escalate':
    case 'escalate_platform':
      return { className: 'bg-red-50 border-red-200 text-red-900 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300', text: 'High-risk behaviour detected. Report to platform and authorities.' }
    default:
      return { className: 'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300', text: 'Continue monitoring. No immediate action needed.' }
  }
}

const getRiskBadge = (score) => {
  if (score >= 71) return {
    title: 'High risk — act now',
    className: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/30',
    strokeColor: 'stroke-red-500',
    textColor: 'text-red-600 dark:text-red-400'
  }
  if (score >= 41) return {
    title: 'Medium risk — review',
    className: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30',
    strokeColor: 'stroke-amber-500',
    textColor: 'text-amber-600 dark:text-amber-400'
  }
  return {
    title: 'Low risk — monitor',
    className: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/30',
    strokeColor: 'stroke-green-500',
    textColor: 'text-green-600 dark:text-green-400'
  }
}

const Dashboard = () => {
  const { sessionId: routeSessionId } = useParams()
  const navigate = useNavigate()
  const [sessions, setSessions] = useState([])
  const [session, setSession] = useState(null)
  const [loadingSessions, setLoadingSessions] = useState(false)
  const [loadingSession, setLoadingSession] = useState(false)
  const [error, setError] = useState(null)
  const [showAllSessions, setShowAllSessions] = useState(false)
  const wsRef = useRef(null)

  const WS_URL = getWsAlertsUrl()

  const loadSessions = useCallback(async () => {
    setLoadingSessions(true)
    try {
      const list = await api.getSessions()
      list.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      setSessions(list)
      setLoadingSessions(false)
    } catch (err) {
      console.error(err)
      setError(err.message || 'Failed to load sessions')
      setLoadingSessions(false)
    }
  }, [])

  const fetchSession = useCallback(async (id) => {
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
    } catch (err) {
      console.error(err)
      setError('Failed to load session')
    } finally { setLoadingSession(false) }
  }, [])

  useEffect(() => {
    const t = setTimeout(() => { loadSessions() }, 0)
    return () => clearTimeout(t)
  }, [loadSessions])

  useEffect(() => {
    if (routeSessionId) {
      const tt = setTimeout(() => fetchSession(routeSessionId), 0)
      return () => clearTimeout(tt)
    }
  }, [routeSessionId, fetchSession])

  useEffect(() => {
    if (!routeSessionId && sessions.length > 0 && !session) {
      const t = setTimeout(() => setSession(sessions[0]), 0)
      return () => clearTimeout(t)
    }
  }, [routeSessionId, sessions, session])

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
        } catch (err) { console.debug(err) }
      }
    } catch (err) {
      console.debug('WebSocket unavailable', err)
    }
    return () => { if (wsRef.current) { wsRef.current.close(); wsRef.current = null } }
  }, [WS_URL, fetchSession])

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
        <h1 className="font-display-sm text-display-sm text-foreground mb-2">Overview</h1>
        <p className="font-body-lg text-body-lg text-muted-foreground flex items-center gap-2 flex-wrap">
          Latest analysis for session <span className="font-mono text-sm">{s.session_id}</span>
          {s.platform && (
            <span className="px-2 py-0.5 rounded-md bg-secondary text-secondary-foreground font-label-sm text-label-sm capitalize border border-border">
              {s.platform.replace(/_/g, ' ')}
            </span>
          )}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Sidebar: Past sessions */}
        <aside className="md:col-span-3">
          <div className="glass-card rounded-2xl p-5 h-full group cursor-pointer relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-[40px] -mr-10 -mt-10 transition-transform duration-500 group-hover:scale-150 pointer-events-none"></div>
            <div className="relative z-10 flex items-center justify-between mb-4">
              <h3 className="font-headline-sm m-0">Past sessions</h3>
              <button className="text-sm text-primary" onClick={loadSessions}>Refresh</button>
            </div>
            {loadingSessions ? (
              <div className="text-sm text-muted-foreground">Loading sessions…</div>
            ) : error ? (
              <div className="text-sm text-red-600">{error}</div>
            ) : (
              <ul className="flex flex-col gap-2">
                {sessions.length === 0 && <li className="text-sm text-muted-foreground">No sessions</li>}
                {sessions.slice(0, 12).map(sess => (
                  <li 
                    key={sess.session_id} 
                    className={`p-3 rounded-xl cursor-pointer group transition-all duration-300 border border-transparent hover:border-border hover:bg-muted ${(routeSessionId || session?.session_id) === sess.session_id ? 'ring-2 ring-primary/20 bg-primary/5 border-primary/20' : ''}`} 
                    onClick={() => { navigate(`/dashboard/${sess.session_id}`) }}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${sess.risk_score > 70 ? 'bg-red-500 animate-pulse' : sess.risk_score > 40 ? 'bg-amber-500' : 'bg-green-500'}`}></div>
                        <div className="text-[13px] text-muted-foreground truncate font-medium">
                          {new Date(sess.timestamp).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                      <div className={`font-display-sm font-bold text-sm shrink-0 px-2 py-0.5 rounded-lg bg-muted/20 ${getRiskBadge(sess.risk_score).textColor}`}>
                        {sess.risk_score}
                      </div>
                    </div>
                  </li>
                ))}
                
                {sessions.length > 12 && (
                  <button 
                    className="mt-4 w-full py-2.5 text-xs text-primary font-bold uppercase tracking-wider hover:bg-primary/5 rounded-xl transition-all border border-primary/10 hover:border-primary/30 flex items-center justify-center gap-2"
                    onClick={() => navigate('/dashboard/history')}
                  >
                    <span className="material-symbols-outlined text-[18px]">history</span>
                    View Session History
                  </button>
                )}
              </ul>
            )}
          </div>
        </aside>

        {/* Main content */}
        <main className={`md:col-span-9 flex flex-col gap-6 transition-opacity duration-200 ${loadingSession ? 'opacity-50 pointer-events-none' : ''}`}>
          {/* Recommendation banner */}
          <div className={`rounded-xl border p-4 ${recommendationMeta(s.recommendation).className}`}>
            <div className="flex items-center justify-between">
              <div className="font-medium">{recommendationMeta(s.recommendation).text}</div>
              <div className="text-sm opacity-80">Updated: {new Date(s.timestamp).toLocaleString()}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Risk Score + Stage */}
            <div className="lg:col-span-6 glass-card rounded-2xl p-8 flex flex-col items-center group cursor-pointer relative overflow-hidden h-full">
              <div className="absolute top-0 right-0 w-40 h-40 bg-primary/5 rounded-full blur-[50px] -mr-12 -mt-12 transition-transform duration-500 group-hover:scale-150 pointer-events-none"></div>
              <div className="w-full flex items-center justify-between mb-4 relative z-10">
                <div className="text-sm text-muted-foreground uppercase tracking-widest">Risk Score</div>
                <div className="text-sm text-muted-foreground">Confidence: {Math.round((s.confidence || 0) * 100)}%</div>
              </div>
              <div className="relative w-36 h-36 sm:w-44 sm:h-44 flex items-center justify-center">
                {/* SVG Progress Circle */}
                <svg className="absolute inset-0 w-full h-full transform -rotate-90 drop-shadow-sm" viewBox="0 0 100 100">
                  {/* Background Circle */}
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    strokeWidth="8"
                    className="stroke-muted border-border"
                  />
                  {/* Progress Circle */}
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    strokeWidth="8"
                    strokeLinecap="round"
                    className={`${getRiskBadge(s.risk_score).strokeColor} transition-all duration-1000 ease-out`}
                    style={{
                      strokeDasharray: 283,
                      strokeDashoffset: 283 - (283 * (s.risk_score || 0)) / 100
                    }}
                  />
                </svg>
                <div className="text-center relative z-10 flex flex-col items-center justify-center bg-card rounded-full w-28 h-28 sm:w-32 sm:h-32 shadow-inner border border-border">
                  <div className={`font-display-xl text-5xl font-bold ${getRiskBadge(s.risk_score).textColor}`}>{s.risk_score}</div>
                  <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mt-1">/ 100</div>
                </div>
              </div>
              <div className="mt-4 text-center text-sm text-muted-foreground">{getRiskBadge(s.risk_score).title}</div>

              <div className="mt-8 w-full relative z-10 border-t border-border/50 pt-6">
                <div className="text-sm font-semibold mb-6 flex items-center justify-between text-foreground">
                  Grooming Stage Analysis
                  <span className="text-xs font-medium bg-muted/80 text-muted-foreground px-2 py-1 rounded-md border border-border/50 capitalize">
                    {s.grooming_stage ? s.grooming_stage.replace('_', ' ') : 'None'}
                  </span>
                </div>

                <div className="relative flex justify-between items-start px-2">
                  {/* Background Track */}
                  <div className="absolute left-[10%] right-[10%] top-3 h-[2px] bg-border/50 rounded-full z-0"></div>

                  {STAGES.map((st) => {
                    const done = s.stage_progression && s.stage_progression[st.key]
                    const active = s.grooming_stage === st.key

                    const markerStyle = done
                      ? 'bg-primary border-primary text-primary-foreground'
                      : active
                        ? 'bg-card border-amber-500 ring-4 ring-amber-500/20 scale-110 shadow-lg shadow-amber-500/20'
                        : 'bg-card border-border/80 text-transparent'

                    const textStyle = done
                      ? 'text-foreground font-semibold'
                      : active
                        ? 'text-amber-500 font-bold'
                        : 'text-muted-foreground font-medium'

                    return (
                      <div key={st.key} className="relative z-10 flex flex-col items-center gap-3 w-1/4">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-500 ${markerStyle}`}>
                          {done && <span className="material-symbols-outlined text-[14px] font-bold" style={{ fontVariationSettings: "'FILL' 1" }}>check</span>}
                          {active && <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>}
                        </div>
                        <span className={`text-[11px] sm:text-xs text-center leading-tight tracking-wide ${textStyle}`}>
                          {st.label}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Center: Flagged snippets & details */}
            <div className="lg:col-span-6 glass-card rounded-2xl p-8 flex flex-col group cursor-pointer relative overflow-hidden">
              <div className="absolute top-0 right-0 w-40 h-40 bg-primary/5 rounded-full blur-[50px] -mr-12 -mt-12 transition-transform duration-500 group-hover:scale-150 pointer-events-none"></div>
              <div className="relative z-10 flex items-center justify-between mb-4">
                <h3 className="font-headline-md">Flagged snippets</h3>
                <div className="text-sm text-muted-foreground">{s.flags ? s.flags.length : 0} flags</div>
              </div>
              <div className="flex flex-col gap-3 overflow-y-auto max-h-[340px] pr-2 min-h-0">
                {s.flags && s.flags.length > 0 ? s.flags.map((f, idx) => (
                  <div key={idx} className="p-3 rounded-xl border border-border bg-muted/50 overflow-hidden">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className={`${severityBadge(f.severity)} px-2 py-0.5 rounded-md text-xs font-medium`}>{f.type.replace(/_/g, ' ')}</span>
                        <div className="text-sm text-muted-foreground">{f.message_index != null ? `#${f.message_index}` : ''}</div>
                      </div>
                      <div className="text-xs text-muted-foreground uppercase">{(f.severity || '').toUpperCase()}</div>
                    </div>
                    <div className="font-body-md text-body-md text-foreground break-words whitespace-pre-wrap max-w-full">"{f.snippet}"</div>
                  </div>
                )) : (
                  <div className="text-sm text-muted-foreground">No flagged snippets</div>
                )}
              </div>
            </div>

            {/* Right: Drift signals (moved below, full width) */}
            <div className="lg:col-span-12 glass-card rounded-2xl p-8 flex flex-col group cursor-pointer relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-[60px] -mr-16 -mt-16 transition-transform duration-500 group-hover:scale-150 pointer-events-none"></div>
              
              <div className="relative z-10 flex items-center justify-between mb-6">
                <h3 className="font-headline-md flex items-center gap-2 m-0 text-foreground">
                  <span className="material-symbols-outlined text-primary/80" style={{fontVariationSettings: "'FILL' 1"}}>radar</span>
                  Behavioral Drift Signals
                </h3>
              </div>

              <div className="relative z-10 grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { 
                    key: 'late_night_messages', 
                    label: 'Late-night messaging', 
                    desc: 'Activity outside normal hours',
                    theme: 'indigo',
                    icon: 'dark_mode'
                  },
                  { 
                    key: 'new_unknown_contact', 
                    label: 'Unknown contacts', 
                    desc: 'Sudden new relationships',
                    theme: 'amber',
                    icon: 'person_search'
                  },
                  { 
                    key: 'message_frequency_spike', 
                    label: 'Frequency spike', 
                    desc: 'Abnormal volume increase',
                    theme: 'rose',
                    icon: 'trending_up'
                  },
                ].map(signal => {
                  const present = s.drift_signals && !!s.drift_signals[signal.key]
                  
                  const themeClasses = {
                    indigo: {
                      bg: 'bg-indigo-500/10 border-indigo-500/30 shadow-sm shadow-indigo-500/5',
                      icon: 'text-indigo-500 bg-indigo-500/20 ring-2 ring-indigo-500/30',
                      text: 'text-indigo-600 dark:text-indigo-400'
                    },
                    amber: {
                      bg: 'bg-amber-500/10 border-amber-500/30 shadow-sm shadow-amber-500/5',
                      icon: 'text-amber-500 bg-amber-500/20 ring-2 ring-amber-500/30',
                      text: 'text-amber-600 dark:text-amber-400'
                    },
                    rose: {
                      bg: 'bg-rose-500/10 border-rose-500/30 shadow-sm shadow-rose-500/5',
                      icon: 'text-rose-500 bg-rose-500/20 ring-2 ring-rose-500/30',
                      text: 'text-rose-600 dark:text-rose-400'
                    }
                  }
                  
                  const colors = themeClasses[signal.theme]
                  const bgClass = present ? colors.bg : 'bg-muted/20 border-border/50'
                  const iconClass = present ? colors.icon : 'text-muted-foreground bg-muted'
                  const iconName = present ? signal.icon : 'check'
                  
                  return (
                    <div key={signal.key} className={`flex items-start gap-4 p-4 rounded-xl border transition-colors ${bgClass}`}>
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${iconClass}`}>
                        <span className="material-symbols-outlined text-[20px]" style={{fontVariationSettings: "'FILL' 1"}}>{iconName}</span>
                      </div>
                      <div>
                        <div className={`text-sm font-semibold mb-1 tracking-tight ${present ? colors.text : 'text-foreground'}`}>
                          {signal.label}
                        </div>
                        <div className="text-xs text-muted-foreground leading-tight">
                          {signal.desc}
                        </div>
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
