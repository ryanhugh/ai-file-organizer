"""
Image file processor.
"""
from pathlib import Path
from typing import Dict, Any

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ImageProcessor:
    """Process image files."""
    
    def process(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from image files."""
        if not PIL_AVAILABLE:
            return {'error': 'PIL not available'}
        
        try:
            with Image.open(file_path) as img:
                metadata = {
                    'dimensions': f"{img.width}x{img.height}",
                    'format': img.format,
                    'mode': img.mode
                }
                
                # Extract EXIF data if available
                exif_data = img.getexif()
                if exif_data:
                    exif = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif[tag] = str(value)[:100]  # Limit value length
                    metadata['exif'] = exif
                    
                return metadata
        except Exception as e:
            return {'error': str(e)}
    
    def format_metadata(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """Format image metadata as a string."""
        if 'error' in metadata:
            return f"Image file: {file_path.name} (error: {metadata['error']})"
        
        return f"Image file: {file_path.name}, {metadata.get('dimensions', 'unknown dimensions')}"
