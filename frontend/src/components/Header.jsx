import React from 'react'

function Header({ onNewChat, messageCount, darkMode, toggleDarkMode, toggleSidebar, showSidebar }) {
  return (
    <div className="header">
      <div className="header-left">
        <button className="sidebar-toggle-btn" onClick={toggleSidebar} title="Toggle sidebar">
          {showSidebar ? '◀' : '☰'}
        </button>
        <span className="logo">Apex</span>
        {messageCount > 0 && (
          <p className="message-count">• {messageCount} messages</p>
        )}
      </div>
      <div className="header-right">
        <button
          className="dark-mode-btn"
          onClick={toggleDarkMode}
          title={darkMode ? "Light mode" : "Dark mode"}
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
        <button
          className="clear-btn"
          onClick={onNewChat}
        >
          + New chat
        </button>
      </div>
    </div>
  )
}

export default Header

