#!/usr/bin/env python3
"""
Test OCR on a single frame from a video.
"""
import subprocess
import sys
from pathlib import Path

# Extract one frame from the video
import os
video_files = [f for f in os.listdir("/Users/ryanhughes/Desktop/file-organizer-test") if f.endswith('.mov')]
if not video_files:
    print("No .mov files found!")
    sys.exit(1)

video_path = os.path.join("/Users/ryanhughes/Desktop/file-organizer-test", video_files[0])
output_frame = "/tmp/test_frame.jpg"

print(f"Extracting frame from: {video_path}")
print(f"Output: {output_frame}")

# Use ffmpeg to extract frame at 10 seconds
cmd = [
    'ffmpeg',
    '-i', video_path,
    '-ss', '10',  # Extract at 10 seconds
    '-vframes', '1',  # Extract 1 frame
    '-q:v', '2',  # High quality
    '-y',  # Overwrite
    output_frame
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"Error extracting frame: {result.stderr}")
    sys.exit(1)

print(f"✓ Frame extracted to: {output_frame}")
print(f"\nNow testing OCR with EasyOCR...")

# Test OCR
try:
    import easyocr
    import cv2
    
    print("Loading EasyOCR...")
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    print("✓ EasyOCR loaded")
    
    # Read the frame
    frame = cv2.imread(output_frame)
    if frame is None:
        print(f"Error: Could not read frame from {output_frame}")
        sys.exit(1)
    
    print(f"✓ Frame loaded: {frame.shape}")
    
    # Perform OCR
    print("\nPerforming OCR...")
    results = reader.readtext(frame, detail=0, paragraph=True)
    
    print(f"\n{'='*70}")
    print(f"OCR Results ({len(results)} text blocks found):")
    print(f"{'='*70}")
    
    if results:
        for i, text in enumerate(results, 1):
            print(f"\n[Block {i}]")
            print(text)
    else:
        print("No text detected")
    
    print(f"\n{'='*70}")
    print(f"\nFrame saved at: {output_frame}")
    print("You can open this image to see what was OCR'd")
    
except ImportError as e:
    print(f"Error: {e}")
    print("Install with: pip3 install --break-system-packages easyocr")
    sys.exit(1)
except Exception as e:
    print(f"Error during OCR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
