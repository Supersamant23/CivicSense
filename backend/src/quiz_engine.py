# backend/src/quiz_engine.py

import json
from pathlib import Path
import sys
import os

# --- Add backend directory to path ---
# This ensures we can import from 'src'
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))
# ------------------------------------

# --- Load .env file ---
# This is needed to potentially load LLM clients for future enhancements
from dotenv import load_dotenv
load_dotenv(dotenv_path=backend_dir / ".env")
# ------------------------

# Import our analysis and LLM tools
from src import LLMClient # We import this for potential future use

# --- Path Configuration ---
DATA_DIR = backend_dir / "data"
QUIZ_PATH = DATA_DIR / "qq.json"
MANIFESTOS_PATH = DATA_DIR / "manifestos.json"
PDF_INPUTS_DIR = backend_dir / "inputs"

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

# --- Core Alignment Logic (MODIFIED) ---

def compute_alignment(user_answers: list[int], llm_client: LLMClient = None) -> dict:
    """
    Computes alignment for all manifestos, summarizes user preferences,
    and highlights top matching policies for the best match.
    
    Args:
        user_answers: List of integer answers from the quiz.
        llm_client: (Ignored in this reverted version) An initialized LLMClient instance.
    """
    tag_answer_map = link_answers_to_tags(user_answers)
    manifestos = load_manifestos()
    
    if not manifestos:
        return {"error": "No manifestos loaded."}
    if not tag_answer_map:
        return {"error": "No valid answers or quiz questions."}

    # --- First, calculate the user's average preference for each tag ---
    avg_user_scores = {
        tag: round(sum(vals) / len(vals), 2) 
        for tag, vals in tag_answer_map.items() if vals
    }

    alignment_results = []
    total_answer_count = sum(len(v) for v in tag_answer_map.values())

    for m in manifestos:
        manifesto_scores = m.get("analysis", {}).get("policy_scores", {})
        if not manifesto_scores:
            continue

        score_sum = 0
        
        # This list will store the similarity details for each policy tag
        policy_similarities = []

        for tag, answers in tag_answer_map.items():
            manifesto_score_data = manifesto_scores.get(tag, {})
            manifesto_score = manifesto_score_data.get("score", 3) 
            
            tag_similarity_sum = 0
            tag_answer_count = 0
            
            for ans in answers:
                # similarity = 1 - (normalized_distance)
                # Max distance is 4 (e.g., 1 vs 5)
                distance = abs(ans - manifesto_score)
                similarity = 1 - (distance / 4)
                
                current_similarity = max(0, similarity)
                score_sum += current_similarity
                tag_similarity_sum += current_similarity
                tag_answer_count += 1
            
            # Calculate average similarity for this specific tag
            if tag_answer_count > 0:
                avg_tag_similarity = (tag_similarity_sum / tag_answer_count) * 100
                policy_similarities.append({
                    "tag": tag,
                    "similarity_score": round(avg_tag_similarity, 1),
                    "explanation": manifesto_score_data.get("explanation", "This policy was not clearly mentioned."),
                    "party_score": manifesto_score,
                    "user_score": avg_user_scores.get(tag)
                })

        # Calculate final percentage
        if total_answer_count == 0:
            alignment_percentage = 0
        else:
            alignment_percentage = (score_sum / total_answer_count) * 100
            
        # Sort this party's policies by similarity
        policy_similarities.sort(key=lambda x: x['similarity_score'], reverse=True)

        alignment_results.append({
            "manifesto_id": m["id"],
            "name": m.get("name", f"Manifesto {m['id']}"),
            "alignment": round(alignment_percentage, 1),
            "summary": m.get("analysis", {}).get("summary", "No summary available."),
            
            # --- This key provides the "highlight" you asked for ---
            "top_matching_policies": policy_similarities[:3] 
        })

    # Sort final results descending by alignment
    alignment_results.sort(key=lambda x: x['alignment'], reverse=True)

    # Sort user's preferences by their score, descending
    user_preferences = sorted(avg_user_scores.items(), key=lambda x: x[1], reverse=True)

    # Return a single dictionary with all results
    return {
        "alignment_results": alignment_results,
        "user_preferences": user_preferences
    }