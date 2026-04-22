"""LLM client abstraction supporting OpenAI, Anthropic, and OLLAMA providers"""
import os
from typing import Optional


class LLMClient:
    """Client for interacting with LLM APIs (OpenAI/Anthropic/OLLAMA)"""
    
    def __init__(self, provider: str = 'openai', model: str = 'gpt-4o-mini', api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            provider: 'openai', 'anthropic', 'ollama', or 'omlx'
            model: Model name (e.g., 'gpt-4o-mini', 'claude-3-sonnet-20240229', 'qwen2.5:latest')
            api_key: API key (defaults to environment variable, not required for local models)
            base_url: Base URL for API (for omlx: http://127.0.0.1:8000)
        """
        self.provider = provider.lower()
        self.model = model
        self.base_url = base_url
        
        # Get API key from parameter or environment
        if api_key:
            self.api_key = api_key
        elif self.provider == 'openai':
            self.api_key = os.environ.get('OPENAI_API_KEY', '')
        elif self.provider == 'anthropic':
            self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        elif self.provider in ['ollama', 'omlx']:
            # Some local models (like oMLX) require an API key
            if not getattr(self, 'api_key', None):
                self.api_key = os.environ.get('LLM_API_KEY', os.environ.get('OLLAMA_API_KEY', os.environ.get('OPENAI_API_KEY', 'local')))
            # Default base URL for local models
            if not self.base_url:
                self.base_url = os.environ.get('LLM_BASE_URL', os.environ.get('OLLAMA_BASE_URL', 'http://127.0.0.1:8000'))
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Initialize provider client
        self._client = None
        if self.provider == 'openai':
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)
        elif self.provider == 'anthropic':
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        elif self.provider in ['ollama', 'omlx']:
            import openai
            # Use OpenAI client with custom base URL for local compatibility
            self._client = openai.OpenAI(
                base_url=f"{self.base_url}/v1",
                api_key=self.api_key
            )
    
    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate text response from LLM
        
        Args:
            prompt: Input prompt text
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            Generated text response
        """
        try:
            if self.provider in ['openai', 'ollama', 'omlx']:
                # Both OpenAI and local models use the same API format
                print(f"DEBUG: LLMClient generate() called with provider={self.provider}, model={self.model}, base_url={self._client.base_url}")
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                return response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self._client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=temperature,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            
            else:
                return f"Error: Unsupported provider '{self.provider}'"
        
        except Exception as e:
            # Handle API errors gracefully - return user-friendly error message
            error_msg = str(e)
            if 'rate limit' in error_msg.lower():
                return "Error: API rate limit exceeded. Please try again later."
            elif 'authentication' in error_msg.lower() or 'api key' in error_msg.lower():
                return "Error: Authentication failed. Please check your API key."
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                return "Error: Network connection failed. Please check your internet connection."
            else:
                return f"Error: Failed to generate response - {error_msg}"
