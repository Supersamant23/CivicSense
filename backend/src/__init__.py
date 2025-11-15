# backend/src/__init__.py

# This file can be left empty.
# Its presence alone tells Python that 'src' is a package.

# --- Optional ---
# For convenience, we can make our main functions and classes
# available for easier import. This is a common practice.

from .llm_client import LLMClient
from .pdf_extractor import extract_text_from_pdf
from .manifesto_analyzer import (
    build_analysis_prompt, 
    parse_llm_output, 
    POLICY_TAGS
)
from .text_simplifier import build_simplify_prompt
from .quiz_engine import (
    load_quiz_questions,
    load_manifestos,
    compute_alignment
)

print("Package 'src' initialized.")