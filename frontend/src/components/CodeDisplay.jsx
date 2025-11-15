import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

function CodeDisplay({ code, language, onDownload, onEvaluate, onShowAST, fileExtension }) {
  const [copied, setCopied] = useState(false)
  const supportedASTLanguages = ['python', 'java', 'javascript', 'c', 'cpp', 'c_sharp']
  const isASTSupported = supportedASTLanguages.includes(language?.toLowerCase())

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
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
            onClick={onShowAST} 
            className="code-action-btn"
            title={isASTSupported ? 'Show Abstract Syntax Tree' : 'AST available for: Python, Java, JavaScript, C, C++'}
            style={!isASTSupported ? { opacity: 0.5, cursor: 'not-allowed' } : {}}
            disabled={!isASTSupported}
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
