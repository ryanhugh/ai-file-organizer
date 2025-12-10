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
from processors.cache import FileCache
from llm_client import get_llm_client


class ImageProcessor(MediaProcessor):
    """Process image files."""
    
    # Supported image file extensions
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic', '.heif'}
    
    def __init__(self):
        """Initialize the image processor with OCR and vision model enabled."""
        print("Initializing EasyOCR for image text extraction...")
        # Initialize EasyOCR with English support
        self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        self.summary_generator = SummaryGenerator()
        self.ocr_cache = FileCache('ocr')
        self.vision_cache = FileCache('vision')  # Separate cache for LLaVA
        print("OCR enabled for image processing")
    
    def _analyze_with_vision_model(self, file_path: Path) -> str:
        """
        Analyze image using LLaVA vision model.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Description of what's in the image
        """
        # Check vision cache first
        file_hash = self.vision_cache.get_file_hash(file_path)
        cached_description = self.vision_cache.get(file_hash)
        
        if cached_description is not None:
            print(f"  ✓ Using cached vision analysis for {file_path.name}")
            return cached_description
        
        try:
            llm_client = get_llm_client()
            
            # Use LLaVA to analyze the image
            response = llm_client.generate(
                model='llava:7b',  # or 'llava:13b' for better quality
                prompt='Describe what you see in this image in detail. Include any text, UI elements, people, objects, or activities visible. Be specific about colors, layout, and context.',
                images=[str(file_path)]
            )
            
            description = response['response'].strip()
            
            # Cache the result
            self.vision_cache.set(file_hash, description)
            
            return description
            
        except Exception as e:
            print(f"  Warning: Vision model analysis failed: {str(e)}")
            return ""
    
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
            # Check OCR cache first
            file_hash = self.ocr_cache.get_file_hash(file_path)
            ocr_text = self.ocr_cache.get(file_hash)
            
            if ocr_text is not None:
                print(f"  ✓ Using cached OCR for {file_path.name}")
            else:
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
                
                # Cache the OCR result
                self.ocr_cache.set(file_hash, ocr_text)
            
            # Print the OCR text
            if ocr_text:
                print(f"\n  📝 OCR Text from {file_path.name}:")
                print(f"  {'-' * 70}")
                print(f"  {ocr_text}")
                print(f"  {'-' * 70}\n")
            
            # Analyze with vision model
            vision_description = self._analyze_with_vision_model(file_path)
            
            if vision_description:
                print(f"\n  👁️  Vision Model Analysis:")
                print(f"  {'-' * 70}")
                print(f"  {vision_description}")
                print(f"  {'-' * 70}\n")
            
            # Generate summary combining OCR and vision analysis
            summary = self._generate_summary(file_path.name, ocr_text, vision_description)
            
            # Get metadata
            metadata = self._get_metadata(file_path)
            
            # Build final summary with metadata appended
            final_summary = summary if summary else '(No text detected in image)'
            
            if metadata:
                final_summary += f"\n\nMetadata: {metadata}"
            
            final_summary += f"\n\nFilename: {file_path.name}"
            
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
    
    def _generate_summary(self, filename: str, ocr_text: str, vision_description: str = "") -> str:
        """
        Generate a concise summary of the image content using LLM.
        
        Args:
            filename: Name of the image file
            ocr_text: OCR text from the image
            vision_description: Description from vision model
            
        Returns:
            One paragraph summary
        """
        if not ocr_text and not vision_description:
            return ""
        
        # Build context for the LLM
        context_parts = [f"Image file: {filename}"]
        
        if vision_description:
            context_parts.append(f"\nVisual description:\n{vision_description[:500]}")
        
        if ocr_text:
            context_parts.append(f"\nText visible in image:\n{ocr_text[:1000]}")
        
        context = "\n".join(context_parts)
        
        # Create prompt for summary
        prompt = f"""Based on the following information about an image, write a single concise paragraph (2-3 sentences) describing what this image is about. Focus on the main topic, what's being shown, and any key information (eg proper names, dates, etc).
        Super important to keep proper names and dates, including S3 bucket names. 

        DO not say "This image appears to be a screenshot of " or any other filler text just get right to the point. eg "An image of a child process..."

{context}

Summary:"""

        print('prompt we are sending to llm to make summary', prompt)
        
        return self.summary_generator.generate(prompt)


if __name__ == '__main__':
    # Test the image processor
    
    # NOTE this file name has some odd character in it just before PM. THis character is not a normal space. 
    # image_path = Path('/Users/ryanhughes/Desktop/file-organizer-test/Screenshot 2025-11-08 at 3.30.59 PM.png')
    image_path = Path('/Users/ryanhughes/Desktop/file-organizer-test/Screenshot 2025-10-21 at 5.56.00 PM.png')
    # image_path = Path('/Users/ryanhughes/Desktop/file-organizer-test/Screenshot 2025-10-22 at 8.54.40 PM.png')
    if not image_path.exists():
        print(f"Error: File not found: {image_path}")
        print("Please update the path in the script or provide a valid image path")
        sys.exit(1)
    
    # Initialize processor (LLM client is auto-initialized on first use)
    processor = ImageProcessor()
    
    print(f"Processing: {image_path.name}")
    print("=" * 50)
    
    # Process the image
    result = processor.process(image_path)
    if result['success']:
        print(f"\n✓ Success!")
        print(f"Summary:\n{result['summary']}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")
