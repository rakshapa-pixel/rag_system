import { useState, useEffect } from 'react'
import { signup, login } from '../api/auth.js'
import { apiRequest } from '../api/client.js'

export default function AuthPage({ onAuth }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [googleEnabled, setGoogleEnabled] = useState(false)

  useEffect(() => {
    // Check if Google OAuth is configured on the backend
    apiRequest('/auth/providers').then(({ ok, data }) => {
      if (ok) setGoogleEnabled(data.google)
    })

    // Show error if redirected back from a failed OAuth attempt
    const params = new URLSearchParams(window.location.search)
    const oauthError = params.get('oauth_error')
    if (oauthError) {
      setError(oauthError)
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const { ok, data } = mode === 'signup'
      ? await signup(username.trim(), password)
      : await login(username.trim(), password)

    setLoading(false)
    if (ok) {
      onAuth(data.username)
    } else {
      setError(data.error)
    }
  }

  const toggleMode = () => {
    setMode(m => m === 'login' ? 'signup' : 'login')
    setUsername('')
    setPassword('')
    setError('')
  }

  return (
    <div className="auth-bg">
      <div className="auth-card">
        <div className="auth-logo">📄</div>
        <h1 className="auth-title">RAG Chat</h1>
        <p className="auth-subtitle">
          {mode === 'login' ? 'Welcome back' : 'Create your account'}
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
          <label>Username</label>
          <input
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="Enter your username"
            autoFocus
            required
          />

          <label>Password</label>
          <div className="password-wrap">
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder={mode === 'signup' ? 'At least 6 characters' : 'Enter password'}
              required
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(v => !v)}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? '🙈' : '👁️'}
            </button>
          </div>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? '…' : mode === 'login' ? 'Log In' : 'Sign Up'}
          </button>
        </form>

        {googleEnabled && (
          <>
            <div className="auth-divider"><span>or</span></div>
            <a href={`${import.meta.env.VITE_BACKEND_URL || ''}/api/auth/google`} className="google-btn">
              <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
                <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
                <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
                <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
                <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </a>
          </>
        )}

        <p className="auth-switch">
          {mode === 'login'
            ? <>Don't have an account? <button onClick={toggleMode}>Sign up</button></>
            : <>Already have an account? <button onClick={toggleMode}>Log in</button></>}
        </p>
      </div>
    </div>
  )
}
