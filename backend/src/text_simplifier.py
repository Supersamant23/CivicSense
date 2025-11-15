# backend/src/text_simplifier.py

def build_simplify_prompt(text: str) -> str:
    """Constructs the simplification prompt for the LLM."""
    return f"""
You are a specialized Jargon Removal and Simplification Engine. Your task is to receive complex political, legal, or policy text and rewrite it to be easily understandable by a general audience (a layman).

The simplified text must be presented as the content of a single, self-contained TEXT file block with the title "Simplified Policy Text". Absolutely no commentary or explanation should be included outside this file block.

For every sentence or core idea, replace all political jargon, complex technical terms, and bureaucratic phrasing with simple, direct, everyday language. The simplified text must accurately convey the original meaning and intent without losing any critical details.

Text to simplify: {text}
"""