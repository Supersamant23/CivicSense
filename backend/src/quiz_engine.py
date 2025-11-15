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
from src import LLMClient
# --- MODIFIED: Added pdf_extractor ---
from src import extract_text_from_pdf

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

# --- NEW: LLM Explanation Prompt Builder ---

def _build_explanation_prompt(tag: str, user_score: float, party_score: int, party_explanation: str, manifesto_full_text: str) -> str:
    """
    Builds a prompt for the LLM to explain an alignment or disagreement.
    """
    
    # Determine if it's an agreement or disagreement
    distance = abs(user_score - party_score)
    if distance < 1.5: # Arbitrary threshold for "alignment"
        alignment_type = "ALIGNMENT"
        intro = f"You and this party are closely aligned on {tag}."
    else:
        alignment_type = "DISAGREEMENT"
        intro = f"You and this party have a notable disagreement on {tag}."

    # Define score meanings
    score_meaning = """
    * 1 = Strong Left/Progressive (e.g., high government spending, strong regulation)
    * 3 = Neutral / Centrist
    * 5 = Strong Right/Conservative (e.g., tax cuts, free market)
    """

    return f"""
    You are a helpful, non-partisan political analyst. Your task is to write a brief, 2-3 sentence explanation for a user about their policy alignment with a political party.

    **Context:**
    1.  **Policy Topic:** {tag}
    2.  **User's Average Score:** {user_score:.1f} (on a 1-5 scale)
    3.  **Party's Score:** {party_score} (on a 1-5 scale)
    4.  **Score Meaning:** {score_meaning}
    5.  **Party's Stated Position (Summary):** "{party_explanation}"
    
    **This is a {alignment_type}.**

    **Your Task:**
    Write a 2-3 sentence explanation for the user. Be direct and use "You" and "The party".
    1.  Start by stating the alignment/disagreement clearly (e.g., "{intro}").
    2.  Briefly explain *why* based on the scores. (e.g., "You lean towards [X], while the party advocates for [Y].")
    3.  **Crucially, find one specific policy point or quote from the 'Full Manifesto Text' below that backs this up.** (e.g., "For example, the manifesto states, '...'")
    4.  Keep it simple, clear, and focused *only* on this single policy topic. Do not add any conversational greeting or sign-off.

    **Full Manifesto Text (for finding quotes):**
    ---
    {manifesto_full_text}
    ---
    
    Begin your explanation now.
    """

# --- Core Alignment Logic (MODIFIED) ---

def compute_alignment(user_answers: list[int], llm_client: LLMClient = None) -> dict:
    """
    Computes alignment for all manifestos, summarizes user preferences,
    and highlights top matching policies for the best match.
    
    Args:
        user_answers: List of integer answers from the quiz.
        llm_client: (MODIFIED) An initialized LLMClient instance.
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
            
        # --- NEW: Load full manifesto text if llm_client is available ---
        manifesto_full_text = None
        if llm_client:
            try:
                # The 'name' in manifestos.json matches the PDF filename stem
                pdf_name = m.get("name")
                if pdf_name:
                    pdf_path = PDF_INPUTS_DIR / f"{pdf_name}.pdf"
                    if pdf_path.exists():
                        manifesto_full_text = extract_text_from_pdf(pdf_path)
                        print(f"Loaded full text for {pdf_name} for LLM explanation.")
                    else:
                        print(f"Warning: PDF file not found at {pdf_path}")
            except Exception as e:
                print(f"Error loading PDF text for {m.get('name')}: {e}")
                manifesto_full_text = None # Ensure it's None on failure
        # -----------------------------------------------------------------

        score_sum = 0
        policy_similarities = []

        for tag, answers in tag_answer_map.items():
            manifesto_score_data = manifesto_scores.get(tag, {})
            manifesto_score = manifesto_score_data.get("score", 3) 
            
            tag_similarity_sum = 0
            tag_answer_count = 0
            
            for ans in answers:
                distance = abs(ans - manifesto_score)
                similarity = 1 - (distance / 4)
                
                current_similarity = max(0, similarity)
                score_sum += current_similarity
                tag_similarity_sum += current_similarity
                tag_answer_count += 1
            
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
            
        # Sort for TOP matches (descending similarity)
        top_matches = sorted(policy_similarities, key=lambda x: x['similarity_score'], reverse=True)
        
        # Sort for WORST matches (ascending similarity)
        top_disagreements = sorted(policy_similarities, key=lambda x: x['similarity_score'])

        # --- NEW: Generate LLM explanations if possible ---
        if llm_client and manifesto_full_text:
            print(f"Generating LLM explanations for {m.get('name')}...")
            # Generate for top 3 matches
            for policy in top_matches[:3]:
                try:
                    prompt = _build_explanation_prompt(
                        policy['tag'], 
                        policy['user_score'], 
                        policy['party_score'], 
                        policy['explanation'], 
                        manifesto_full_text
                    )
                    # Use output_json=False for plain text
                    new_explanation = llm_client.generate(prompt, output_json=False)
                    policy['explanation'] = new_explanation
                except Exception as e:
                    print(f"LLM explanation failed for {policy['tag']}: {e}")
                    # Fallback to the original short explanation is already in place
            
            # Generate for top 3 disagreements
            for policy in top_disagreements[:3]:
                try:
                    prompt = _build_explanation_prompt(
                        policy['tag'], 
                        policy['user_score'], 
                        policy['party_score'], 
                        policy['explanation'], 
                        manifesto_full_text
                    )
                    # Use output_json=False for plain text
                    new_explanation = llm_client.generate(prompt, output_json=False)
                    policy['explanation'] = new_explanation
                except Exception as e:
                    print(f"LLM explanation failed for {policy['tag']}: {e}")
                    # Fallback to the original short explanation is already in place
        # ----------------------------------------------------

        alignment_results.append({
            "manifesto_id": m["id"],
            "name": m.get("name", f"Manifesto {m['id']}"),
            "alignment": round(alignment_percentage, 1),
            "summary": m.get("analysis", {}).get("summary", "No summary available."),
            "top_matching_policies": top_matches[:3], 
            "top_disagreements": top_disagreements[:3] 
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