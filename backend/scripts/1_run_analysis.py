# backend/scripts/1_run_analysis.py

import os
import json
from pathlib import Path
import sys

# --- Add backend directory to path ---
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))
# ------------------------------------

# --- Load .env file ---
from dotenv import load_dotenv
load_dotenv(dotenv_path=backend_dir / ".env")
# ------------------------

# Now we can import from our 'src' package
from src import (
    extract_text_from_pdf,
    LLMClient,
    build_analysis_prompt,
    parse_llm_output
)

# --- Configuration ---
INPUTS_DIR = backend_dir / "inputs"
DATA_DIR = backend_dir / "data"
OUTPUT_NAME = "manifestos.json" # The name of our final data file

# Ensure the data directory exists
DATA_DIR.mkdir(exist_ok=True)
output_path = DATA_DIR / OUTPUT_NAME

# --- LLM Provider Configuration ---
# Change this to "google", "openai", or "anthropic"
PROVIDER = "google"
API_KEY_NAME = "GOOGLE_API_KEY" # Must match PROVIDER
# ------------------------------------


def run_analysis_for_all_pdfs():
    """
    Main function to find all PDFs, analyze them, and save as one JSON.
    """
    print("--- Starting Manifesto Analysis Pipeline ---")
    
    # === Step 1: Get API Key ===
    api_key = os.getenv(API_KEY_NAME) 
    if not api_key:
        raise EnvironmentError(
            f"Please set your API key in the .env file (e.g., {API_KEY_NAME})"
        )
    
    # === Step 2: Initialize LLM client ===
    try:
        llm = LLMClient(provider=PROVIDER, api_key=api_key)
        print(f"LLM client initialized (provider: {PROVIDER}).")
    except Exception as e:
        print(f"Error initializing LLM client: {e}")
        return

    # === Step 3: Find all PDFs in the inputs directory ===
    pdf_files = list(INPUTS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"Error: No PDF files found in {INPUTS_DIR}")
        return
        
    print(f"Found {len(pdf_files)} PDF(s) to analyze.")

    # This list will hold all our final manifesto data
    all_manifesto_data = []
    manifesto_id_counter = 1

    # === Step 4: Loop through each PDF and analyze it ===
    for pdf_path in pdf_files:
        print(f"\n--- Analyzing: {pdf_path.name} ---")
        
        # 4a. Extract text
        try:
            manifesto_text = extract_text_from_pdf(pdf_path)
            print(f"Successfully extracted text from {pdf_path.name}.")
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            continue # Skip to the next file

        # 4b. Build Prompt and Call LLM
        print("Building analysis prompt...")
        prompt = build_analysis_prompt(manifesto_text)
        
        print("Calling the LLM. This may take a few moments...")
        try:
            llm_output = llm.generate(prompt)
            print("LLM response received.")
        except Exception as e:
            print(f"Error during LLM generation: {e}")
            continue # Skip to the next file

        # 4c. Parse Output
        try:
            analysis_data = parse_llm_output(llm_output)
            print("LLM output parsed successfully.")
            
            # 4d. Create a clean name from the filename
            # e.g., "cong_manifesto_2024.pdf" -> "Cong Manifesto 2024"
            clean_name = pdf_path.stem.replace("_", " ").replace("-", " ").title()
            
            # 4e. Add to our master list
            all_manifesto_data.append({
                "id": manifesto_id_counter,
                "name": clean_name,
                "analysis": analysis_data
            })
            
            manifesto_id_counter += 1
            
        except Exception as e:
            print(f"Error parsing or saving JSON: {e}")
            print(f"--- Raw LLM Output ---\n{llm_output}\n---------------------")
            continue # Skip to the next file

    # === Step 5: Save all data to a single file ===
    if not all_manifesto_data:
        print("No manifestos were successfully analyzed. Exiting.")
        return
        
    print(f"\n--- Analysis Complete! ---")
    print(f"Successfully analyzed {len(all_manifesto_data)} manifestos.")
    
    try:
        print(f"Saving all analyses to: {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_manifesto_data, f, ensure_ascii=False, indent=4)
        print("Data saved successfully.")
    except Exception as e:
        print(f"Fatal error saving final JSON: {e}")


if __name__ == "__main__":
    run_analysis_for_all_pdfs()