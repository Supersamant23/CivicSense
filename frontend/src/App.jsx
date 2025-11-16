// frontend/src/App.jsx
import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import './App.css';
import Quiz from './Quiz';
import LandingPage from './LandingPage';
import Auth from './Auth';
import { supabase } from './supabaseClient';

// Protected Route Component
function ProtectedRoute({ children }) {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }

  if (!session) {
    return <Navigate to="/auth" replace />;
  }

  return children;
}

// Top-Left Button Component
function FixedBackButton() {
  const location = useLocation();

  if (location.pathname === '/' || location.pathname === '/auth') {
    return null;
  }

  return (
    <div className="fixed-button-group">
      <Link to="/" className="fixed-back-btn">
        Back to Home
      </Link>
    </div>
  );
}

// Main App Component
function App() {
  return (
    <Router>
      <div className="app-container">
        <FixedBackButton />

        <div className="content-wrapper fade-in-up">
          <Routes>
            {/* Landing Page */}
            <Route path="/" element={<LandingPage />} />

            {/* Auth Page */}
            <Route path="/auth" element={<Auth />} />

            {/* Protected Quiz Page */}
            <Route
              path="/quiz"
              element={
                <ProtectedRoute>
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
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;