# backend/src/manifesto_analyzer.py

import json
import re

# These are the 10 policy tags from your original quiz generator.
# We MUST get a score and explanation for *every single one* from the LLM.
POLICY_TAGS = [
    "Economy", "Education", "Technology", "Environment", "Healthcare",
    "Defense", "Infrastructure", "Foreign Policy", "Social Justice", "Agriculture"
]

def build_analysis_prompt(manifesto_text: str) -> str:
    """
    Constructs the core analysis prompt for the LLM.
    This prompt instructs the LLM to perform all logic at once:
    1. Read the full text.
    2. For EACH of the 10 policy tags:
    3. Assign a 1-5 stance score.
    4. Write a simple, one-sentence summary of that stance.
    """
    
    # We will format the 10 tags for the prompt
    policy_list = "\n".join([f"- {tag}" for tag in POLICY_TAGS])
    
    # The JSON schema we want the LLM to fill
    # Note: We provide a full example so the LLM knows what to do for all 10 tags.
    json_schema = """
{
  "summary": "A 2-3 sentence, simple-language overview of the manifesto's main focus and tone.",
  "policy_scores": {
    "Economy": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Economy>"
    },
    "Education": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Education>"
    },
    "Technology": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Technology>"
    },
    "Environment": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Environment>"
    },
    "Healthcare": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Healthcare>"
    },
    "Defense": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Defense>"
    },
    "Infrastructure": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Infrastructure>"
    },
    "Foreign Policy": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Foreign Policy>"
    },
    "Social Justice": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Social Justice>"
    },
    "Agriculture": {
      "score": <1-5>,
      "explanation": "<Simple 1-sentence explanation of the stance on Agriculture>"
    }
  }
}
"""

    return f"""
You are a precise, non-partisan political analyst. Your task is to analyze the provided political manifesto and output a structured JSON.

**Instructions:**
1.  Read the entire manifesto text provided.
2.  For **each** of the 10 policy areas listed below, you MUST determine the party's stance and assign a score from 1 to 5.
3.  The score represents a political leaning:
    * **1 = Strong Left/Progressive:** (e.g., high government spending, strong regulation, social programs)
    * **2 = Moderate Left/Progressive**
    * **3 = Neutral / Centrist:** (e.g., mixed policies, no strong stance, or not mentioned)
    * **4 = Moderate Right/Conservative**
    * **5 = Strong Right/Conservative:** (e.g., tax cuts, free market, privatization)
4.  If a policy is **not mentioned** or the stance is unclear, assign a score of **3 (Neutral)** and set the explanation to "This policy was not clearly mentioned."
5.  For **each** policy, you MUST also provide a simple, one-sentence "explanation" of that stance, written in plain language a layman can understand.
6.  You MUST provide a 2-3 sentence "summary" of the manifesto's overall goals.

**Policy Areas to Score:**
{policy_list}

**Output Format:**
You must output *only* the JSON object in the exact schema below. Do not include "```json", "```", or any other text.

**Schema:**
{json_schema}

**Manifesto Text:**
---
{manifesto_text}
---
"""

def parse_llm_output(output_text: str) -> dict:
    """
    Cleans and parses the LLM's string output into a Python dictionary.
    """
    # The LLM might still add "```json" or "```"
    # We use regex to find the first '{' and the last '}'
    match = re.search(r'\{.*\}', output_text, re.DOTALL)
    
    if not match:
        print("LLM output did not contain a valid JSON object.")
        print(f"--- Raw LLam Output ---\n{output_text}\n-------------------")
        raise ValueError("No JSON object found in LLM output.")
        
    json_string = match.group(0)
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error. LLM output was:\n{json_string}")
        raise e