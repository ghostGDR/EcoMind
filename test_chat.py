import asyncio
from src.rag.conversation_manager import ConversationManager
from src.rag.query_engine import QueryEngine

qe = QueryEngine()
cm = ConversationManager(query_engine=qe)

response = cm.send_message(32, "你好")
print("Response:", response["answer"])
