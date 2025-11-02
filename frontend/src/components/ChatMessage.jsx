import React from 'react'

function ChatMessage({ message }) {
  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const roleName = message.role === 'user' ? 'You' : 'Apex'

  return (
    <div className={`message-bubble ${message.role} ${message.isError ? 'error' : ''}`}>
      <div className="message-header">
        <span className="message-role">{roleName}</span>
        <span className="message-time">{formatTime(message.timestamp)}</span>
      </div>
      <div className="message-content">{message.content}</div>
    </div>
  )
}

export default ChatMessage

