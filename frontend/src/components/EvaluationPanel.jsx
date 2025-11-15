import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'

function EvaluationPanel({ 
  referenceCode, 
  setReferenceCode, 
  evaluationResult, 
  isEvaluating,
  onClose,
  onCalculate,
  generatedCode,
  language
}) {
  const [uploadedFileName, setUploadedFileName] = useState('')
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (file) {
      setUploadedFileName(file.name)
      const reader = new FileReader()
      reader.onload = (e) => {
        setReferenceCode(e.target.result)
      }
      reader.readAsText(file)
    }
  }, [setReferenceCode])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'text/*': ['.py', '.java', '.js', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.ts']
    },
    multiple: false
  })

  return (
    <>
      <div className="drawer-overlay" onClick={onClose}></div>
      <div className="evaluation-drawer">
        <div className="evaluation-header">
          <h3>📊 Code Evaluation (CodeBLEU)</h3>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>
        <div className="evaluation-scroll-content">

      <div className="reference-input-section">
        <label>Reference Code (Ground Truth):</label>
        
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''} ${uploadedFileName ? 'has-file' : ''}`}>
          <input {...getInputProps()} />
          {isDragActive ? (
            <p>📂 Drop the code file here...</p>
          ) : uploadedFileName ? (
            <p>✅ File uploaded: {uploadedFileName}</p>
          ) : (
            <p>📁 Drag & drop a code file here, or click to select</p>
          )}
        </div>

        <textarea
          value={referenceCode}
          onChange={(e) => {
            setReferenceCode(e.target.value)
            setUploadedFileName('')
          }}
          placeholder="Or paste reference code here..."
          className="reference-textarea"
          rows={12}
        />

        {referenceCode.trim() && !isEvaluating && (
          <button 
            onClick={() => onCalculate(generatedCode, language)} 
            className="calculate-btn"
            disabled={!referenceCode.trim()}
          >
            📊 Calculate CodeBLEU Score
          </button>
        )}
      </div>

      {isEvaluating && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <span>Evaluating code...</span>
        </div>
      )}

      {evaluationResult && (
        <div className="evaluation-results">
          <h4>Evaluation Results:</h4>
          
          <div className="score-main">
            <div className="score-value">{(evaluationResult.codebleu_score * 100).toFixed(2)}%</div>
            <div className="score-label">Overall CodeBLEU Score</div>
          </div>

          <div className="score-grid">
            <div className="score-item">
              <div className="score-num">{(evaluationResult.ngram_match_score * 100).toFixed(2)}%</div>
              <div className="score-name">N-gram Match</div>
            </div>
            <div className="score-item">
              <div className="score-num">{(evaluationResult.weighted_ngram_match_score * 100).toFixed(2)}%</div>
              <div className="score-name">Weighted N-gram</div>
            </div>
            <div className="score-item">
              <div className="score-num">{(evaluationResult.syntax_match_score * 100).toFixed(2)}%</div>
              <div className="score-name">Syntax Match</div>
            </div>
            <div className="score-item">
              <div className="score-num">{(evaluationResult.dataflow_match_score * 100).toFixed(2)}%</div>
              <div className="score-name">Dataflow Match</div>
            </div>
          </div>

          <div className={`score-interpretation ${getInterpretationClass(evaluationResult.codebleu_score)}`}>
            {getInterpretationText(evaluationResult.codebleu_score)}
          </div>
        </div>
      )}
        </div>
      </div>
    </>
  )
}

function getInterpretationClass(score) {
  if (score >= 0.8) return 'excellent'
  if (score >= 0.6) return 'good'
  if (score >= 0.4) return 'fair'
  return 'poor'
}

function getInterpretationText(score) {
  if (score >= 0.8) return '✅ Excellent match! The generated code is highly similar to the reference.'
  if (score >= 0.6) return '👍 Good match! The generated code is reasonably similar.'
  if (score >= 0.4) return '⚠️ Fair match. Some differences detected.'
  return '❌ Poor match. Significant differences detected.'
}

export default EvaluationPanel
