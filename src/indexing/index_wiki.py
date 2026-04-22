#!/usr/bin/env python3
"""
Index all documents from wiki directory into Qdrant vector database.

This script loads all documents from the user's wiki directory and indexes
them into the Qdrant vector database for semantic search.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.storage.document_store import DocumentStore
from src.storage.vector_store import EcoMindVectorStore
from src.indexing.document_indexer import DocumentIndexer


def main():
    """Index all wiki documents into vector database."""
    print("=" * 60)
    print("EcoMind Knowledge Base - Document Indexing")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing storage components...")
    doc_store = DocumentStore.from_env()  # Uses WIKI_PATH env var or default
    vector_store = EcoMindVectorStore()
    indexer = DocumentIndexer(doc_store, vector_store)
    
    # Get document count before indexing
    print("\n2. Scanning wiki directory...")
    doc_count = doc_store.get_document_count()
    print(f"   Found {doc_count['total']} documents:")
    print(f"   - {doc_count['markdown']} Markdown files")
    print(f"   - {doc_count['excel']} Excel files")
    
    if doc_count['total'] == 0:
        print("\n❌ No documents found. Please check wiki directory path.")
        vector_store.close()
        return
    
    # Index all documents
    print("\n3. Indexing documents...")
    try:
        index = indexer.index_all_documents()
        
        # Verify indexing succeeded
        print("\n4. Verifying indexing results...")
        stats = indexer.get_index_stats()
        print(f"   ✓ {stats['total_documents']} documents processed")
        print(f"   ✓ {stats['points_count']} vector chunks stored")
        print(f"   ✓ Collection status: {stats['collection_status']}")
        
        print("\n" + "=" * 60)
        print("✅ Indexing complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Indexing failed: {str(e)}")
        raise
    finally:
        # Clean up
        vector_store.close()


if __name__ == "__main__":
    main()
