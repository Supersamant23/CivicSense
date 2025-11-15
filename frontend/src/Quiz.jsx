// frontend/src/Quiz.jsx

import React, { useState, useEffect } from 'react'

// This is the URL of your Flask server.
// Make sure your Flask server is running!
const API_URL = 'http://127.0.0.1:5000'

function Quiz() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)

  // 1. Fetch questions from the backend when the component loads
  useEffect(() => {
    // Start your Flask server (python app.py)
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
  }, []) // The empty array [] means this runs only once

  // 2. Handle when a user clicks an answer
  const handleAnswerChange = (questionId, answerValue) => {
    setAnswers({
      ...answers, // Keep old answers
      [questionId]: answerValue, // Add/update new answer
    })
  }

  // 3. Handle submitting the quiz
  const handleSubmit = (e) => {
    e.preventDefault()
    setLoading(true)

    // We just need the list of answer values, e.g., [5, 4, 3, ...]
    const answerValues = questions.map((q) => answers[q.id] || 3) // Default to 3 (Neutral)

    fetch(`${API_URL}/api/align`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ answers: answerValues }),
    })
      .then((res) => res.json())
      .then((data) => {
        setResults(data) // Save the alignment results
        setLoading(false)
      })
      .catch((err) => {
        console.error('Error submitting quiz:', err)
        setLoading(false)
      })
  }

  // --- Render the UI ---

  if (loading && !results) {
    return <div>Loading questions...</div>
  }

  // Show results *after* submitting
  if (results) {
    return (
      <div className="results-container">
        <h2>Your Results</h2>
        <div className="alignment-scores">
          <h3>Your Top Matches:</h3>
          {results.alignment_results.slice(0, 3).map((res, index) => (
            <div key={res.manifesto_id} className="result-item">
              <strong>
                {res.name} ({res.alignment}%)
              </strong>
              <p>{res.summary}</p>

              {/* --- MODIFIED SECTION --- */}
              {/* Only show details for the #1 match (index 0) */}
              {index === 0 && (
                <div className="top-match-details" style={{ marginTop: '1.5rem' }}>
                  
                  {/* Top Matching Policies (if they exist) */}
                  {res.top_matching_policies && res.top_matching_policies.length > 0 && (
                    <div className="policy-summary" style={{ marginTop: '1.5rem', background: 'none', border: 'none', padding: 0, boxShadow: 'none' }}>
                      <h5 style={{color: '#0f0f1a', marginBottom: '1rem'}}>Your Top Policy Alignments:</h5>
                      <ul>
                        {res.top_matching_policies.map((policy) => (
                          <li key={policy.tag} style={{ borderLeft: '5px solid var(--green)' }}> {/* Added green border */}
                            <strong>{policy.tag}</strong> {/* Score removed as requested */}
                            {/* Add a paragraph for the explanation, matching the pattern */}
                            <p style={{margin: 0, marginTop: '0.5rem', fontSize: '0.95rem'}}>
                              {policy.explanation}
                            </p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* --- NEW SECTION: TOP DISAGREEMENTS --- */}
                  {res.top_disagreements && res.top_disagreements.length > 0 && (
                    <div className="policy-summary" style={{ marginTop: '1.5rem', background: 'none', border: 'none', padding: 0, boxShadow: 'none' }}>
                      <h5 style={{color: '#0f0f1a', marginBottom: '1rem'}}>Your Top Policy Disagreements:</h5>
                      <ul>
                        {res.top_disagreements.map((policy) => (
                          <li key={policy.tag} style={{ borderLeft: '5px solid var(--saffron)' }}> {/* Added saffron/red border */}
                            <strong>{policy.tag}</strong> {/* Score removed as requested */}
                            <p style={{margin: 0, marginTop: '0.5rem', fontSize: '0.95rem'}}>
                              {policy.explanation}
                            </p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {/* --- END NEW SECTION --- */}

                </div>
              )}
              {/* --- END MODIFIED SECTION --- */}

            </div>
          ))}
        </div>

        <button onClick={() => setResults(null)}>Take Quiz Again</button>
      </div>
    )
  }

  // Show the quiz by default
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