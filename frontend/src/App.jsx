import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import ChatMessage from './components/ChatMessage'
import InputArea from './components/InputArea'
import Header from './components/Header'

function App() {
  const [conversations, setConversations] = useState([])
  const [currentConversationId, setCurrentConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [showSidebar, setShowSidebar] = useState(true)
  const messagesEndRef = useRef(null)

  // Load conversations from localStorage on mount
  useEffect(() => {
    const savedConversations = localStorage.getItem('apex-conversations')
    const savedDarkMode = localStorage.getItem('apex-darkmode')
    
    if (savedDarkMode) {
      setDarkMode(JSON.parse(savedDarkMode))
    }
    
    if (savedConversations) {
      const parsed = JSON.parse(savedConversations)
      setConversations(parsed)
      
      // Load the most recent conversation
      if (parsed.length > 0) {
        const mostRecent = parsed[0]
        setCurrentConversationId(mostRecent.id)
        setMessages(mostRecent.messages)
      }
    }
  }, [])

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('apex-conversations', JSON.stringify(conversations))
    }
  }, [conversations])

  // Save current conversation when messages change
  useEffect(() => {
    if (currentConversationId && messages.length > 0) {
      setConversations(prev => prev.map(conv => 
        conv.id === currentConversationId 
          ? { ...conv, messages, updatedAt: new Date().toISOString() }
          : conv
      ))
    }
  }, [messages, currentConversationId])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    // Create a new conversation if none exists
    if (!currentConversationId) {
      const newConv = {
        id: Date.now().toString(),
        title: input.slice(0, 30) + (input.length > 30 ? '...' : ''),
        messages: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      setConversations(prev => [newConv, ...prev])
      setCurrentConversationId(newConv.id)
    }

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    
    // Update conversation title if it's the first message
    if (messages.length === 0 && currentConversationId) {
      setConversations(prev => prev.map(conv =>
        conv.id === currentConversationId
          ? { ...conv, title: input.slice(0, 30) + (input.length > 30 ? '...' : '') }
          : conv
      ))
    }
    
    setInput('')
    setIsLoading(true)

    try {
      // Build conversation history for API
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await axios.post('http://localhost:5001/api/chat', {
        message: input,
        history: history
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const createNewChat = () => {
    const newConversation = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    setConversations(prev => [newConversation, ...prev])
    setCurrentConversationId(newConversation.id)
    setMessages([])
  }

  const switchConversation = (conversationId) => {
    const conversation = conversations.find(c => c.id === conversationId)
    if (conversation) {
      setCurrentConversationId(conversationId)
      setMessages(conversation.messages)
    }
  }

  const deleteConversation = (conversationId) => {
    const updated = conversations.filter(c => c.id !== conversationId)
    setConversations(updated)
    
    if (conversationId === currentConversationId) {
      if (updated.length > 0) {
        setCurrentConversationId(updated[0].id)
        setMessages(updated[0].messages)
      } else {
        setCurrentConversationId(null)
        setMessages([])
      }
    }
    
    localStorage.setItem('apex-conversations', JSON.stringify(updated))
  }

  const toggleDarkMode = () => {
    const newMode = !darkMode
    setDarkMode(newMode)
    localStorage.setItem('apex-darkmode', JSON.stringify(newMode))
  }

  const toggleSidebar = () => {
    setShowSidebar(!showSidebar)
  }

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      {/* Sidebar */}
      {showSidebar && (
        <div className="sidebar">
          <button className="new-chat-btn" onClick={createNewChat}>
            + New Chat
          </button>
          <div className="conversations-list">
            {conversations.map(conv => (
              <div
                key={conv.id}
                className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
                onClick={() => switchConversation(conv.id)}
              >
                <div className="conversation-title">{conv.title}</div>
                <button
                  className="delete-conversation-btn"
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteConversation(conv.id)
                  }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="container">
        <Header 
          onNewChat={createNewChat}
          messageCount={messages.length}
          darkMode={darkMode}
          toggleDarkMode={toggleDarkMode}
          toggleSidebar={toggleSidebar}
          showSidebar={showSidebar}
        />
        
        <div className="chat-container">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-icon">💬</div>
              <h1 className="welcome-title">How can I help you today?</h1>
              <p className="welcome-subtitle">I'm Apex, your AI assistant. I can help you with analysis, research, writing, coding, and more.</p>
              <div className="suggestion-cards">
                <button 
                  className="suggestion-card"
                  onClick={() => setInput("Explain quantum computing in simple terms")}
                >
                  <span className="suggestion-icon">💡</span>
                  <span>Explain quantum computing in simple terms</span>
                </button>
                <button 
                  className="suggestion-card"
                  onClick={() => setInput("Help me write a Python function to sort a list")}
                >
                  <span className="suggestion-icon">💻</span>
                  <span>Help me write a Python function to sort a list</span>
                </button>
                <button 
                  className="suggestion-card"
                  onClick={() => setInput("Give me tips for better writing")}
                >
                  <span className="suggestion-icon">✏️</span>
                  <span>Give me tips for better writing</span>
                </button>
                <button 
                  className="suggestion-card"
                  onClick={() => setInput("Analyze the pros and cons of remote work")}
                >
                  <span className="suggestion-icon">📊</span>
                  <span>Analyze the pros and cons of remote work</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="messages-container">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {isLoading && (
                <div className="typing-indicator">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <InputArea
          input={input}
          setInput={setInput}
          onSend={sendMessage}
          onKeyPress={handleKeyPress}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}

export default App

