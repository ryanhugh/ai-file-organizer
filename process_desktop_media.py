#!/usr/bin/env python3
"""
Process all media files on Desktop and generate summaries.
"""
from pathlib import Path
from datetime import datetime
from multiprocessing import Pool
import ollama
from processors.images import ImageProcessor
from processors.videos import VideoTranscriber


def process_single_file(file_path_str: str) -> dict:
    """
    Process a single media file (called by worker process).
    
    Args:
        file_path_str: String path to the file
        
    Returns:
        Dictionary with filename and summary
    """
    file_path = Path(file_path_str)
    
    # Each process creates its own processor instances and LLM client
    llm_client = ollama.Client()
    
    # Determine file type and create appropriate processor
    ext = file_path.suffix.lower()
    
    if ext in ImageProcessor.SUPPORTED_EXTENSIONS:
        processor = ImageProcessor(llm_client=llm_client)
    elif ext in VideoTranscriber.SUPPORTED_EXTENSIONS:
        processor = VideoTranscriber(
            model_size="base",
            enable_ocr=True,
            frame_interval=5,
            llm_client=llm_client
        )
    else:
        return {
            'filename': file_path.name,
            'summary': '(Error: Unsupported file type)',
            'success': False
        }
    
    # Process the file
    try:
        result = processor.process(file_path)
        
        if result['success']:
            print(f"✓ Successfully processed {file_path.name}")
            return {
                'filename': file_path.name,
                'summary': result['summary'],
                'success': True
            }
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"✗ Error processing {file_path.name}: {error_msg}")
            return {
                'filename': file_path.name,
                'summary': f'(Error: {error_msg})',
                'success': False
            }
    except Exception as e:
        print(f"✗ Unexpected error processing {file_path.name}: {str(e)}")
        return {
            'filename': file_path.name,
            'summary': f'(Unexpected error: {str(e)})',
            'success': False
        }


def process_desktop_media():
    """Process all media files on Desktop."""
    
    # Setup paths
    desktop_path = Path.home() / "Desktop"
    log_file = desktop_path / f"media_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print(f"Processing media files in: {desktop_path}")
    print(f"Log file will be saved to: {log_file}")
    print("=" * 80)
    
    # Find all media files
    print(f"\nScanning {desktop_path} for media files...")
    supported_extensions = ImageProcessor.SUPPORTED_EXTENSIONS | VideoTranscriber.SUPPORTED_EXTENSIONS
    media_files = []
    
    for file_path in desktop_path.iterdir():
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in supported_extensions:
                media_files.append(file_path)
    
    print(f"Found {len(media_files)} media file(s)")
    print("=" * 80)
    
    if not media_files:
        print("\nNo media files to process.")
        return
    
    # Process files in parallel with 8 processes
    print(f"\n{'='*80}")
    print(f"PROCESSING {len(media_files)} FILES WITH 8 PROCESSES")
    print(f"{'='*80}\n")
    
    # Convert paths to strings for multiprocessing
    file_paths_str = [str(f) for f in media_files]
    
    # Use multiprocessing Pool with 8 workers
    with Pool(processes=8) as pool:
        results = pool.map(process_single_file, file_paths_str)
    
    # Filter out None results
    results = [r for r in results if r is not None]
    
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
