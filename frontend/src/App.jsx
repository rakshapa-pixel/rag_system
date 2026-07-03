import { useState, useEffect } from 'react'
import { getMe, logout } from './api/auth.js'
import AuthPage from './components/AuthPage.jsx'
import ChatPage from './components/ChatPage.jsx'
import './App.css'

export default function App() {
  const [username, setUsername] = useState(null) // null = loading

  useEffect(() => {
    getMe().then(({ data }) => {
      setUsername(data.authenticated ? data.username : false)
    })
  }, [])

  const handleLogout = async () => {
    await logout()
    setUsername(false)
  }

  if (username === null) {
    return (
      <div className="auth-bg">
        <div className="auth-card" style={{ textAlign: 'center', color: '#6b7280' }}>
          Loading…
        </div>
      </div>
    )
  }

  if (!username) {
    return <AuthPage onAuth={setUsername} />
  }

  return <ChatPage username={username} onLogout={handleLogout} />
}
