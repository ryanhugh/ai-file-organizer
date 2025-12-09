"""
Utility functions.
"""
import sys
from pathlib import Path


# Auto-fix imports for direct script execution
# This allows processor files to be run directly with: python3 processors/images.py
if __name__ != '__main__':
    # Only do this when imported as a module
    _current_file = Path(__file__).resolve()
    _project_root = _current_file.parent
    
    # If we're in a subdirectory (like processors/), add parent to path
    if _project_root.name == 'processors':
        _project_root = _project_root.parent
    
    # Add project root to path if not already there
    _project_root_str = str(_project_root)
    if _project_root_str not in sys.path:
        sys.path.insert(0, _project_root_str)


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