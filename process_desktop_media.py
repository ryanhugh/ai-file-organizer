#!/usr/bin/env python3
"""
Process all images and videos on Desktop and generate summaries.
"""
from pathlib import Path
from datetime import datetime
import ollama
from processors.images import ImageProcessor
from processors.videos import VideoTranscriber


# Supported file extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic', '.heif'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}


def process_desktop_media():
    """Process all images and videos on Desktop."""
    
    # Setup paths
    desktop_path = Path.home() / "Desktop"
    log_file = desktop_path / f"media_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print(f"Processing media files in: {desktop_path}")
    print(f"Log file will be saved to: {log_file}")
    print("=" * 80)
    
    # Initialize Ollama client
    print("\nInitializing Ollama client...")
    llm_client = ollama.Client()
    
    # Initialize processors
    print("Initializing processors...")
    image_processor = ImageProcessor(llm_client=llm_client)
    video_transcriber = VideoTranscriber(
        model_size="base",
        enable_ocr=True,
        frame_interval=5,
        llm_client=llm_client
    )
    
    # Find all media files
    print(f"\nScanning {desktop_path} for media files...")
    image_files = []
    video_files = []
    
    for file_path in desktop_path.iterdir():
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                image_files.append(file_path)
            elif ext in VIDEO_EXTENSIONS:
                video_files.append(file_path)
    
    print(f"Found {len(image_files)} image(s) and {len(video_files)} video(s)")
    print("=" * 80)
    
    # Process files and collect results
    results = []
    
    # Process images
    if image_files:
        print(f"\n{'='*80}")
        print(f"PROCESSING IMAGES ({len(image_files)} files)")
        print(f"{'='*80}\n")
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Processing image: {image_path.name}")
            print("-" * 80)
            
            try:
                result = image_processor.ocr_image(image_path)
                
                if result['success'] and result.get('summary'):
                    results.append({
                        'type': 'image',
                        'filename': image_path.name,
                        'summary': result['summary'],
                        'text': result.get('text', '')
                    })
                    print(f"✓ Successfully processed {image_path.name}")
                else:
                    results.append({
                        'type': 'image',
                        'filename': image_path.name,
                        'summary': '(No summary generated - no text detected)',
                        'text': result.get('text', '')
                    })
                    print(f"⚠ No summary for {image_path.name} (no text detected)")
                    
            except Exception as e:
                print(f"✗ Error processing {image_path.name}: {str(e)}")
                results.append({
                    'type': 'image',
                    'filename': image_path.name,
                    'summary': f'(Error: {str(e)})',
                    'text': ''
                })
    
    # Process videos
    if video_files:
        print(f"\n{'='*80}")
        print(f"PROCESSING VIDEOS ({len(video_files)} files)")
        print(f"{'='*80}\n")
        
        for i, video_path in enumerate(video_files, 1):
            print(f"\n[{i}/{len(video_files)}] Processing video: {video_path.name}")
            print("-" * 80)
            
            try:
                result = video_transcriber.transcribe_video(video_path, max_duration=300)
                
                if result['success'] and result.get('summary'):
                    results.append({
                        'type': 'video',
                        'filename': video_path.name,
                        'summary': result['summary'],
                        'text': result.get('text', '')
                    })
                    print(f"✓ Successfully processed {video_path.name}")
                else:
                    results.append({
                        'type': 'video',
                        'filename': video_path.name,
                        'summary': '(No summary generated)',
                        'text': result.get('text', '')
                    })
                    print(f"⚠ No summary for {video_path.name}")
                    
            except Exception as e:
                print(f"✗ Error processing {video_path.name}: {str(e)}")
                results.append({
                    'type': 'video',
                    'filename': video_path.name,
                    'summary': f'(Error: {str(e)})',
                    'text': ''
                })
    
    # Write results to log file
    print(f"\n{'='*80}")
    print("WRITING LOG FILE")
    print(f"{'='*80}\n")
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Media File Summaries\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Desktop Path: {desktop_path}\n")
        f.write(f"Total Files Processed: {len(results)}\n")
        f.write(f"{'='*80}\n\n")
        
        # Group by type
        images = [r for r in results if r['type'] == 'image']
        videos = [r for r in results if r['type'] == 'video']
        
        if images:
            f.write(f"IMAGES ({len(images)})\n")
            f.write(f"{'-'*80}\n\n")
            for item in images:
                f.write(f"File: {item['filename']}\n")
                f.write(f"Summary: {item['summary']}\n")
                f.write(f"\n")
        
        if videos:
            f.write(f"\nVIDEOS ({len(videos)})\n")
            f.write(f"{'-'*80}\n\n")
            for item in videos:
                f.write(f"File: {item['filename']}\n")
                f.write(f"Summary: {item['summary']}\n")
                f.write(f"\n")
    
    print(f"✓ Log file written to: {log_file}")
    print(f"\nProcessing complete!")
    print(f"  - Images processed: {len(images)}")
    print(f"  - Videos processed: {len(videos)}")
    print(f"  - Total files: {len(results)}")


if __name__ == '__main__':
    process_desktop_media()
