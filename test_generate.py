import os
from dotenv import load_dotenv
load_dotenv()
from src.llm.llm_client import LLMClient

provider = os.getenv('LLM_PROVIDER', 'openai')
model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
print(f"Testing with provider={provider}, model={model}")

client = LLMClient(provider=provider, model=model)
print(f"Client base_url is {client._client.base_url if hasattr(client, '_client') else 'N/A'}")

try:
    response = client.generate("你好", temperature=0.7)
    print("Response:", response)
except Exception as e:
    print("Error:", e)
