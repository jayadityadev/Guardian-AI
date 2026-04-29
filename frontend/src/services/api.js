import demoSession from '../mock/demoSession.json'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

/**
 * Normalize a raw session object from backend to match the API contract exactly.
 * Contract fields (snake_case):
 *   session_id, platform, timestamp, risk_score, confidence,
 *   grooming_stage, flags[], categories[], stage_progression{},
 *   recommendation, drift_signals{}
 */
function normalizeSession(raw) {
    if (!raw) return null

    // Backend returns flags as `flags` (contract-compliant).
    // DB column is `raw_flag_json` but backend already maps it.
    const flags = Array.isArray(raw.flags) ? raw.flags : []

    return {
        session_id: raw.session_id || raw.id || '',
        platform: raw.platform || 'json_upload',
        timestamp: raw.timestamp || raw.created_at || new Date().toISOString(),
        risk_score: raw.risk_score != null ? raw.risk_score : 0,
        confidence: raw.confidence != null ? raw.confidence : 0,
        grooming_stage: raw.grooming_stage || 'none',
        flags: flags,
        categories: raw.categories || (flags.length > 0 ? Array.from(new Set(flags.map(f => f.type).filter(Boolean))) : []),
        stage_progression: raw.stage_progression || {},
        recommendation: raw.recommendation || 'monitor',
        drift_signals: raw.drift_signals || {},
    }
}

/**
 * Parse backend error responses.
 * Contract format: { "error": "message" }
 */
function parseApiError(status, bodyText) {
    let message = `API error: ${status}`
    try {
        const parsed = JSON.parse(bodyText)
        if (parsed && parsed.error) {
            message = parsed.error
        }
    } catch {
        if (bodyText) message += ` - ${bodyText}`
    }
    return message
}

async function apiFetch(path, opts = {}) {
    const base = API_BASE.replace(/\/$/, '')
    const url = path.startsWith('http') ? path : base + (path.startsWith('/') ? path : '/' + path)
    const { method = 'GET', body, headers = {} } = opts

    const init = { method, headers: { ...headers } }
    if (body instanceof FormData) {
        init.body = body
        // let browser set Content-Type for multipart
    } else if (body != null) {
        init.headers['Content-Type'] = 'application/json'
        init.body = JSON.stringify(body)
    }

    const res = await fetch(url, init)
    if (!res.ok) {
        const text = await res.text().catch(() => '')
        const err = new Error(parseApiError(res.status, text))
        err.status = res.status
        err.body = text
        throw err
    }

    const contentType = res.headers.get('content-type') || ''
    if (contentType.includes('application/json')) return res.json()
    return res.text()
}

// ─── Public API ────────────────────────────────────────────

/**
 * GET /session/{session_id}
 * Returns full risk assessment (RiskJSON) for a session.
 */
export async function getSession(sessionId) {
    if (USE_MOCK) {
        const key = 'session_' + sessionId
        const stored = localStorage.getItem(key)
        if (stored) return normalizeSession(JSON.parse(stored))
        if (demoSession && demoSession.session_id === sessionId) return normalizeSession(demoSession)
        return null
    }

    const res = await apiFetch(`/session/${sessionId}`)
    return normalizeSession(res)
}

/**
 * GET /sessions?limit=N&offset=M
 * Returns lightweight list of past sessions.
 */
export async function getSessions(limit = 50, offset = 0) {
    if (USE_MOCK) {
        const keys = Object.keys(localStorage).filter(k => k.startsWith('session_'))
        let sessions = keys.map(k => {
            try { return normalizeSession(JSON.parse(localStorage.getItem(k))) } catch { return null }
        }).filter(Boolean)
        if (sessions.length === 0) sessions = [normalizeSession(demoSession)]
        sessions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        return sessions
    }

    const res = await apiFetch(`/sessions?limit=${limit}&offset=${offset}`)
    // Backend returns a plain array per contract
    const arr = Array.isArray(res) ? res : []
    return arr.map(normalizeSession)
}

/**
 * POST /ingest
 * Submit chat messages for analysis.
 * Body: { platform: string, messages: [{sender, text, timestamp}] }
 * Response: { session_id: uuid, status: "processing" }
 */
export async function ingestJson(body) {
    if (USE_MOCK) {
        const id = 'mock-' + Date.now().toString(36)
        const session = Object.assign({}, demoSession, {
            session_id: id,
            timestamp: new Date().toISOString(),
        })
        localStorage.setItem('session_' + id, JSON.stringify(session))
        return { session_id: id, status: 'processing' }
    }

    const res = await apiFetch('/ingest', { method: 'POST', body })
    return res
}

/**
 * POST /ingest/audio
 * Upload audio file for transcription + analysis.
 * Body: FormData with field "file"
 * Response: { session_id: uuid, transcript: string, status: "processing" }
 */
export async function ingestAudio(file) {
    if (USE_MOCK) {
        const id = 'mock-audio-' + Date.now().toString(36)
        const session = Object.assign({}, demoSession, {
            session_id: id,
            platform: 'audio_upload',
            timestamp: new Date().toISOString(),
        })
        localStorage.setItem('session_' + id, JSON.stringify(session))
        return { session_id: id, transcript: 'Mock transcript of uploaded audio.', status: 'processing' }
    }

    const formData = new FormData()
    formData.append('file', file)
    const res = await apiFetch('/ingest/audio', { method: 'POST', body: formData })
    return res
}

/**
 * GET /health
 * Check if backend is running.
 */
export async function checkHealth() {
    try {
        const res = await apiFetch('/health')
        return res && res.status === 'ok'
    } catch {
        return false
    }
}

/**
 * Build WebSocket URL for /ws/alerts
 */
export function getWsAlertsUrl() {
    if (import.meta.env.VITE_WS_URL) return import.meta.env.VITE_WS_URL
    if (API_BASE) return API_BASE.replace(/^http/, 'ws') + '/ws/alerts'
    // Proxy mode: derive WS URL from current page host
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${proto}//${window.location.host}/ws/alerts`
}

export default {
    getSession,
    getSessions,
    ingestJson,
    ingestAudio,
    checkHealth,
    getWsAlertsUrl,
    normalizeSession,
}
