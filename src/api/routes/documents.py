"""Document management REST API endpoints"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.dependencies import get_search_engine, get_document_store
from src.api.models import (
    DocumentResponse,
    DocumentListResponse,
    TopicDocumentsResponse,
    SearchResultItem,
    SearchResponse
)
from src.search.search_engine import SearchEngine
from src.storage.document_store import DocumentStore
import logging

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/documents",
    tags=["documents"]
)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    search_engine: SearchEngine = Depends(get_search_engine),
    document_store: DocumentStore = Depends(get_document_store)
):
    """
    List all documents with metadata
    
    Returns documents ordered by modified_at DESC (newest first)
    """
    try:
        # Get all documents from search engine
        all_docs = search_engine.list_all_documents()
        
        # Get total count from document store
        counts = document_store.get_document_count()
        
        # Transform to response format
        documents = []
        for doc in all_docs:
            documents.append(DocumentResponse(
                filename=doc['title'],
                file_path=doc['relative_path'],
                topic=doc['topic'],
                modified_at=doc['modified_date'],
                size_kb=round(doc['size_bytes'] / 1024, 2)
            ))
        
        # Sort by modified_at DESC (newest first)
        # Parse date strings for sorting
        documents.sort(key=lambda d: d.modified_at, reverse=True)
        
        return DocumentListResponse(
            documents=documents,
            total=counts['total']
        )
    
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list documents")


@router.get("/topics", response_model=TopicDocumentsResponse)
async def list_documents_by_topic(
    search_engine: SearchEngine = Depends(get_search_engine)
):
    """
    List documents grouped by topic
    
    Returns topics in alphabetical order
    """
    try:
        # Get documents grouped by topic
        by_topic = search_engine.list_documents_by_topic()
        
        # Transform to response format
        topics = {}
        for topic, docs in by_topic.items():
            topics[topic] = [
                DocumentResponse(
                    filename=doc['title'],
                    file_path=doc['relative_path'],
                    topic=doc['topic'],
                    modified_at=doc['modified_date'],
                    size_kb=round(doc['size_bytes'] / 1024, 2)
                )
                for doc in docs
            ]
        
        # Sort topics alphabetically
        sorted_topics = {k: topics[k] for k in sorted(topics.keys())}
        
        return TopicDocumentsResponse(topics=sorted_topics)
    
    except Exception as e:
        logger.error(f"Error listing documents by topic: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list documents by topic")


@router.get("/search", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., description="Search query string"),
    top_k: int = Query(5, ge=1, le=50, description="Maximum number of results"),
    min_score: float = Query(0.2, ge=0.0, le=1.0, description="Minimum similarity score"),
    search_engine: SearchEngine = Depends(get_search_engine)
):
    """
    Search documents by content using hybrid search
    
    Combines semantic understanding with keyword boosting for technical terms
    """
    # Validate query is not empty
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty")
    
    # T-06-15 mitigation: Validate top_k <= 50
    if top_k > 50:
        raise HTTPException(status_code=400, detail="top_k cannot exceed 50")
    
    try:
        # Perform hybrid search
        results = search_engine.hybrid_search(
            query=query.strip(),
            top_k=top_k,
            min_score=min_score
        )
        
        # Transform to response format
        search_results = []
        for result in results:
            metadata = result.get('metadata', {})
            # Try different possible keys for the file path
            path = metadata.get('relative_path') or metadata.get('path') or metadata.get('file_path') or 'unknown'
            
            search_results.append(SearchResultItem(
                content=result['content'],
                score=result['score'],
                document_path=path,
                chunk_id=str(result['node_id'])
            ))
        
        return SearchResponse(
            results=search_results,
            query=query,
            total=len(search_results)
        )
    
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search documents")


@router.get("/stats", response_model=Dict[str, Any])
async def get_document_stats(
    search_engine: SearchEngine = Depends(get_search_engine),
    document_store: DocumentStore = Depends(get_document_store)
):
    """
    Get document statistics
    
    Returns document counts by type and topic
    """
    try:
        # Get file type counts
        counts = document_store.get_document_count()
        
        # Get topic counts
        by_topic = search_engine.list_documents_by_topic()
        topic_counts = {topic: len(docs) for topic, docs in by_topic.items()}
        
        return {
            "total": counts['total'],
            "by_type": {
                "markdown": counts['markdown'],
                "excel": counts['excel']
            },
            "by_topic": topic_counts
        }
    
    except Exception as e:
        logger.error(f"Error getting document stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get document statistics")

@router.post("/reindex")
async def reindex_documents(
    document_store: DocumentStore = Depends(get_document_store)
):
    """
    Clear and rebuild the entire knowledge base index.
    """
    from src.indexing.document_indexer import DocumentIndexer
    from src.api.dependencies import get_vector_store
    try:
        vector_store = get_vector_store()
        indexer = DocumentIndexer(document_store=document_store, vector_store=vector_store)
        indexer.index_all_documents(clear_existing=True)
        return {"status": "success", "message": "Knowledge base rebuilt successfully."}
    except Exception as e:
        logger.error(f"Error reindexing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to rebuild knowledge base: {str(e)}")

