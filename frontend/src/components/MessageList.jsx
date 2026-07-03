import { useEffect, useRef } from 'react'

function TypingIndicator() {
  return (
    <div className="row assistant">
      <span className="avatar">🤖</span>
      <div className="bubble-wrap">
        <div className="bubble typing">
          <span /><span /><span />
        </div>
      </div>
    </div>
  )
}

function Message({ msg }) {
  return (
    <div className={`row ${msg.role}`}>
      {msg.role !== 'user' && <span className="avatar">🤖</span>}
      <div className="bubble-wrap">
        <div className="bubble">{msg.text}</div>
        {msg.sources?.length > 0 && (
          <div className="meta">
            📎 {msg.sources.join(', ')}
            {msg.pages?.length > 0 && `  ·  Pages: ${msg.pages.join(', ')}`}
          </div>
        )}
      </div>
      {msg.role === 'user' && <span className="avatar">🧑</span>}
    </div>
  )
}

export default function MessageList({ messages, loading, emptyHint }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <div className="chat">
      {messages.length === 0 && (
        <div className="empty">{emptyHint}</div>
      )}
      {messages.map((msg) => (
        <Message key={msg.id} msg={msg} />
      ))}
      {loading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  )
}
