import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const API_URL = 'http://127.0.0.1:5000'

function Quiz() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expandedManifesto, setExpandedManifesto] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/api/quiz`)
      .then((res) => res.json())
      .then((data) => {
        setQuestions(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Error fetching questions:', err)
        setLoading(false)
      })
  }, [])

  const handleAnswerChange = (questionId, answerValue) => {
    setAnswers({ ...answers, [questionId]: answerValue })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setLoading(true)

    const answerValues = questions.map((q) => answers[q.id] || 3)

    fetch(`${API_URL}/api/align`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers: answerValues }),
    })
      .then((res) => res.json())
      .then((data) => {
        setResults(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Error submitting quiz:', err)
        setLoading(false)
      })
  }

  const getAlignmentColor = (percentage) => {
    if (percentage >= 80) return '#00c26e'
    if (percentage >= 60) return '#7cb342'
    if (percentage >= 40) return '#ffa726'
    return '#ff6b6b'
  }

  const getMatchQuality = (percentage) => {
    if (percentage >= 80) return 'Excellent Match'
    if (percentage >= 60) return 'Good Match'
    if (percentage >= 40) return 'Moderate Match'
    return 'Low Match'
  }

  // Calculate policy alignment details
  const getPolicyBreakdown = (manifestoId) => {
    if (!results || !results.alignment_results) return null

    const manifesto = results.alignment_results.find(m => m.manifesto_id === manifestoId)
    if (!manifesto || !manifesto.policy_details) return null

    return manifesto.policy_details
  }

  if (loading && !results) return <div className="loading-spinner">Loading questions...</div>

  if (results) {
    return (
      <div className="results-container">
        <h2>Your Political Alignment Results</h2>
        
        <div className="alignment-scores">
          <h3>Your Top Matches:</h3>
          {results.alignment_results.slice(0, 3).map((res, index) => (
            <div key={res.manifesto_id} className="result-item">
              <div className="result-header">
                <strong className="manifesto-name">
                  {index === 0 && '🥇 '}
                  {index === 1 && '🥈 '}
                  {index === 2 && '🥉 '}
                  {res.name}
                </strong>
                <div className="alignment-badge" style={{ background: getAlignmentColor(res.alignment) }}>
                  {res.alignment}% Match
                </div>
              </div>
              
              <div className="match-quality" style={{ color: getAlignmentColor(res.alignment) }}>
                {getMatchQuality(res.alignment)}
              </div>
              
              <p className="manifesto-summary">{res.summary}</p>

              {res.policy_details && (
                <button 
                  className="view-details-btn"
                  onClick={() => setExpandedManifesto(
                    expandedManifesto === res.manifesto_id ? null : res.manifesto_id
                  )}
                >
                  {expandedManifesto === res.manifesto_id ? '▼ Hide Details' : '▶ View Policy Breakdown'}
                </button>
              )}

              {expandedManifesto === res.manifesto_id && res.policy_details && (
                <div className="policy-breakdown">
                  <h4>How This Manifesto Reflects Your Views:</h4>
                  <div className="policy-grid">
                    {Object.entries(res.policy_details).map(([policy, details]) => {
                      const userScore = details.your_position
                      const manifestoScore = details.manifesto_position
                      const alignment = details.alignment
                      
                      return (
                        <div key={policy} className="policy-card">
                          <div className="policy-header">
                            <span className="policy-name">{policy}</span>
                            <span 
                              className="policy-alignment"
                              style={{ 
                                color: alignment >= 70 ? '#00c26e' : alignment >= 40 ? '#ffa726' : '#ff6b6b'
                              }}
                            >
                              {alignment}% aligned
                            </span>
                          </div>
                          
                          <div className="position-comparison">
                            <div className="position-bar">
                              <span className="bar-label">You</span>
                              <div className="bar-container">
                                <div 
                                  className="bar-fill your-bar"
                                  style={{ width: `${(userScore / 5) * 100}%` }}
                                />
                              </div>
                              <span className="bar-value">{userScore}/5</span>
                            </div>
                            
                            <div className="position-bar">
                              <span className="bar-label">Party</span>
                              <div className="bar-container">
                                <div 
                                  className="bar-fill manifesto-bar"
                                  style={{ width: `${(manifestoScore / 5) * 100}%` }}
                                />
                              </div>
                              <span className="bar-value">{manifestoScore}/5</span>
                            </div>
                          </div>
                          
                          <p className="policy-explanation">{details.explanation}</p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="policy-summary">
          <h3>Your Overall Policy Preferences:</h3>
          <div className="preference-bars">
            {results.user_preferences.map(([tag, score]) => (
              <div key={tag} className="preference-item">
                <div className="preference-header">
                  <span className="preference-label">{tag}</span>
                  <span className="preference-score">{score} / 5</span>
                </div>
                <div className="preference-bar-container">
                  <div 
                    className="preference-bar-fill"
                    style={{ 
                      width: `${(score / 5) * 100}%`,
                      background: `linear-gradient(90deg, #ff7a00, #00c26e)`
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <button onClick={() => setResults(null)} className="retake-btn">
          Take Quiz Again
        </button>
      </div>
    )
  }

  return (
    <form className="quiz-form" onSubmit={handleSubmit}>
      <h2>Policy Quiz</h2>
      {questions.map((q, index) => (
        <div key={q.id} className="question-block">
          <p>
            {index + 1}. {q.question}
          </p>
          <div className="options-group">
            {[1, 2, 3, 4, 5].map((value) => (
              <label key={value}>
                <input
                  type="radio"
                  name={`question-${q.id}`}
                  value={value}
                  onChange={() => handleAnswerChange(q.id, value)}
                  required
                />
                {q.options[value]}
              </label>
            ))}
          </div>
        </div>
      ))}
      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'See Your Results'}
      </button>
    </form>
  )
}

export default Quiz