# backend/src/quiz_engine.py

import json
from pathlib import Path

# --- Path Configuration ---
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

# --- Core Quiz Logic ---

def link_answers_to_tags(user_answers: list[int]) -> dict:
    """
    Maps a user's list of answers to their corresponding policy tags.
    e.g., [5, 4, 2] -> {"Economy": [5], "Education": [4], "Technology": [2]}
    """
    quiz_questions = load_quiz_questions()
    tag_answer_map = {}

    for q, ans in zip(quiz_questions, user_answers):
        tag = q.get('tag')
        if not tag:
            continue
            
        if tag not in tag_answer_map:
            tag_answer_map[tag] = []
        tag_answer_map[tag].append(ans)

    return tag_answer_map

def calculate_policy_alignment(user_score: float, manifesto_score: int) -> float:
    """Calculate alignment percentage between user and manifesto for a single policy"""
    distance = abs(user_score - manifesto_score)
    similarity = 1 - (distance / 4)  # Max distance is 4 (1 vs 5)
    return max(0, similarity * 100)

def compute_alignment(user_answers: list[int]) -> dict:
    """
    Computes alignment for all manifestos with detailed policy breakdowns.
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
        manifesto_scores = m.get("analysis", {}).get("policy_scores", {})
        if not manifesto_scores:
            continue

        score_sum = 0
        policy_details = {}

        for tag, answers in tag_answer_map.items():
            manifesto_score_data = manifesto_scores.get(tag, {})
            manifesto_score = manifesto_score_data.get("score", 3)
            explanation = manifesto_score_data.get("explanation", "No explanation available.")
            
            # Calculate user's average score for this policy
            user_avg_score = sum(answers) / len(answers) if answers else 3
            
            # Calculate alignment for this specific policy
            policy_alignment = calculate_policy_alignment(user_avg_score, manifesto_score)
            
            # Store detailed policy information
            policy_details[tag] = {
                "your_position": round(user_avg_score, 1),
                "manifesto_position": manifesto_score,
                "alignment": round(policy_alignment, 1),
                "explanation": explanation
            }
            
            # Calculate overall similarity score
            for ans in answers:
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
            "summary": m.get("analysis", {}).get("summary", "No summary available."),
            "policy_details": policy_details
        })

    # Sort descending by alignment
    alignment_results.sort(key=lambda x: x['alignment'], reverse=True)

    # Calculate user's preference summary
    avg_scores = {
        tag: round(sum(vals) / len(vals), 2) 
        for tag, vals in tag_answer_map.items() if vals
    }
    
    user_preferences = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)

    return {
        "alignment_results": alignment_results,
        "user_preferences": user_preferences
    }