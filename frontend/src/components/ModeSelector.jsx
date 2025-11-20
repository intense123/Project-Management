function ModeSelector({ mode, setMode }) {
  return (
    <div className="mode-selector">
      <label htmlFor="chat-mode">Mode:</label>
      <select 
        id="chat-mode" 
        value={mode} 
        onChange={(e) => setMode(e.target.value)}
        className="mode-dropdown"
      >
        <option value="general">💬 General Chat Mode</option>
        <option value="code">💻 Code Mode</option>
      </select>
    </div>
  )
}

export default ModeSelector
