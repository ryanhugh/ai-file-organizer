"""
Import path fixer for running processor files directly.

Import this at the very top of any processor file to enable both:
- Running as module: python -m processors.images
- Running as script: python processors/images.py
"""
import sys
from pathlib import Path

# Add project root to path when running as direct script
_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent  # Go up from processors/ to project root

_project_root_str = str(_project_root)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
