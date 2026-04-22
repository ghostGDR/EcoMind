import sys
from src.storage.vector_store import HenryVectorStore
from llama_index.core import Settings

vector_store = HenryVectorStore()

query = "TikTok 广告投放的最佳时间是什么？"
query_embedding = Settings.embed_model.get_query_embedding(query)

search_result = vector_store.client.query_points(
    collection_name="henry_knowledge_base",
    query=query_embedding,
    limit=5,
    with_payload=True,
    with_vectors=False
)

for point in search_result.points:
    print(f"Score: {point.score:.4f}, Text: {point.payload.get('text', '')[:100]}")
