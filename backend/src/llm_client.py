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
            self.genai = importlib.import_module("google.generativeai")
            self.genai.configure(api_key=self.api_key)
            self.model = self.genai.GenerativeModel("gemini-1.5-pro") # Updated model
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

    def generate(self, prompt: str, output_json: bool = True) -> str:
        """Generate text using the configured model."""
        return self._generate_func(prompt, output_json)

    def _generate_gemini(self, prompt: str, output_json: bool = True) -> str:
        # Toggle response mime type based on the flag
        generation_config = self.genai.GenerationConfig(
            response_mime_type="application/json"
        ) if output_json else None
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text

    def _generate_openai(self, prompt: str, output_json: bool = True) -> str:
        # Toggle response_format based on the flag
        response_format = {"type": "json_object"} if output_json else {"type": "text"}
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini", # Using 4o-mini for speed and cost
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format # Apply the format
        )
        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str, output_json: bool = True) -> str:
        # output_json flag is accepted for signature consistency but ignored
        # as Anthropic's JSON mode is controlled via the prompt itself.
        response = self.client.messages.create(
            model="claude-3-5-sonnet-latest", # Using latest Sonnet
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text