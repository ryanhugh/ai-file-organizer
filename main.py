#!/usr/bin/env python3
"""
Intelligent File Organizer using Local LLM

Organizes files in a directory using a local LLM (via Ollama) to intelligently
categorize files and match them to existing projects.
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from file_extractor import FileExtractor
from llm_categorizer import LLMCategorizer
from project_manager import ProjectManager
from video_transcriber import VideoTranscriber


class FileOrganizer:
    """Main file organization orchestrator."""
    
    def __init__(
        self,
        source_dir: Path,
        output_dir: Path,
        projects_dir: Optional[Path] = None,
        model: str = "llama3.2:3b",
        copy_mode: bool = True,
        dry_run: bool = False,
        transcribe_videos: bool = False,
        whisper_model: str = "base"
    ):
        """
        Initialize the file organizer.
        
        Args:
            source_dir: Directory containing files to organize
            output_dir: Directory where organized files will be placed
            projects_dir: Optional directory containing existing projects
            model: Ollama model to use
            copy_mode: If True, copy files; if False, move files
            dry_run: If True, simulate organization without moving files
            transcribe_videos: If True, transcribe video/audio files
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.projects_dir = Path(projects_dir) if projects_dir else None
        self.copy_mode = copy_mode
        self.dry_run = dry_run
        self.transcribe_videos = transcribe_videos
        
        # Initialize components
        self.categorizer = LLMCategorizer(model=model)
        
        video_transcriber = None
        if transcribe_videos:
            print(f"Initializing Whisper model '{whisper_model}' for video transcription...")
            video_transcriber = VideoTranscriber(
                model_size=whisper_model,
                enable_ocr=True,
                frame_interval=5,  # Extract frame every 5 seconds
                llm_client=self.categorizer.client  # Pass Ollama client for summaries
            )
        
        self.extractor = FileExtractor(
            transcribe_videos=transcribe_videos,
            video_transcriber=video_transcriber
        )
        self.project_manager = ProjectManager(output_dir)
        
        # Validate directories
        if not self.source_dir.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        if self.source_dir == self.output_dir:
            raise ValueError("Source and output directories cannot be the same")
    
    def scan_files(self, recursive: bool = False) -> List[Path]:
        """
        Scan the source directory for files.
        
        Args:
            recursive: If True, scan subdirectories recursively
            
        Returns:
            List of file paths
        """
        files = []
        
        if recursive:
            for item in self.source_dir.rglob('*'):
                if item.is_file() and not self._should_ignore(item):
                    files.append(item)
        else:
            for item in self.source_dir.iterdir():
                if item.is_file() and not self._should_ignore(item):
                    files.append(item)
        
        return files
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if a file should be ignored."""
        ignore_patterns = [
            '.DS_Store',
            'Thumbs.db',
            '.git',
            '__pycache__',
            '.pyc',
            '.swp',
            '~'
        ]
        
        name = path.name
        
        # Check ignore patterns
        for pattern in ignore_patterns:
            if pattern in name:
                return True
        
        # Ignore hidden files (starting with .)
        if name.startswith('.') and name not in ['.gitignore', '.env.example']:
            return True
        
        return False
    
    def organize(self, recursive: bool = False, max_files: Optional[int] = None):
        """
        Run the complete organization process.
        
        Args:
            recursive: If True, scan subdirectories recursively
            max_files: Optional limit on number of files to process
        """
        print("="*60)
        print("File Organization System")
        print("="*60)
        print(f"Source: {self.source_dir}")
        print(f"Output: {self.output_dir}")
        if self.projects_dir:
            print(f"Projects: {self.projects_dir}")
        print(f"Mode: {'COPY' if self.copy_mode else 'MOVE'}")
        if self.dry_run:
            print("DRY RUN: No files will be moved/copied")
        print("="*60)
        print()
        
        # Step 1: Load existing projects
        print("[1/5] Loading existing projects...")
        projects = self.project_manager.load_projects(self.projects_dir)
        print(f"Found {len(projects)} projects")
        for project in projects:
            print(f"  - {project['name']}")
        print()
        
        # Step 2: Scan files
        print("[2/5] Scanning files...")
        files = self.scan_files(recursive=recursive)
        
        if max_files:
            files = files[:max_files]
        
        print(f"Found {len(files)} files to organize")
        print()
        
        if not files:
            print("No files to organize. Exiting.")
            return
        
        # Step 3: Extract file content
        print("[3/5] Extracting file content...")
        file_infos = []
        for i, file_path in enumerate(files, 1):
            print(f"  [{i}/{len(files)}] {file_path.name}")
            file_info = self.extractor.extract(file_path)
            file_infos.append(file_info)
        print()
        
        # Step 4: Categorize files using LLM
        print("[4/5] Categorizing files with local LLM...")
        print("(This may take a while depending on the number of files)")
        categorized = self.categorizer.batch_categorize(file_infos, projects)
        print(f"\nCategorized into {len(categorized)} categories:")
        for category, files_list in sorted(categorized.items()):
            print(f"  - {category}: {len(files_list)} files")
        print()
        
        # Step 5: Organize files
        print("[5/5] Organizing files...")
        stats = self.project_manager.organize_files(
            categorized,
            copy_mode=self.copy_mode,
            dry_run=self.dry_run
        )
        print()
        
        # Create summary report
        if not self.dry_run:
            self.project_manager.create_summary_report(stats)
        
        # Print summary
        print("="*60)
        print("Organization Complete!")
        print("="*60)
        print(f"Total files: {stats['total_files']}")
        print(f"Successfully organized: {stats['organized']}")
        print(f"Errors: {stats['errors']}")
        print(f"\nOrganized files location: {self.output_dir}")
        print("="*60)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Intelligent File Organizer using Local LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Organize files in ~/Downloads to ~/Downloads/Organized
  python main.py ~/Downloads -o ~/Downloads/Organized
  
  # Use existing projects for matching
  python main.py ~/Downloads -o ~/Organized -p ~/Projects
  
  # Move files instead of copying
  python main.py ~/Downloads -o ~/Organized --move
  
  # Dry run to see what would happen
  python main.py ~/Downloads -o ~/Organized --dry-run
  
  # Organize recursively with a different model
  python main.py ~/Documents -o ~/Organized -r --model llama3.2:1b

Requirements:
  1. Install Ollama: https://ollama.ai
  2. Pull a model: ollama pull llama3.2:3b
  3. Install dependencies: pip install -r requirements.txt
        """
    )
    
    parser.add_argument(
        'source',
        type=str,
        help='Source directory containing files to organize'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Output directory for organized files'
    )
    
    parser.add_argument(
        '-p', '--projects',
        type=str,
        help='Directory containing existing projects with README files'
    )
    
    parser.add_argument(
        '-m', '--model',
        type=str,
        default='llama3.2:3b',
        help='Ollama model to use (default: llama3.2:3b)'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Scan subdirectories recursively'
    )
    
    parser.add_argument(
        '--move',
        action='store_true',
        help='Move files instead of copying them'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate organization without actually moving/copying files'
    )
    
    parser.add_argument(
        '--max-files',
        type=int,
        help='Maximum number of files to process (useful for testing)'
    )
    
    parser.add_argument(
        '--transcribe',
        action='store_true',
        help='Transcribe video and audio files to understand content (requires ffmpeg and Whisper)'
    )
    
    parser.add_argument(
        '--whisper-model',
        type=str,
        default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size for transcription (default: base). tiny=fastest, large=most accurate'
    )
    
    args = parser.parse_args()
    
    try:
        organizer = FileOrganizer(
            source_dir=args.source,
            output_dir=args.output,
            projects_dir=args.projects,
            model=args.model,
            copy_mode=not args.move,
            dry_run=args.dry_run,
            transcribe_videos=args.transcribe,
            whisper_model=args.whisper_model
        )
        
        organizer.organize(
            recursive=args.recursive,
            max_files=args.max_files
        )
        
    except KeyboardInterrupt:
        print("\n\nOrganization cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()