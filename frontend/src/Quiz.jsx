import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const API_URL = 'http://127.0.0.1:5000'

function Quiz() {
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)

  // NEW: Back button visibility
  const [showBack, setShowBack] = useState(true)
  let lastScroll = window.pageYOffset

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

    // Scroll listener for back button
    const handleScroll = () => {
      const currentScroll = window.pageYOffset
      setShowBack(lastScroll > currentScroll || currentScroll < 10)
      lastScroll = currentScroll
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
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

  if (loading && !results) return <div>Loading questions...</div>

  const backButton = (
    <Link
      to="/"
      className={`primary-btn fixed-back-btn ${showBack ? 'show' : 'hide'}`}
    >
      Back to Home
    </Link>
  )

  if (results) {
    return (
      <div className="results-container">
        <h2>Your Results</h2>
        <div className="alignment-scores">
          <h3>Your Top Matches:</h3>
          {results.alignment_results.slice(0, 3).map((res) => (
            <div key={res.manifesto_id} className="result-item">
              <strong>
                {res.name} ({res.alignment}%)
              </strong>
              <p>{res.summary}</p>
            </div>
          ))}
        </div>
        <div className="policy-summary">
          <h3>Your Policy Preferences:</h3>
          <ul>
            {results.user_preferences.map(([tag, score]) => (
              <li key={tag}>
                {tag}: {score} / 5
              </li>
            ))}
          </ul>
        </div>
        <button onClick={() => setResults(null)}>Take Quiz Again</button>
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
