"""
Image file processor.
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import cv2
import easyocr
import numpy as np

from PIL import Image
from PIL.ExifTags import TAGS

from .summary import SummaryGenerator


class ImageProcessor:
    """Process image files."""
    
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
    
    def process(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from image files."""
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
    
    def ocr_image(self, image_path: Path) -> Dict[str, Any]:
        """
        Perform OCR on a single image file and generate a summary.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with OCR text and summary
        """
        try:
            # Read image with OpenCV
            frame = cv2.imread(str(image_path))
            if frame is None:
                return {'text': '', 'summary': '', 'success': False}
            
            ocr_text = self.ocr_frame(frame)
            
            # Print the OCR text
            if ocr_text:
                print(f"\n  📝 OCR Text from {image_path.name}:")
                print(f"  {'-' * 70}")
                print(f"  {ocr_text}")
                print(f"  {'-' * 70}\n")
            
            # Generate summary
            summary = self._generate_summary(image_path.name, ocr_text)
            if summary:
                print(f"  📋 Summary:")
                print(f"  {'-' * 70}")
                print(f"  {summary}")
                print(f"  {'-' * 70}\n")
            
            return {
                'text': ocr_text,
                'summary': summary,
                'success': True
            }
            
        except Exception as e:
            print(f"  Error performing OCR on {image_path.name}: {str(e)}")
            return {'text': '', 'summary': '', 'error': str(e), 'success': False}
    
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
        prompt = f"""Based on the following image content, write a single concise paragraph (2-3 sentences) describing what this image is about. Focus on the main topic, what's being shown, and any key information.

{context}

Summary:"""
        
        return self.summary_generator.generate(prompt)


if __name__ == '__main__':
    # Test the image processor
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
    result = processor.ocr_image(image_path)
    if result['success']:
        print(f"\nOCR Result:")
        print(f"Text: {result['text'] if result['text'] else '(No text detected)'}")
        print(f"Summary: {result['summary'] if result['summary'] else '(No summary generated)'}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
