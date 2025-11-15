# backend/src/quiz_engine.py

import json
from pathlib import Path

# --- Path Configuration ---
# We define the paths relative to this file's parent (backend/)
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"
QUIZ_PATH = DATA_DIR / "qq.json"
MANIFESTOS_PATH = DATA_DIR / "manifestos.json"

# --- Data Loading Functions ---

def load_quiz_questions():
    """Loads the quiz questions from qq.json"""
    try:
        with open(QUIZ_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Quiz file not found at {QUIZ_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode quiz file at {QUIZ_PATH}")
        return []

def load_manifestos():
    """Loads the analyzed manifestos from manifestos.json"""
    try:
        with open(MANIFESTOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Manifestos file not found at {MANIFESTOS_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode manifestos file at {MANIFESTOS_PATH}")
        return []

# --- Core Quiz Logic (from your ql.py) ---

def link_answers_to_tags(user_answers: list[int]) -> dict:
    """
    Maps a user's list of answers to their corresponding policy tags.
    e.g., [5, 4, 2] -> {"Economy": [5], "Education": [4, 2]}
    """
    quiz_questions = load_quiz_questions()
    tag_answer_map = {}

    # user_answers and quiz_questions should be parallel lists
    for q, ans in zip(quiz_questions, user_answers):
        tag = q.get('tag')
        if not tag:
            continue
            
        if tag not in tag_answer_map:
            tag_answer_map[tag] = []
        tag_answer_map[tag].append(ans)

    return tag_answer_map

# --- Core Alignment Logic (from your qe.ipynb) ---

def compute_alignment(user_answers: list[int]) -> dict:
    """
    Computes alignment for all manifestos and summarizes user preferences.
    """
    tag_answer_map = link_answers_to_tags(user_answers)
    manifestos = load_manifestos()
    
    if not manifestos:
        return {"error": "No manifestos loaded."}
    if not tag_answer_map:
        return {"error": "No valid answers or quiz questions."}

    alignment_results = []
    total_answer_count = sum(len(v) for v in tag_answer_map.values())

    for m in manifestos:
        # Get the policy_scores from our new LLM-generated structure
        manifesto_scores = m.get("analysis", {}).get("policy_scores", {})
        if not manifesto_scores:
            continue

        score_sum = 0
        for tag, answers in tag_answer_map.items():
            # Get the manifesto's score for this tag
            manifesto_score_data = manifesto_scores.get(tag, {})
            # Default to 3 (Neutral) if not found
            manifesto_score = manifesto_score_data.get("score", 3) 
            
            for ans in answers:
                # similarity = 1 - (normalized_distance)
                # Max distance is 4 (e.g., 1 vs 5)
                distance = abs(ans - manifesto_score)
                similarity = 1 - (distance / 4)
                score_sum += max(0, similarity)

        # Calculate final percentage
        if total_answer_count == 0:
            alignment_percentage = 0
        else:
            alignment_percentage = (score_sum / total_answer_count) * 100
            
        alignment_results.append({
            "manifesto_id": m["id"],
            "name": m.get("name", f"Manifesto {m['id']}"),
            "alignment": round(alignment_percentage, 1),
            "summary": m.get("analysis", {}).get("summary", "No summary available.")
        })

    # Sort descending by alignment
    alignment_results.sort(key=lambda x: x['alignment'], reverse=True)

    # --- Also calculate the user's preference summary ---
    avg_scores = {
        tag: round(sum(vals) / len(vals), 2) 
        for tag, vals in tag_answer_map.items() if vals
    }
    
    # Sort policies by the user's score, descending
    user_preferences = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)

    # Return a single dictionary with all results
    return {
        "alignment_results": alignment_results,
        "user_preferences": user_preferences
    }