"""
Image file processor.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

import easyocr
import cv2


class ImageProcessor:
    """Process image files."""
    
    def __init__(self):
        """
        Initialize the image processor with OCR enabled.
        """
        print("Initializing EasyOCR for image text extraction...")
        # Initialize EasyOCR with English support
        self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("OCR enabled for image processing")
    
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
    
    def ocr_image(self, image_path: Path) -> str:
        """
        Perform OCR on a single image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted and cleaned text
        """
        try:
            # Read image with OpenCV
            frame = cv2.imread(str(image_path))
            if frame is None:
                return ""
            
            return self.ocr_frame(frame)
            
        except Exception as e:
            print(f"  Error performing OCR on {image_path.name}: {str(e)}")
            return ""
    
    def ocr_frame(self, frame: np.ndarray) -> str:
        """
        Perform OCR on a single image frame (numpy array).
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            Extracted and cleaned text
        """
        try:
            # EasyOCR works directly with numpy arrays (OpenCV frames)
            # It handles preprocessing internally
            results = self.ocr_reader.readtext(frame, detail=0, paragraph=True)
            
            # Combine all detected text
            text = '\n'.join(results)
            
            # Clean up the text
            text = self._clean_ocr_text(text)
            
            return text
            
        except Exception as e:
            return ""
    
    def _clean_ocr_text(self, text: str) -> str:
        """
        Clean up OCR output to remove garbage.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that are mostly non-alphanumeric (likely garbage)
            alphanumeric_count = sum(c.isalnum() or c.isspace() for c in line)
            if len(line) > 0 and alphanumeric_count / len(line) < 0.5:
                continue
            
            # Skip very short lines (likely noise) - but allow short meaningful words
            if len(line) < 2:
                continue
            
            # Skip lines with too many repeated characters (likely artifacts)
            if any(line.count(char) > len(line) * 0.5 for char in set(line)):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)


if __name__ == '__main__':
    # Test the image processor
    import sys
    
    # if len(sys.argv) < 2:
    #     print("Usage: python processors/images.py '/Users/ryanhughes/Desktop/file-organizer-test/Screenshot 2025-11-08 at 3.30.59 PM.png'")
    #     sys.exit(1)
    
    image_path = Path('/Users/ryanhughes/Desktop/file-organizer-test/Screenshot 2025-11-08 at 3.30.59 PM.png')
    if not image_path.exists():
        print(f"Error: File not found: {image_path}")
        sys.exit(1)
    
    processor = ImageProcessor()
    
    print(f"Processing: {image_path.name}")
    print("=" * 50)
    
    # Get metadata
    metadata = processor.process(image_path)
    print(f"Metadata: {metadata}")
    
    # Perform OCR
    text = processor.ocr_image(image_path)
    print(f"\nOCR Text:\n{'-' * 50}")
    print(text if text else "(No text detected)")
