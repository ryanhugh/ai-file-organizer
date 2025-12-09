#!/usr/bin/env python3
"""
Test script to demonstrate accessing supported file extensions.
"""
from processors.images import ImageProcessor
from processors.videos import VideoTranscriber


def test_supported_extensions():
    """Test accessing supported extensions from processor classes."""
    
    print("Supported File Extensions")
    print("=" * 60)
    
    # Access image extensions (no instance needed)
    print("\nImage Extensions:")
    print(f"  {sorted(ImageProcessor.SUPPORTED_EXTENSIONS)}")
    
    # Access video extensions (no instance needed)
    print("\nVideo Extensions:")
    print(f"  {sorted(VideoTranscriber.SUPPORTED_EXTENSIONS)}")
    
    # Example: Check if a file is supported
    test_files = [
        'photo.jpg',
        'video.mp4',
        'document.pdf',
        'image.png',
        'movie.avi'
    ]
    
    print("\n" + "=" * 60)
    print("File Type Detection:")
    print("=" * 60)
    
    for filename in test_files:
        ext = '.' + filename.split('.')[-1].lower()
        
        if ext in ImageProcessor.SUPPORTED_EXTENSIONS:
            print(f"  {filename:20} -> IMAGE")
        elif ext in VideoTranscriber.SUPPORTED_EXTENSIONS:
            print(f"  {filename:20} -> VIDEO")
        else:
            print(f"  {filename:20} -> UNSUPPORTED")


if __name__ == '__main__':
    test_supported_extensions()
