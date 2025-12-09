"""
Base processor class for media files.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Set


class MediaProcessor(ABC):
    """Abstract base class for media file processors."""
    
    @property
    @abstractmethod
    def SUPPORTED_EXTENSIONS(self) -> Set[str]:
        """Return set of supported file extensions."""
        pass
    
    @abstractmethod
    def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a media file and return results.
        
        Args:
            file_path: Path to the media file
            
        Returns:
            Dictionary with:
                - success: bool - Whether processing succeeded
                - summary: str - One paragraph summary of the content
                - error: str (optional) - Error message if failed
        """
        pass
