const BASE_URL = `${import.meta.env.VITE_BACKEND_URL || ''}/api`

export async function apiRequest(endpoint, options = {}) {
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      credentials: 'include',
      ...options,
    })
    const data = await res.json()
    return { ok: res.ok, data }
  } catch {
    return { ok: false, data: { error: 'Network error. Is the backend running?' } }
  }
}
