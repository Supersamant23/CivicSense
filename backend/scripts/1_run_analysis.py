# backend/scripts/1_run_analysis.py

import os
import json
from pathlib import Path

# --- IMPORTANT: We need to tell Python where our 'src' module is ---
# This adds the 'backend' directory to the Python path
import sys
from dotenv import load_dotenv

# Go up one level (to 'backend') and add it to the path
backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=backend_dir / ".env")
sys.path.append(str(backend_dir))
# -----------------------------------------------------------------

# Now we can import from our 'src' package
from src import (
    extract_text_from_pdf,
    LLMClient,
    build_analysis_prompt,
    parse_llm_output
)

# --- Configuration ---
# Use Pathlib for robust file paths
INPUTS_DIR = backend_dir / "inputs"
DATA_DIR = backend_dir / "data"
PDF_NAME = "cong.pdf"  # The name of your input PDF
OUTPUT_NAME = "manifestos.json" # The name of our final data file

# Ensure the data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Define file paths
pdf_path = INPUTS_DIR / PDF_NAME
output_path = DATA_DIR / OUTPUT_NAME

def run_analysis():
    """
    The main function to run the analysis pipeline.
    """
    print(f"Starting analysis for: {pdf_path}")
    
    # === Step 1: Get API Key ===
    # We'll use OpenAI for this example. Change "OPENAI_API_KEY"
    # to "GOOGLE_API_KEY" or "ANTHROPIC_API_KEY" as needed.
    api_key = os.getenv("OPENAI_API_KEY") 
    if not api_key:
        raise EnvironmentError(
            "Please set your API key in the .env file (e.g., OPENAI_API_KEY)"
        )
    
    # === Step 2: Extract text from PDF ===
    try:
        manifesto_text = extract_text_from_pdf(pdf_path)
        print(f"Successfully extracted text from {PDF_NAME}.")
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
        print("Please make sure 'cong.pdf' is in the 'backend/inputs/' directory.")
        return
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return

    # === Step 3: Initialize LLM client ===
    # Change 'openai' to 'google' or 'anthropic' if you prefer
    try:
        # NOTE: Make sure your .env variable matches the provider
        llm = LLMClient(provider="openai", api_key=api_key)
        print("LLM client initialized (provider: OpenAI).")
    except ImportError as e:
        print(f"Error: Missing library for LLM provider. {e}")
        print("Please install the required library (e.g., 'pip install openai')")
        return
    except Exception as e:
        print(f"Error initializing LLM client: {e}")
        return

    # === Step 4: Build Prompt and Call LLM ===
    print("Building analysis prompt...")
    prompt = build_analysis_prompt(manifesto_text)
    
    print("Calling the LLM. This may take a few moments...")
    try:
        llm_output = llm.generate(prompt)
        print("LLM response received.")
    except Exception as e:
        print(f"Error during LLM generation: {e}")
        return

    # === Step 5: Parse and Save Output ===
    try:
        print("Parsing LLM output...")
        analysis_data = parse_llm_output(llm_output)
        
        # --- This is the key part ---
        # We are creating a list of manifestos.
        # This structure matches your *original* quiz engine's expectation.
        final_data = [
            {
                "id": 1,  # We'll just start with 1
                "name": "Congress Manifesto 2024 (Example)", # Add a name
                "analysis": analysis_data # This contains summary + policy_scores
            }
        ]
        # (If you add more PDFs, you'll append them to this list)

        print(f"Saving analysis to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
            
        print("\n--- Analysis Complete! ---")
        print(f"Data saved to {output_path}")

    except Exception as e:
        print(f"Error parsing or saving JSON: {e}")
        print(f"--- Raw LLM Output ---\n{llm_output}\n---------------------")


if __name__ == "__main__":
    # This allows us to run the script directly from the terminal
    run_analysis()