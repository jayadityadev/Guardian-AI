import demoSession from '../mock/demoSession.json'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

function normalizeSession(raw) {
    if (!raw) return null
    const flags = Array.isArray(raw.flags) ? raw.flags : raw.raw_flag_json || []

    return {
        session_id: raw.session_id || raw.id || raw.sessionId || (raw.sessionId && String(raw.sessionId)),
        platform: raw.platform || 'json_upload',
        timestamp: raw.timestamp || raw.created_at || new Date().toISOString(),
        risk_score: raw.risk_score != null ? raw.risk_score : raw.riskScore != null ? raw.riskScore : raw.score || 0,
        confidence: raw.confidence != null ? raw.confidence : raw.confidenceScore || 0,
        grooming_stage: raw.grooming_stage || raw.groomingStage || raw.stage || 'none',
        flags: flags,
        categories: raw.categories || (flags ? Array.from(new Set(flags.map(f => f.type))) : []),
        stage_progression: raw.stage_progression || raw.stage_progression_json || raw.stageProgression || {},
        recommendation: raw.recommendation || 'monitor',
        drift_signals: raw.drift_signals || raw.drift_json || {},
    }
}

async function apiFetch(path, opts = {}) {
    const base = API_BASE.replace(/\/$/, '')
    const url = path.startsWith('http') ? path : base + (path.startsWith('/') ? path : '/' + path)
    const { method = 'GET', body, headers = {} } = opts

    const init = { method, headers: { ...headers } }
    if (body instanceof FormData) {
        init.body = body
        // let browser set Content-Type
    } else if (body != null) {
        init.headers['Content-Type'] = 'application/json'
        init.body = JSON.stringify(body)
    }

    const res = await fetch(url, init)
    if (!res.ok) {
        const text = await res.text().catch(() => '')
        const err = new Error('API error: ' + res.status + ' ' + res.statusText + (text ? ' - ' + text : ''))
        err.status = res.status
        err.body = text
        throw err
    }

    const contentType = res.headers.get('content-type') || ''
    if (contentType.includes('application/json')) return res.json()
    return res.text()
}

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

export async function getSessions() {
    if (USE_MOCK) {
        const keys = Object.keys(localStorage).filter(k => k.startsWith('session_'))
        let sessions = keys.map(k => {
            try { return normalizeSession(JSON.parse(localStorage.getItem(k))) } catch (e) { return null }
        }).filter(Boolean)
        if (sessions.length === 0) sessions = [normalizeSession(demoSession)]
        sessions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        return sessions
    }

    const res = await apiFetch('/sessions')
    const arr = Array.isArray(res) ? res : (res.sessions || [])
    return arr.map(normalizeSession)
}

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

export async function ingestAudio(formData) {
    if (USE_MOCK) {
        return ingestJson({ platform: 'audio_upload', messages: [] })
    }

    const res = await apiFetch('/ingest/audio', { method: 'POST', body: formData })
    return res
}

export default {
    getSession,
    getSessions,
    ingestJson,
    ingestAudio,
    normalizeSession,
}
