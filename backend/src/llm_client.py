# backend/src/llm_client.py

import importlib

class LLMClient:
    def __init__(self, provider: str, api_key: str):
        """
        Initialize a general-purpose LLM client.
        provider: 'google', 'openai', or 'anthropic'
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = None
        self._setup_provider()

    def _setup_provider(self):
        if self.provider == "google":
            genai = importlib.import_module("google.generativeai")
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-pro-latest") # Note: You may want to update this model name
            self._generate_func = self._generate_gemini

        elif self.provider == "openai":
            # We need the 'openai' library
            openai = importlib.import_module("openai")
            # Create a client instance
            self.client = openai.OpenAI(api_key=self.api_key)
            self._generate_func = self._generate_openai

        elif self.provider == "anthropic":
            # We need the 'anthropic' library
            anthropic = importlib.import_module("anthropic")
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self._generate_func = self._generate_anthropic

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def generate(self, prompt: str) -> str:
        """Generate text using the configured model."""
        return self._generate_func(prompt)

    def _generate_gemini(self, prompt: str) -> str:
        return self.model.generate_content(prompt).text

    def _generate_openai(self, prompt: str) -> str:
        # Note: Updated to use the new OpenAI client (v1.0+)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini", # Using 4o-mini for speed and cost
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-3-5-sonnet-latest", # Using latest Sonnet
            max_tokens=4096, # Increased max_tokens
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text