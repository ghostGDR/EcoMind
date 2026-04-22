import os
from dotenv import load_dotenv
load_dotenv()
from src.llm.llm_client import LLMClient

provider = os.getenv('LLM_PROVIDER', 'openai')
model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
client = LLMClient(provider=provider, model=model)

print(f"Provider: {client.provider}")
print(f"Model: {client.model}")
print(f"Base URL: {client.base_url}")
print(f"Client Base URL: {client._client.base_url if hasattr(client, '_client') and hasattr(client._client, 'base_url') else 'N/A'}")
