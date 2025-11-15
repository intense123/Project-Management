import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

function CodeDisplay({ code, language, onDownload, onEvaluate, onShowAST, fileExtension }) {
  const [copied, setCopied] = useState(false)
  const isPython = language === 'python' || language === 'Python'

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleShowAST = () => {
    if (!isPython) {
      alert('AST visualization is currently supported for Python code only.')
      return
    }
    onShowAST()
  }

  return (
    <div className="code-display-container">
      <div className="code-header">
        <div className="code-language-badge">{language || 'code'}</div>
        <div className="code-actions">
          <button onClick={copyToClipboard} className="code-action-btn">
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>
          <button onClick={() => onDownload(code, `code${fileExtension}`)} className="code-action-btn">
            ⬇️ Download
          </button>
          <button 
            onClick={handleShowAST} 
            className="code-action-btn"
            title={isPython ? 'Show Abstract Syntax Tree' : 'AST only available for Python'}
            style={!isPython ? { opacity: 0.5, cursor: 'not-allowed' } : {}}
          >
            🌳 Show AST
          </button>
          <button onClick={() => onEvaluate(code, language)} className="code-action-btn">
            📊 Evaluate
          </button>
        </div>
      </div>
      <div className="code-content">
        <SyntaxHighlighter 
          language={language || 'python'} 
          style={vscDarkPlus}
          showLineNumbers
          customStyle={{
            margin: 0,
            borderRadius: '0 0 8px 8px',
            fontSize: '14px'
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  )
}

export default CodeDisplay
