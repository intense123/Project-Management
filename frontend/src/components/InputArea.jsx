import React from 'react'

function InputArea({ input, setInput, onSend, onKeyPress, isLoading }) {
  return (
    <div className="input-area">
      <div className="input-wrapper">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={onKeyPress}
          placeholder="Message Apex..."
          disabled={isLoading}
          rows={1}
        />
      </div>
      <button
        className="send-btn"
        onClick={onSend}
        disabled={isLoading || !input.trim()}
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </div>
  )
}

export default InputArea

