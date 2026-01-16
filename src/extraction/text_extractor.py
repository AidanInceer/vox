"""Abstract interface for text extraction from various sources."""

from abc import ABC, abstractmethod


class TextExtractor(ABC):
    """Abstract base class for text extraction from different sources.
    
    Implementations:
        - ExtractFromTab: Extract text from browser tabs
        - ExtractFromURL: Extract text from web URLs
        - ExtractFromFile: Extract text from local HTML files
    """
    
    @abstractmethod
    def extract(self, source: str) -> str:
        """Extract text from the given source.
        
        Args:
            source: Source identifier (tab_id, URL, or file path)
        
        Returns:
            Extracted text content from the source
            
        Raises:
            ExtractionError: If text extraction fails
            TimeoutError: If extraction exceeds timeout
            ValidationError: If source is invalid
        """
        pass
    
    @abstractmethod
    def supports(self, source_type: str) -> bool:
        """Check if this extractor supports the given source type.
        
        Args:
            source_type: Type of source ('tab', 'url', 'file', etc.)
        
        Returns:
            True if this extractor can handle the source type
        """
        pass
