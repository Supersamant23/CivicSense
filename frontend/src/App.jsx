// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import Quiz from './Quiz';
import LandingPage from './LandingPage';

// --- COMPONENT 1: The Top-Left Button ---
// This component correctly renders the button in the top-left corner
// and hides it on the homepage.
function FixedBackButton() {
  const location = useLocation();

  if (location.pathname === '/') {
    return null;
  }

  return (
    <Link to="/" className="fixed-back-btn">
      Back to Home
    </Link>
  );
}


// --- COMPONENT 2: Your Main App ---
function App() {
  return (
    <Router>
      <div className="app-container">
        
        {/* HERE is the one and only button. 
          It is OUTSIDE the content wrapper. 
        */}
        <FixedBackButton />

        {/* This div animates your content */}
        <div className="content-wrapper fade-in-up">
          <Routes>
            {/* Landing Page */}
            <Route path="/" element={<LandingPage />} />

            {/* Quiz Page */}
            <Route
              path="/quiz"
              element={
                <>
                  {/*
                    LOOK: The <header> block below is CLEAN.
                    It ONLY has the <h1> and <p> tags.
                    The second and third buttons are GONE.
                  */}
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
                </>
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;