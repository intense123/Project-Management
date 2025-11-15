function ASTViewer({ astData, onClose }) {
  const renderAST = (node, depth = 0) => {
    if (!node || typeof node !== 'object') {
      return <span className="ast-value">{JSON.stringify(node)}</span>
    }

    if (node.type) {
      return (
        <div className="ast-node" style={{ marginLeft: `${depth * 20}px` }}>
          <div className="ast-type">
            <span className="ast-type-name">{node.type}</span>
          </div>
          <div className="ast-fields">
            {Object.entries(node).map(([key, value]) => {
              if (key === 'type') return null
              return (
                <div key={key} className="ast-field">
                  <span className="ast-field-name">{key}:</span>
                  {Array.isArray(value) ? (
                    <div className="ast-array">
                      {value.map((item, idx) => (
                        <div key={idx}>{renderAST(item, depth + 1)}</div>
                      ))}
                    </div>
                  ) : typeof value === 'object' && value !== null ? (
                    renderAST(value, depth + 1)
                  ) : (
                    <span className="ast-value"> {JSON.stringify(value)}</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )
    }

    return <span className="ast-value">{JSON.stringify(node)}</span>
  }

  return (
    <div className="ast-viewer-overlay">
      <div className="ast-viewer-container">
        <div className="ast-viewer-header">
          <h3>🌳 Abstract Syntax Tree (AST)</h3>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>
        <div className="ast-viewer-content">
          {!astData ? (
            <div className="ast-info">
              <p>⚠️ No AST data available</p>
            </div>
          ) : astData.supported === false ? (
            <div className="ast-info">
              <p>ℹ️ {astData.message}</p>
              <p style={{ marginTop: '12px', fontSize: '0.875rem', color: '#6b7280' }}>
                AST visualization is currently only available for Python code. Support for other languages may be added in the future.
              </p>
            </div>
          ) : astData.error ? (
            <div className="ast-error">
              <p>❌ Error generating AST:</p>
              <code>{astData.error}</code>
            </div>
          ) : astData.message ? (
            <div className="ast-info">
              <p>ℹ️ {astData.message}</p>
            </div>
          ) : (
            <div className="ast-tree">
              {renderAST(astData.ast || astData)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ASTViewer
