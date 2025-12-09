#!/usr/bin/env python3
"""
Process all media files on Desktop and generate summaries.
"""
from pathlib import Path
from datetime import datetime
import ollama
from processors.images import ImageProcessor
from processors.videos import VideoTranscriber


def process_desktop_media():
    """Process all media files on Desktop."""
    
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
    processors = [
        ImageProcessor(llm_client=llm_client),
        VideoTranscriber(
            model_size="base",
            enable_ocr=True,
            frame_interval=5,
            llm_client=llm_client
        )
    ]
    
    # Build extension to processor mapping
    ext_to_processor = {}
    for processor in processors:
        for ext in processor.SUPPORTED_EXTENSIONS:
            ext_to_processor[ext] = processor
    
    # Find all media files
    print(f"\nScanning {desktop_path} for media files...")
    media_files = []
    
    for file_path in desktop_path.iterdir():
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in ext_to_processor:
                media_files.append(file_path)
    
    print(f"Found {len(media_files)} media file(s)")
    print("=" * 80)
    
    # Process files and collect results
    results = []
    
    print(f"\n{'='*80}")
    print(f"PROCESSING {len(media_files)} FILES")
    print(f"{'='*80}\n")
    
    for i, file_path in enumerate(media_files, 1):
        print(f"\n[{i}/{len(media_files)}] Processing: {file_path.name}")
        print("-" * 80)
        
        ext = file_path.suffix.lower()
        processor = ext_to_processor.get(ext)
        
        if not processor:
            print(f"✗ No processor found for {file_path.name}")
            continue
        
        try:
            result = processor.process(file_path)
            
            if result['success']:
                results.append({
                    'filename': file_path.name,
                    'summary': result['summary']
                })
                print(f"✓ Successfully processed {file_path.name}")
            else:
                error_msg = result.get('error', 'Unknown error')
                results.append({
                    'filename': file_path.name,
                    'summary': f'(Error: {error_msg})'
                })
                print(f"✗ Error processing {file_path.name}: {error_msg}")
                
        except Exception as e:
            print(f"✗ Unexpected error processing {file_path.name}: {str(e)}")
            results.append({
                'filename': file_path.name,
                'summary': f'(Unexpected error: {str(e)})'
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
        
        for item in results:
            f.write(f"File: {item['filename']}\n")
            f.write(f"Summary: {item['summary']}\n")
            f.write(f"\n{'-'*80}\n\n")
    
    print(f"✓ Log file written to: {log_file}")
    print(f"\nProcessing complete!")
    print(f"  - Total files processed: {len(results)}")


if __name__ == '__main__':
    process_desktop_media()
