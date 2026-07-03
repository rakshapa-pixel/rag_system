export default function Header({ username, uploading, onFileSelect, onLogout }) {
  return (
    <header>
      <div className="header-left">
        <span className="logo">📄</span>
        <div>
          <h1>RAG Chat</h1>
          <p>Ask questions about your PDF documents</p>
        </div>
      </div>
      <div className="header-right">
        <label className={`upload-btn ${uploading ? 'busy' : ''}`}>
          {uploading ? 'Uploading…' : '+ Upload PDF'}
          <input
            type="file"
            accept=".pdf"
            onChange={e => onFileSelect(e.target.files[0])}
            disabled={uploading}
            hidden
          />
        </label>
        <div className="user-info">
          <span className="username">👤 {username}</span>
          <button className="logout-btn" onClick={onLogout}>Log out</button>
        </div>
      </div>
    </header>
  )
}
