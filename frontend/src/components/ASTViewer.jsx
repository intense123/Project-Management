function ASTViewer({ astData, onClose }) {
  const renderTreeSitterAST = (node, depth = 0, index = 0) => {
    if (!node || typeof node !== 'object') {
      return <span className="ast-value">{JSON.stringify(node)}</span>
    }

    const isTreeSitter = node.start && node.end
    
    if (node.type) {
      return (
        <div className="ast-node" style={{ marginLeft: `${depth * 20}px` }} key={`${depth}-${index}`}>
          <div className="ast-type">
            <span className="ast-type-name">{node.type}</span>
            {isTreeSitter && (
              <span className="ast-position">
                ({node.start.row}:{node.start.column} - {node.end.row}:{node.end.column})
              </span>
            )}
          </div>
          <div className="ast-fields">
            {node.text && (
              <div className="ast-field">
                <span className="ast-field-name">text:</span>
                <span className="ast-text-value">"{node.text}"</span>
              </div>
            )}
            {node.children && (
              <div className="ast-field">
                <span className="ast-field-name">children ({node.children.length}):</span>
                <div className="ast-array">
                  {node.children.map((child, idx) => (
                    <div key={idx}>{renderTreeSitterAST(child, depth + 1, idx)}</div>
                  ))}
                </div>
              </div>
            )}
            {!isTreeSitter && Object.entries(node).map(([key, value]) => {
              if (key === 'type') return null
              return (
                <div key={key} className="ast-field">
                  <span className="ast-field-name">{key}:</span>
                  {Array.isArray(value) ? (
                    <div className="ast-array">
                      {value.map((item, idx) => (
                        <div key={idx}>{renderTreeSitterAST(item, depth + 1, idx)}</div>
                      ))}
                    </div>
                  ) : typeof value === 'object' && value !== null ? (
                    renderTreeSitterAST(value, depth + 1, 0)
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
          <h3>🌳 Abstract Syntax Tree</h3>
          {astData?.method && (
            <span className="ast-method-badge">{astData.method}</span>
          )}
          {astData?.language && (
            <span className="ast-lang-badge">{astData.language.toUpperCase()}</span>
          )}
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
                Supported languages: Python, Java, JavaScript, C, C++
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
            <>
              <div className="ast-info-bar">
                <span>📊 Total nodes: {countNodes(astData.ast || astData)}</span>
                <span>📏 Max depth: {getMaxDepth(astData.ast || astData)}</span>
              </div>
              <div className="ast-tree">
                {renderTreeSitterAST(astData.ast || astData, 0, 0)}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function countNodes(node) {
  if (!node || typeof node !== 'object') return 0
  let count = 1
  if (node.children) {
    count += node.children.reduce((sum, child) => sum + countNodes(child), 0)
  }
  Object.values(node).forEach(value => {
    if (Array.isArray(value)) {
      count += value.reduce((sum, item) => sum + countNodes(item), 0)
    } else if (typeof value === 'object' && value !== null && value.type) {
      count += countNodes(value)
    }
  })
  return count
}

function getMaxDepth(node, depth = 0) {
  if (!node || typeof node !== 'object') return depth
  let maxDepth = depth
  if (node.children) {
    node.children.forEach(child => {
      maxDepth = Math.max(maxDepth, getMaxDepth(child, depth + 1))
    })
  }
  Object.values(node).forEach(value => {
    if (Array.isArray(value)) {
      value.forEach(item => {
        if (item && typeof item === 'object' && item.type) {
          maxDepth = Math.max(maxDepth, getMaxDepth(item, depth + 1))
        }
      })
    } else if (typeof value === 'object' && value !== null && value.type) {
      maxDepth = Math.max(maxDepth, getMaxDepth(value, depth + 1))
    }
  })
  return maxDepth
}

export default ASTViewer
