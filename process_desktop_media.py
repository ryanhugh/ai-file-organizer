#!/usr/bin/env python3
"""
Process all media files on Desktop and generate summaries.
"""
import argparse
from pathlib import Path
from datetime import datetime
from multiprocessing import Process, Queue, Manager
import psutil
import os
import signal
from processors.images import ImageProcessor
from processors.videos import VideoTranscriber
from processors.documents import DocumentProcessor
from processors.text import TextProcessor
from processors.archives import ArchiveProcessor
from processors.cache import cleanup_cache_locks


def worker_process(worker_id: int, task_queue: Queue, result_queue: Queue):
    """
    Worker process that initializes processors once and processes files from queue.
    
    Args:
        worker_id: Unique ID for this worker
        task_queue: Queue to pull file paths from
        result_queue: Queue to put results into
    """
    print(f"Worker {worker_id}: Initializing...")
    
    # Initialize all processors once per worker
    print(f"Worker {worker_id}: Loading ImageProcessor (EasyOCR)...")
    image_processor = ImageProcessor()
    
    print(f"Worker {worker_id}: Loading VideoTranscriber (Whisper)...")
    video_processor = VideoTranscriber(
        model_size="base",
        enable_ocr=True,
        frame_interval=5
    )
    
    print(f"Worker {worker_id}: Loading DocumentProcessor...")
    document_processor = DocumentProcessor()
    
    print(f"Worker {worker_id}: Loading TextProcessor...")
    text_processor = TextProcessor()
    
    print(f"Worker {worker_id}: Loading ArchiveProcessor...")
    archive_processor = ArchiveProcessor()
    
    print(f"Worker {worker_id}: Ready to process files\n")
    
    # Process files from queue until we get None (poison pill)
    while True:
        file_path_str = task_queue.get()
        
        # None signals end of work
        if file_path_str is None:
            print(f"Worker {worker_id}: Received poison pill, exiting")
            break
        
        print(f"Worker {worker_id}: Processing {Path(file_path_str).name}...")
        
        file_path = Path(file_path_str)
        ext = file_path.suffix.lower()
        
        # Select appropriate processor
        if ext in ImageProcessor.SUPPORTED_EXTENSIONS:
            processor = image_processor
        elif ext in VideoTranscriber.SUPPORTED_EXTENSIONS:
            processor = video_processor
        elif ext in DocumentProcessor.SUPPORTED_EXTENSIONS:
            processor = document_processor
        elif ext in TextProcessor.SUPPORTED_EXTENSIONS:
            processor = text_processor
        elif ext in ArchiveProcessor.SUPPORTED_EXTENSIONS:
            processor = archive_processor
        else:
            result_queue.put({
                'filename': file_path.name,
                'summary': '(Error: Unsupported file type)',
                'success': False
            })
            continue
        
        # Process the file
        try:
            result = processor.process(file_path)
            
            if result['success']:
                print(f"Worker {worker_id}: ✓ {file_path.name}")
                result_queue.put({
                    'filename': file_path.name,
                    'summary': result['summary'],
                    'success': True
                })
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"Worker {worker_id}: ✗ {file_path.name} - {error_msg}")
                result_queue.put({
                    'filename': file_path.name,
                    'summary': f'(Error: {error_msg})',
                    'success': False
                })
        except Exception as e:
            print(f"Worker {worker_id}: ✗ {file_path.name} - {str(e)}")
            result_queue.put({
                'filename': file_path.name,
                'summary': f'(Unexpected error: {str(e)})',
                'success': False
            })
    
    # Clean up all child processes before exiting
    print(f"Worker {worker_id}: Cleaning up child processes...")
    try:
        current_process = psutil.Process(os.getpid())
        children = current_process.children(recursive=True)
        
        for child in children:
            try:
                print(f"Worker {worker_id}: Terminating child process {child.pid} ({child.name()})")
                child.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Wait a bit for graceful termination
        gone, alive = psutil.wait_procs(children, timeout=3)
        
        # Force kill any remaining processes
        for child in alive:
            try:
                print(f"Worker {worker_id}: Force killing child process {child.pid}")
                child.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"Worker {worker_id}: Error during cleanup: {e}")
    
    print(f"Worker {worker_id}: Shutting down")


def process_desktop_media(num_processes: int = 8, group_files: bool = False):
    """
    Process all media files on Desktop.
    
    Args:
        num_processes: Number of parallel processes to use (default: 8)
        group_files: Whether to group files by semantic similarity
    """
    # Setup paths
    desktop_path = Path.home() / "Desktop"
    log_file = desktop_path / f"media_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print(f"Processing media files in: {desktop_path}")
    print(f"Log file will be saved to: {log_file}")
    print("=" * 80)
    
    # Clean up stale lock files from previous runs
    print()
    cleanup_cache_locks()
    
    # Find all supported files
    print(f"\nScanning {desktop_path} for supported files...")
    supported_extensions = (
        ImageProcessor.SUPPORTED_EXTENSIONS | 
        VideoTranscriber.SUPPORTED_EXTENSIONS |
        DocumentProcessor.SUPPORTED_EXTENSIONS |
        TextProcessor.SUPPORTED_EXTENSIONS |
        ArchiveProcessor.SUPPORTED_EXTENSIONS
    )
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
    
    # Create queues for tasks and results
    task_queue = Queue()
    result_queue = Queue()
    
    # Add all files to task queue
    print(f"\n{'='*80}")
    print(f"ADDING {len(media_files)} FILES TO QUEUE")
    print(f"{'='*80}\n")
    
    for file_path in media_files:
        task_queue.put(str(file_path))
    
    # Add poison pills (one per worker to signal completion)
    for _ in range(num_processes):
        task_queue.put(None)
    
    # Start worker processes
    print(f"{'='*80}")
    print(f"STARTING {num_processes} WORKER PROCESSES")
    print(f"{'='*80}\n")
    
    workers = []
    for i in range(num_processes):
        worker = Process(target=worker_process, args=(i, task_queue, result_queue))
        worker.start()
        workers.append(worker)
    
    # Wait for all workers to complete
    for worker in workers:
        worker.join()
    
    print(f"\n{'='*80}")
    print("ALL WORKERS COMPLETED")
    print(f"{'='*80}\n")
    
    # Collect results from queue
    print("Collecting results from queue...")
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    print(f"✓ Collected {len(results)} results")
    
    # Close queues to prevent hanging on exit
    print("Closing queues...")
    task_queue.close()
    task_queue.join_thread()
    result_queue.close()
    result_queue.join_thread()
    print("✓ Queues closed")
    
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
    
    # Group files if requested
    if group_files:
        print(f"\n{'='*80}")
        print("GROUPING FILES BY SIMILARITY")
        print(f"{'='*80}\n")
        
        from file_grouper import FileGrouper
        
        # Filter successful results
        successful_results = [r for r in results if r.get('success', False)]
        
        if successful_results:
            grouper = FileGrouper()
            groups = grouper.group_files(successful_results, min_cluster_size=2)
            
            # Save groups to JSON
            groups_file = desktop_path / f"file_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            grouper.save_groups(groups, groups_file)
            
            # Print summary
            grouper.print_groups(groups)
        else:
            print("No successful results to group.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process all media files on Desktop and generate summaries.'
    )
    parser.add_argument(
        '-p', '--processes',
        type=int,
        default=8,
        help='Number of parallel processes to use (default: 8)'
    )
    parser.add_argument(
        '-g', '--group',
        action='store_true',
        help='Group files by semantic similarity after processing'
    )
    
    args = parser.parse_args()
    process_desktop_media(num_processes=args.processes, group_files=args.group)
