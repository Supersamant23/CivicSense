// frontend/src/App.jsx

import React from 'react'
import './App.css' // <-- ADD THIS LINE
import Quiz from './Quiz'

function App() {
  return (
    <div className="app-container">
      <h1>Civic Sense</h1>
      <p>Helping you understand where you stand.</p>
      
      <hr />
      <Quiz />
      <hr />
    </div>
  )
}

export default App