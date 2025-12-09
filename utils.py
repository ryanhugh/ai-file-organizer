"""
Utility functions.
"""
from pathlib import Path


def find_project_root() -> Path:
    """
    Find the project root by looking for requirements.txt.
    
    Returns:
        Path to project root directory
    """
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / 'requirements.txt').exists():
            return current
        current = current.parent
    # Fallback to the directory containing this file
    return Path(__file__).resolve().parent

if __name__ == '__main__':
    print(find_project_root())