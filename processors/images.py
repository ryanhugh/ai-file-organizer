"""
Image file processor.
"""
# Import fix must be first - enables running as both module and script
try:
    from . import _import_fix
except ImportError:
    import _import_fix

import sys
from pathlib import Path
from typing import Dict, Any, Optional

import cv2
import easyocr
import numpy as np

from PIL import Image
from PIL.ExifTags import TAGS

from processors.base import MediaProcessor
from processors.summary import SummaryGenerator


class ImageProcessor(MediaProcessor):
    """Process image files."""
    
    # Supported image file extensions
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic', '.heif'}
    
    def __init__(self, llm_client=None):
        """
        Initialize the image processor with OCR enabled.
        
        Args:
            llm_client: Ollama client for generating summaries
        """
        print("Initializing EasyOCR for image text extraction...")
        # Initialize EasyOCR with English support
        self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        self.llm_client = llm_client
        self.summary_generator = SummaryGenerator(llm_client=llm_client)
        print("OCR enabled for image processing")
    
    def _get_metadata(self, file_path: Path) -> str:
        """Extract and format metadata from image files."""
        try:
            with Image.open(file_path) as img:
                parts = []
                parts.append(f"Dimensions: {img.width}x{img.height}")
                parts.append(f"Format: {img.format}")
                
                # Extract EXIF data if available
                exif_data = img.getexif()
                if exif_data:
                    exif_items = []
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag in ['DateTime', 'Make', 'Model', 'Software']:
                            exif_items.append(f"{tag}: {str(value)[:50]}")
                    if exif_items:
                        parts.extend(exif_items)
                    
                return ', '.join(parts)
        except Exception as e:
            return f"Error reading metadata: {str(e)}"
    
    
    def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Process an image file with OCR and generate a summary.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dictionary with success status and summary
        """
        try:
            # Read image with OpenCV
            frame = cv2.imread(str(file_path))
            if frame is None:
                return {
                    'success': False,
                    'summary': '',
                    'error': 'Failed to read image file'
                }
            
            # Perform OCR
            ocr_text = self.ocr_frame(frame)
            
            # Print the OCR text
            if ocr_text:
                print(f"\n  📝 OCR Text from {file_path.name}:")
                print(f"  {'-' * 70}")
                print(f"  {ocr_text}")
                print(f"  {'-' * 70}\n")
            
            # Generate summary
            summary = self._generate_summary(file_path.name, ocr_text)
            
            # Get metadata
            metadata = self._get_metadata(file_path)
            
            # Build final summary with metadata appended
            final_summary = summary if summary else '(No text detected in image)'
            
            if metadata:
                final_summary += f"\n\nMetadata: {metadata}"
            
            if summary:
                print(f"  📋 Summary:")
                print(f"  {'-' * 70}")
                print(f"  {final_summary}")
                print(f"  {'-' * 70}\n")
            
            return {
                'success': True,
                'summary': final_summary
            }
            
        except Exception as e:
            print(f"  Error processing {file_path.name}: {str(e)}")
            return {
                'success': False,
                'summary': '',
                'error': str(e)
            }
    
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
    
    def _generate_summary(self, filename: str, ocr_text: str) -> str:
        """
        Generate a concise summary of the image content using LLM.
        
        Args:
            filename: Name of the image file
            ocr_text: OCR text from the image
            
        Returns:
            One paragraph summary
        """
        if not ocr_text or not ocr_text.strip():
            return ""
        
        # Build context for the LLM
        context = f"""Image file: {filename}

Text visible in image:
{ocr_text[:1000]}"""
        
        # Create prompt for summary
        prompt = f"""Based on the following text extracted from an image, write a single concise paragraph (2-3 sentences) describing what this image is about. Focus on the main topic, what's being shown, and any key information (eg proper names, dates, etc).

{context}

Summary:"""

        print('prompt we are sending to llm to make summary', prompt)
        
        return self.summary_generator.generate(prompt)


if __name__ == '__main__':
    # Test the image processor
    import ollama
    
    # NOTE this file name has some odd character in it just before PM. THis character is not a normal space. 
    image_path = Path('/Users/ryanhughes/Desktop/file-organizer-test/Screenshot 2025-11-08 at 3.30.59 PM.png')
    if not image_path.exists():
        print(f"Error: File not found: {image_path}")
        print("Please update the path in the script or provide a valid image path")
        sys.exit(1)
    
    # Initialize with LLM client for summary generation
    print("Initializing Ollama client...")
    llm_client = ollama.Client()
    processor = ImageProcessor(llm_client=llm_client)
    
    print(f"Processing: {image_path.name}")
    print("=" * 50)
    
    # Process the image
    result = processor.process(image_path)
    if result['success']:
        print(f"\n✓ Success!")
        print(f"Summary:\n{result['summary']}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")
