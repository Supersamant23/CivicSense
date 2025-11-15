import React, { useEffect } from "react"; // <-- Import useEffect
import { Link } from "react-router-dom";
import "./landing.css";

export default function LandingPage() {
  // --- Add this useEffect hook ---
  useEffect(() => {
    // When this page loads, apply styles to the body
    document.body.style.background = "#050510";
    document.body.style.margin = "0";
    document.body.style.padding = "0";
    document.body.style.color = "#ffffff";
    document.body.style.fontFamily =
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

    // When this page is left (unmounted), reset the styles
    return () => {
      document.body.style.background = "";
      document.body.style.margin = "";
      document.body.style.padding = "";
      document.body.style.color = "";
      document.body.style.fontFamily = "";
    };
  }, []); // <-- Empty array means this runs only once on mount and unmount
  // --- End of hook ---

  return (
    <div className="landing-container">
      <div className="landing-box">
        <h1 className="landing-title">Civic Sense</h1>
        <p className="landing-subtitle">
          Understand where you stand — discover your civic alignment.
        </p>

        <Link to="/quiz" className="primary-btn">
          Take the Quiz
        </Link>
      </div>
    </div>
  );
}