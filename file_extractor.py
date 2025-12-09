"""
File content extraction module supporting various file types.
"""
import os
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any

# Import processors
from processors.documents import DocumentProcessor
from processors.text import TextProcessor
from processors.images import ImageProcessor
from processors.archives import ArchiveProcessor


class FileExtractor:
    """Extract content and metadata from various file types."""
    
    def __init__(self, max_text_size: int = 50000, transcribe_videos: bool = False, video_transcriber=None, llm_client=None):
        """
        Initialize the file extractor.
        
        Args:
            max_text_size: Maximum characters to extract from text files
            transcribe_videos: Whether to transcribe video/audio files
            video_transcriber: VideoTranscriber instance (if transcribing)
            llm_client: LLM client for generating summaries
        """
        self.max_text_size = max_text_size
        self.transcribe_videos = transcribe_videos
        self.video_transcriber = video_transcriber
        self.llm_client = llm_client
        
        # Initialize processors
        self.doc_processor = DocumentProcessor(max_text_size)
        self.text_processor = TextProcessor(max_text_size)
        self.image_processor = ImageProcessor()
        self.archive_processor = ArchiveProcessor(max_text_size, extract_text_files=True)
        
        # Give archive processor access to other processors for deep processing
        self.archive_processor.other_processors = {
            'doc': self.doc_processor,
            'text': self.text_processor,
            'image': self.image_processor
        }
        
    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract content and metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file metadata and extracted content
        """
        result = {
            'path': str(file_path),
            'name': file_path.name,
            'extension': file_path.suffix.lower(),
            'size': file_path.stat().st_size,
            'content': '',
            'metadata': {},
            'type': 'unknown'
        }
        
        try:
            # Determine file type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            result['mime_type'] = mime_type or 'unknown'
            
            # Extract content based on file type
            ext = result['extension']
            
            if ext in ['.txt', '.md', '.log', '.cfg', '.conf', '.ini', '.yaml', '.yml', '.toml']:
                result['type'] = 'text'
                result['content'] = self.text_processor.process(file_path)
            elif ext == '.pdf':
                result['type'] = 'pdf'
                result['content'] = self.doc_processor.process_pdf(file_path)
            elif ext in ['.docx', '.doc']:
                result['type'] = 'document'
                result['content'] = self.doc_processor.process_docx(file_path)
            elif ext in ['.json', '.jsonl']:
                result['type'] = 'json'
                result['content'] = self.doc_processor.process_json(file_path)
            elif ext in ['.py', '.js', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.ts', '.tsx', '.jsx']:
                result['type'] = 'code'
                result['content'] = self.text_processor.process(file_path)
            elif ext in ['.html', '.htm', '.xml', '.svg']:
                result['type'] = 'markup'
                result['content'] = self.text_processor.process(file_path)
            elif ext in ['.csv', '.tsv']:
                result['type'] = 'data'
                result['content'] = self.text_processor.process(file_path)
            elif ext in ['.xlsx', '.xls']:
                result['type'] = 'spreadsheet'
                result['content'] = self.doc_processor.process_excel(file_path)
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif']:
                result['type'] = 'image'
                result['metadata'] = self.image_processor.process(file_path)
                result['content'] = self.image_processor.format_metadata(file_path, result['metadata'])
            elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']:
                result['type'] = 'video'
                if self.transcribe_videos and self.video_transcriber:
                    transcription = self.video_transcriber.transcribe_video(file_path)
                    if transcription['success']:
                        # Use summary if available, otherwise use full transcription
                        if transcription.get('summary'):
                            result['content'] = f"Video file: {file_path.name}\n\nSummary: {transcription['summary']}"
                        else:
                            result['content'] = f"Video file: {file_path.name}\n\nTranscription:\n{transcription['text']}"
                        result['transcription'] = transcription['text']
                        result['summary'] = transcription.get('summary', '')
                    else:
                        result['content'] = f"Video file: {file_path.name} (transcription failed)"
                else:
                    result['content'] = f"Video file: {file_path.name}"
            elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']:
                result['type'] = 'audio'
                if self.transcribe_videos and self.video_transcriber:
                    transcription = self.video_transcriber.transcribe_audio(file_path)
                    if transcription['success']:
                        result['content'] = f"Audio file: {file_path.name}\n\nTranscription:\n{transcription['text']}"
                        result['transcription'] = transcription['text']
                    else:
                        result['content'] = f"Audio file: {file_path.name} (transcription failed)"
                else:
                    result['content'] = f"Audio file: {file_path.name}"
            elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z', '.bz2']:
                result['type'] = 'archive'
                result['content'] = self.archive_processor.process(file_path, self.llm_client)
            else:
                # Try to read as text if small enough
                if result['size'] < 1024 * 1024:  # 1MB
                    try:
                        result['content'] = self.text_processor.process(file_path)
                        result['type'] = 'text'
                    except:
                        result['content'] = f"Binary or unknown file: {file_path.name}"
                else:
                    result['content'] = f"Large binary file: {file_path.name}"
                    
        except Exception as e:
            result['content'] = f"Error extracting {file_path.name}: {str(e)}"
            result['error'] = str(e)
            
        return result
