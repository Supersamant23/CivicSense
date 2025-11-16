// frontend/src/LandingPage.jsx
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { supabase } from './supabaseClient';
import "./landing.css";

export default function LandingPage() {
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Apply body styles
    document.body.style.background = "#050510";
    document.body.style.margin = "0";
    document.body.style.padding = "0";
    document.body.style.color = "#ffffff";
    document.body.style.fontFamily =
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

    // Get session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    // Auto logout when browser/tab closes
    const handleBeforeUnload = async () => {
      if (session) {
        await supabase.auth.signOut();
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup
    return () => {
      subscription.unsubscribe();
      window.removeEventListener('beforeunload', handleBeforeUnload);
      document.body.style.background = "";
      document.body.style.margin = "";
      document.body.style.padding = "";
      document.body.style.color = "";
      document.body.style.fontFamily = "";
    };
  }, [session]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  return (
    <div className="landing-container">
      <div className="landing-box">
        <h1 className="landing-title">Civic Sense</h1>
        <p className="landing-subtitle">
          Understand where you stand — discover your civic alignment.
        </p>

        {session ? (
          <div className="landing-buttons">
            <Link to="/quiz" className="primary-btn">
              Take the Quiz
            </Link>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
            <p className="user-email">
              Logged in as: {session.user.email}
            </p>
          </div>
        ) : (
          <div className="landing-buttons">
            <Link to="/auth" className="primary-btn">
              Get Started
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}