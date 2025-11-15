# backend/scripts/2_generate_quiz.py

import json
import random
from pathlib import Path
import sys

# --- Add backend directory to path ---
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))
# ------------------------------------

# Import our policy tags from the src package
from src import POLICY_TAGS 

# --- Paths ---
DATA_DIR = backend_dir / "data"
QUIZ_OUTPUT_PATH = DATA_DIR / "qq.json"

# --- Predefined question templates per policy tag ---
# (This is from your qqgen.ipynb)
question_templates = {
    "Economy": [
        "Do you support government initiatives to boost economic growth?",
        "Should taxes be reduced to encourage private sector development?",
        "Do you agree with increased spending on job creation programs?"
    ],
    "Education": [
        "Should education be more practical and skill-oriented?",
        "Do you support free higher education for all students?",
        "Should government increase funding for schools and universities?"
    ],
    "Technology": [
        "Should artificial intelligence and automation be regulated to prevent misuse?",
        "Do you support investment in digital infrastructure?",
        "Should government promote research and innovation in technology?"
    ],
    "Environment": [
        "Do you support increased funding for renewable energy?",
        "Should stricter policies be enforced to reduce pollution?",
        "Do you agree with conservation programs for forests and wildlife?"
    ],
    "Healthcare": [
        "Should healthcare be completely free and government-funded?",
        "Do you support government initiatives for mental health?",
        "Should public hospitals receive increased funding?"
    ],
    "Defense": [
        "Do you support increased government spending on national defense?",
        "Should military modernization programs be prioritized?",
        "Do you agree with the current defense policy approach?"
    ],
    "Infrastructure": [
        "Should the government invest more in public transport and smart cities?",
        "Do you support development of roads, bridges, and housing?",
        "Should infrastructure projects prioritize sustainability?"
    ],
    "Foreign Policy": [
        "Do you support strengthening diplomatic relations internationally?",
        "Should government prioritize trade agreements with other countries?",
        "Do you agree with the current foreign policy strategy?"
    ],
    "Social Justice": [
        "Should laws be strengthened to ensure equality and social justice?",
        "Do you support policies promoting gender equality?",
        "Should the government take action against discrimination?"
    ],
    "Agriculture": [
        "Should farmers receive a guaranteed minimum price for crops?",
        "Do you support government subsidies for agriculture?",
        "Should irrigation and soil improvement programs be prioritized?"
    ],
    "General": [ # Fallback, just in case
        "Do you agree with the overall direction of government policies?",
        "Should citizens be more involved in policy-making?"
    ]
}

def generate_quiz():
    """
    Generates a quiz from the POLICY_TAGS and templates.
    """
    print("Generating quiz questions...")
    
    generated_questions = []
    question_id = 1

    # We use the master list of POLICY_TAGS
    for tag in POLICY_TAGS:
        templates = question_templates.get(tag, question_templates["General"])
        
        # Pick one random question for this tag
        if not templates:
            continue
        
        question_text = random.choice(templates)
        
        generated_questions.append({
            "id": question_id,
            "question": question_text,
            "tag": tag,
            "options": {
                1: "Strongly Disagree",
                2: "Disagree",
                3: "Neutral",
                4: "Agree",
                5: "Strongly Agree"
            }
        })
        question_id += 1

    # --- Save Quiz Questions ---
    try:
        with open(QUIZ_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(generated_questions, f, ensure_ascii=False, indent=4)
        
        print(f"\n--- Quiz Generation Complete! ---")
        print(f"Generated {len(generated_questions)} quiz questions.")
        print(f"Data saved to {QUIZ_OUTPUT_PATH}")

    except Exception as e:
        print(f"Error saving quiz file: {e}")

if __name__ == "__main__":
    generate_quiz()