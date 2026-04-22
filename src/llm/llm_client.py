"""LLM client abstraction supporting OpenAI and Anthropic providers"""
import os
from typing import Optional


class LLMClient:
    """Client for interacting with LLM APIs (OpenAI/Anthropic)"""
    
    def __init__(self, provider: str = 'openai', model: str = 'gpt-4o-mini', api_key: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            provider: 'openai' or 'anthropic'
            model: Model name (e.g., 'gpt-4o-mini', 'claude-3-sonnet-20240229')
            api_key: API key (defaults to environment variable)
        """
        self.provider = provider.lower()
        self.model = model
        
        # Get API key from parameter or environment
        if api_key:
            self.api_key = api_key
        elif self.provider == 'openai':
            self.api_key = os.environ.get('OPENAI_API_KEY', '')
        elif self.provider == 'anthropic':
            self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
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
            if self.provider == 'openai':
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
