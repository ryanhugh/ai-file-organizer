"""
Singleton LLM client for thread-safe access across the application.
"""
import ollama
from typing import Optional

# Global client instance
_llm_client: Optional[ollama.Client] = None


def get_llm_client() -> ollama.Client:
    """
    Get or create the global LLM client instance.
    
    This is thread-safe because:
    1. ollama.Client() is thread-safe (uses HTTP requests)
    2. Multiple initializations are harmless (just creates new client objects)
    3. No shared mutable state between threads
    
    Returns:
        ollama.Client instance
    """
    global _llm_client
    
    if _llm_client is None:
        _llm_client = ollama.Client()
    
    return _llm_client
