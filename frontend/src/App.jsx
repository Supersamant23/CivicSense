// frontend/src/App.jsx
// (No changes)

import React from 'react'
import './App.css'
import Quiz from './Quiz'

function App() {
  return (
    <div className="app-container">
      <div className="content-wrapper fade-in-up">
        <header className="app-header">
          <h1 className="shimmer-text">Civic Sense</h1>
          <p>Helping you understand where you stand.</p>
        </header>
        
        <hr className="minimal-divider" />

        <main>
          <Quiz />
        </main>

        <footer className="app-footer">
          <p>&copy; {new Date().getFullYear()} Jai Hind</p>
        </footer>
      </div>
    </div>
  )
}

export default App