from pathlib import Path
from typing import List, Dict, Any, Optional
from llama_index.core import SimpleDirectoryReader, Document
import os

class DocumentStore:
    """Interface for reading documents from file system"""
    
    def __init__(self, base_path: str = "/Users/a1234/wiki/raw/articles"):
        """
        Initialize document storage
        
        Args:
            base_path: Path to wiki articles directory
        """
        self.base_path = Path(base_path)
        
        if not self.base_path.exists():
            raise FileNotFoundError(
                f"Wiki directory not found: {base_path}\n"
                f"Please ensure the directory exists or set WIKI_PATH environment variable."
            )
        
        if not self.base_path.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {base_path}"
            )
    
    def load_all_documents(self) -> List[Document]:
        """
        Load all documents from the wiki directory
        
        Returns:
            List of LlamaIndex Document objects
        """
        reader = SimpleDirectoryReader(
            str(self.base_path),
            recursive=True,
            required_exts=[".md", ".xlsx"]  # Markdown and Excel
        )
        
        documents = reader.load_data()
        
        # Enrich documents with metadata
        for doc in documents:
            if hasattr(doc, 'metadata') and 'file_path' in doc.metadata:
                file_path = Path(doc.metadata['file_path'])
                doc.metadata.update(self.get_document_metadata(file_path))
        
        return documents
    
    def list_documents(self) -> List[Path]:
        """
        List all document files in the wiki directory
        
        Returns:
            List of Path objects for each document
        """
        md_files = list(self.base_path.glob("**/*.md"))
        excel_files = list(self.base_path.glob("**/*.xlsx"))
        
        # Filter out hidden files and temp files
        all_files = md_files + excel_files
        filtered_files = [
            f for f in all_files 
            if not f.name.startswith('.') and not f.name.startswith('~')
        ]
        
        # Sort by filename (not full path)
        return sorted(filtered_files, key=lambda p: p.name)
    
    def get_document_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from document file
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with file metadata
        """
        stat = file_path.stat()
        
        return {
            "path": str(file_path),
            "name": file_path.name,
            "extension": file_path.suffix,
            "size_bytes": stat.st_size,
            "modified_timestamp": stat.st_mtime,
            "relative_path": str(file_path.relative_to(self.base_path))
        }
    
    def get_document_count(self) -> Dict[str, int]:
        """
        Get count of documents by type
        
        Returns:
            Dictionary with counts by file extension
        """
        files = self.list_documents()
        
        counts = {
            "markdown": len([f for f in files if f.suffix == ".md"]),
            "excel": len([f for f in files if f.suffix == ".xlsx"]),
            "total": len(files)
        }
        
        return counts

    @staticmethod
    def from_env() -> "DocumentStore":
        """
        Create DocumentStore from environment variable
        
        Returns:
            DocumentStore instance with path from WIKI_PATH env var
        """
        wiki_path = os.getenv("WIKI_PATH", "/Users/a1234/wiki/raw/articles")
        return DocumentStore(base_path=wiki_path)
