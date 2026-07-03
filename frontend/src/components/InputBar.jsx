export default function InputBar({ value, onChange, onSubmit, disabled }) {
  return (
    <form className="input-bar" onSubmit={onSubmit}>
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={disabled ? 'Upload a PDF first…' : 'Ask a question about your document…'}
        disabled={disabled}
        autoFocus
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  )
}
