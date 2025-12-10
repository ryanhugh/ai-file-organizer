"""
Video and audio transcription module using Whisper and OCR.
"""
# Import fix must be first - enables running as both module and script
try:
    from . import _import_fix
except ImportError:
    import _import_fix

import glob
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List

import cv2
import ffmpeg
import whisper

from processors.base import MediaProcessor
from processors.images import ImageProcessor
from processors.summary import SummaryGenerator
from processors.cache import FileCache
from llm_client import get_llm_client


class VideoTranscriber(MediaProcessor):
    """Transcribe audio from video and audio files using Whisper and OCR."""
    
    # Supported video file extensions
    SUPPORTED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v'}
    
    def __init__(self, model_size: str = "base", enable_ocr: bool = True, frame_interval: int = 5):
        """
        Initialize the transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       - tiny: Fastest, least accurate
                       - base: Good balance (recommended)
                       - small: Better accuracy, slower
                       - medium/large: Best accuracy, much slower
            enable_ocr: Whether to extract and OCR video frames
            frame_interval: Extract one frame every N seconds for OCR
        """
        print(f"Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print(f"Whisper model loaded!")
        
        self.enable_ocr = enable_ocr
        self.frame_interval = frame_interval
        self.image_processor = None
        self.summary_generator = SummaryGenerator()
        self.transcription_cache = FileCache('transcription')
        self.video_vision_cache = FileCache('video_vision')  # Cache for LLaVA video analysis
        self.minicpm_cache = FileCache('minicpm_vision')  # Cache for MiniCPM-V analysis
        
        if enable_ocr:
            print(f"Initializing ImageProcessor")
            # Initialize ImageProcessor
            self.image_processor = ImageProcessor()
            print(f"OCR enabled: extracting frames every {frame_interval} seconds")
    
    def _extract_video_frames(self, video_path: Path, frame_interval_seconds: int = 3, max_frames: int = 20) -> list:
        """
        Extract frames from video at regular intervals.
        
        Args:
            video_path: Path to video file
            frame_interval_seconds: Extract 1 frame every N seconds
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of paths to extracted frame images (in temp directory)
        """
        import tempfile
        import numpy as np
        
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if total_frames == 0 or fps == 0:
            cap.release()
            return []
        
        # Calculate number of frames to sample
        num_frames = int((total_frames / fps) / frame_interval_seconds)
        num_frames = max(1, min(num_frames, max_frames))
        
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        frame_paths = []
        
        # Create temp directory for frames
        temp_dir = tempfile.mkdtemp()
        
        for i, idx in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frame_path = Path(temp_dir) / f"frame_{i}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frame_paths.append(str(frame_path))
        
        cap.release()
        
        return frame_paths
        
    def _analyze_video_with_vision_model(self, video_path: Path) -> str:
        """
        Analyze video using LLaVA vision model via Ollama.
        LLaVA doesn't support video directly, so we extract frames.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Description of what's happening in the video
        """
        # Check vision cache first
        file_hash = self.video_vision_cache.get_file_hash(video_path)
        cached_description = self.video_vision_cache.get(file_hash)
        
        if cached_description is not None:
            print(f"  ✓ Using cached LLaVA analysis for {video_path.name}")
            return cached_description
        
        try:
            import shutil
            
            llm_client = get_llm_client()
            
            # Extract frames from video
            frame_paths = self._extract_video_frames(video_path, frame_interval_seconds=3, max_frames=20)
            
            if not frame_paths:
                return ""
            
            try:
                # Analyze frames with LLaVA
                response = llm_client.generate(
                    model='llava:7b',
                    prompt='Describe what is happening in these video frames. Include details about any visible UI elements, text, actions, people, or activities. Describe the overall context and purpose.',
                    images=frame_paths
                )
                
                description = response['response'].strip()
                
                # Cache the result
                self.video_vision_cache.set(file_hash, description)
                
                return description
                
            finally:
                # Clean up temp directory
                if frame_paths:
                    temp_dir = Path(frame_paths[0]).parent
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            print(f"  Warning: LLaVA analysis failed: {str(e)}")
            return ""
    
    def _analyze_video_with_minicpm(self, video_path: Path) -> str:
        """
        Analyze video using MiniCPM-V model via Ollama.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Description of what's happening in the video
        """
        # Check cache first
        file_hash = self.minicpm_cache.get_file_hash(video_path)
        cached_description = self.minicpm_cache.get(file_hash)
        
        if cached_description is not None:
            print(f"  ✓ Using cached MiniCPM-V analysis for {video_path.name}")
            return cached_description
        
        try:
            import shutil
            
            llm_client = get_llm_client()
            
            # Extract frames from video
            frame_paths = self._extract_video_frames(video_path, frame_interval_seconds=3, max_frames=20)
            
            if not frame_paths:
                return ""
            
            try:
                # Analyze frames with MiniCPM-V
                response = llm_client.generate(
                    model='minicpm-v:latest',
                    prompt='Describe what is happening in these video frames. Include details about any visible UI elements, text, actions, people, or activities. Describe the overall context and purpose.',
                    images=frame_paths
                )
                
                description = response['response'].strip()
                
                # Cache the result
                self.minicpm_cache.set(file_hash, description)
                
                return description
                
            finally:
                # Clean up temp directory
                if frame_paths:
                    temp_dir = Path(frame_paths[0]).parent
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            print(f"  Warning: MiniCPM-V analysis failed: {str(e)}")
            return ""
    
    def process(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a video file with transcription, OCR, and summary generation.
        
        Args:
            file_path: Path to video file
            
        Returns:
            Dictionary with success status and summary
        """
        try:
            result = self._transcribe_video(file_path)
            
            if not result['success']:
                return {
                    'success': False,
                    'summary': '',
                    'error': result.get('error', 'Unknown error')
                }
            
            # Build final summary with metadata
            summary = result.get('summary', '')
            if not summary:
                summary = '(No summary generated)'
            
            # Append video info
            video_info = self.get_video_info(file_path)
            if 'duration' in video_info and video_info['duration'] > 0:
                duration_min = int(video_info['duration'] // 60)
                duration_sec = int(video_info['duration'] % 60)
                summary += f"\n\nMetadata: Duration: {duration_min}m {duration_sec}s"
                if 'format' in video_info:
                    summary += f", Format: {video_info['format']}"
            
            return {
                'success': True,
                'summary': summary
            }
            
        except Exception as e:
            print(f"  Error processing {file_path.name}: {str(e)}")
            return {
                'success': False,
                'summary': '',
                'error': str(e)
            }
    
    def _transcribe_video(self, video_path: Path) -> Dict[str, Any]:
        """
        Transcribe audio from a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with transcription and metadata
        """
        try:
            # Check transcription cache first
            file_hash = self.transcription_cache.get_file_hash(video_path)
            cached_result = self.transcription_cache.get(file_hash)
            
            if cached_result is not None:
                print(f"  ✓ Using cached transcription for {video_path.name}")
                # Parse cached JSON result
                cached_data = json.loads(cached_result)
                
                transcription_text = cached_data['audio_transcription']
                ocr_text = cached_data.get('ocr_text', '')
                
                # Print cached transcription
                print(f"\n  📝 Audio Transcription for {video_path.name} (cached):")
                print(f"  {'-' * 70}")
                print(f"  {transcription_text}")
                print(f"  {'-' * 70}\n")
                
                if ocr_text:
                    print(f"  🖼️  OCR Text from Video Frames (cached):")
                    print(f"  {'-' * 70}")
                    print(f"  {ocr_text}")
                    print(f"  {'-' * 70}\n")
                
                # Get vision analyses (may be cached separately)
                vision_description = self._analyze_video_with_vision_model(video_path)
                if vision_description:
                    print(f"  👁️  LLaVA Analysis:")
                    print(f"  {'-' * 70}")
                    print(f"  {vision_description}")
                    print(f"  {'-' * 70}\n")
                
                # its too slow
                minicpm_description = None # self._analyze_video_with_minicpm(video_path)
                # minicpm_description = self._analyze_video_with_minicpm(video_path)
                if minicpm_description:
                    print(f"  🤖 MiniCPM-V Analysis:")
                    print(f"  {'-' * 70}")
                    print(f"  {minicpm_description}")
                    print(f"  {'-' * 70}\n")
                
                # Generate summary (not cached, as it depends on LLM prompt)
                summary = self._generate_summary(video_path.name, transcription_text, ocr_text, vision_description, minicpm_description)
                if summary:
                    print(f"  📋 Summary:")
                    print(f"  {'-' * 70}")
                    print(f"  {summary}")
                    print(f"  {'-' * 70}\n")
                
                combined_text = transcription_text
                if ocr_text:
                    combined_text = f"{transcription_text}\n\n[Screen Text from Video]:\n{ocr_text}"
                if vision_description:
                    combined_text = f"{combined_text}\n\n[LLaVA Visual Description]:\n{vision_description}"
                if minicpm_description:
                    combined_text = f"{combined_text}\n\n[MiniCPM-V Visual Description]:\n{minicpm_description}"
                
                return {
                    'text': combined_text,
                    'summary': summary,
                    'audio_transcription': transcription_text,
                    'ocr_text': ocr_text,
                    'language': cached_data.get('language', 'en'),
                    'segments': cached_data.get('segments', 0),
                    'success': True
                }
            
            # Not in cache - perform transcription
            # Extract audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            # Extract audio using ffmpeg (first N seconds)
            self._extract_audio(video_path, temp_audio_path)
            
            # Transcribe
            print(f"  Transcribing: {video_path.name}...")
            result = self.model.transcribe(
                temp_audio_path,
                fp16=False,  # Use FP32 for better compatibility
                language='en'  # Assume English, can be auto-detected
            )
            
            transcription_text = result['text'].strip()
            
            # Print the full transcription
            print(f"\n  📝 Audio Transcription for {video_path.name}:")
            print(f"  {'-' * 70}")
            print(f"  {transcription_text}")
            print(f"  {'-' * 70}\n")
            
            # Extract and OCR frames if enabled
            ocr_text = ""
            if self.enable_ocr:
                ocr_text = self._extract_and_ocr_frames(video_path)
                if ocr_text:
                    print(f"  🖼️  OCR Text from Video Frames:")
                    print(f"  {'-' * 70}")
                    print(f"  {ocr_text}")
                    print(f"  {'-' * 70}\n")
            
            # Analyze with vision models (in parallel conceptually)
            vision_description = self._analyze_video_with_vision_model(video_path)
            if vision_description:
                print(f"  👁️  LLaVA Analysis:")
                print(f"  {'-' * 70}")
                print(f"  {vision_description}")
                print(f"  {'-' * 70}\n")
            
            minicpm_description = self._analyze_video_with_minicpm(video_path)
            if minicpm_description:
                print(f"  🤖 MiniCPM-V Analysis:")
                print(f"  {'-' * 70}")
                print(f"  {minicpm_description}")
                print(f"  {'-' * 70}\n")
            
            # Combine transcription, OCR text, and vision descriptions
            combined_text = transcription_text
            if ocr_text:
                combined_text = f"{transcription_text}\n\n[Screen Text from Video]:\n{ocr_text}"
            if vision_description:
                combined_text = f"{combined_text}\n\n[LLaVA Visual Description]:\n{vision_description}"
            if minicpm_description:
                combined_text = f"{combined_text}\n\n[MiniCPM-V Visual Description]:\n{minicpm_description}"
            
            # Generate a summary using LLM
            summary = self._generate_summary(video_path.name, transcription_text, ocr_text, vision_description, minicpm_description)
            if summary:
                print(f"  📋 Summary:")
                print(f"  {'-' * 70}")
                print(f"  {summary}")
                print(f"  {'-' * 70}\n")
            
            # Clean up temp file
            try:
                os.unlink(temp_audio_path)
            except:
                pass
            
            # Cache the transcription result (without summary, as it depends on prompt)
            cache_data = {
                'audio_transcription': transcription_text,
                'ocr_text': ocr_text,
                'language': result.get('language', 'en'),
                'segments': len(result.get('segments', []))
            }
            self.transcription_cache.set(file_hash, json.dumps(cache_data))
            
            return {
                'text': combined_text,
                'summary': summary,
                'audio_transcription': transcription_text,
                'ocr_text': ocr_text,
                'language': result.get('language', 'en'),
                'segments': len(result.get('segments', [])),
                'success': True
            }
            
        except Exception as e:
            print(f"  Error transcribing {video_path.name}: {str(e)}")
            return {
                'text': '',
                'error': str(e),
                'success': False
            }
    
    def _extract_audio(self, video_path: Path, output_path: str):
        """Extract audio from video using ffmpeg."""
        try:
            # Use ffmpeg to extract audio
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM audio
                '-ar', '16000',  # 16kHz sample rate (Whisper requirement)
                '-ac', '1',  # Mono
                '-y',  # Overwrite
                output_path
            ]
            
            # Run ffmpeg
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to extract audio: {str(e)}")
        except FileNotFoundError:
            raise Exception(
                "ffmpeg not found. Install with: brew install ffmpeg"
            )
    
    def transcribe_audio(self, audio_path: Path) -> Dict[str, Any]:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with transcription and metadata
        """
        try:
            print(f"  Transcribing: {audio_path.name}...")
            result = self.model.transcribe(
                str(audio_path),
                fp16=False,
                language='en'
            )
            
            transcription_text = result['text'].strip()
            
            # Print the full transcription
            print(f"\n  📝 Transcription for {audio_path.name}:")
            print(f"  {'-' * 70}")
            print(f"  {transcription_text}")
            print(f"  {'-' * 70}\n")
            
            return {
                'text': transcription_text,
                'language': result.get('language', 'en'),
                'segments': len(result.get('segments', [])),
                'success': True
            }
            
        except Exception as e:
            print(f"  Error transcribing {audio_path.name}: {str(e)}")
            return {
                'text': '',
                'error': str(e),
                'success': False
            }
    
    def get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """Get video metadata using ffprobe."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            
            # Extract useful info
            format_info = data.get('format', {})
            duration = float(format_info.get('duration', 0))
            
            return {
                'duration': duration,
                'size': format_info.get('size', 0),
                'format': format_info.get('format_name', 'unknown')
            }
            
        except Exception as e:
            return {
                'duration': 0,
                'error': str(e)
            }
    
    def _extract_and_ocr_frames(self, video_path: Path) -> str:
        """
        Extract frames from video and perform OCR on them using ffmpeg.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Combined OCR text from all frames
        """
        if not self.image_processor:
            return ""
        
        try:
            # Create temporary directory for frames
            with tempfile.TemporaryDirectory() as temp_dir:
                frame_pattern = str(Path(temp_dir) / 'frame_%04d.jpg')
                
                # Extract frames using ffmpeg
                cmd = [
                    'ffmpeg',
                    '-i', str(video_path),
                    '-vf', f'fps=1/{self.frame_interval}',  # 1 frame every N seconds
                    '-q:v', '2',  # High quality
                    '-f', 'image2',
                    frame_pattern
                ]
            
            # Run ffmpeg
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False  # Don't raise on error
            )
            
            if result.returncode != 0:
                print(f"  Warning: ffmpeg frame extraction had issues")
            
            # Read and OCR extracted frames
            frame_files = sorted(glob.glob(f'{temp_dir}/frame_*.jpg'))
            
            print(f"  Found {len(frame_files)} frames to process")
            
            ocr_results = []
            extracted_count = 0
            prev_text_hash = None
            
            for i, frame_file in enumerate(frame_files):
                # Read frame with OpenCV
                frame = cv2.imread(frame_file)
                if frame is None:
                    continue
                
                # Perform OCR on frame using ImageProcessor
                text = self.image_processor.ocr_frame(frame) if self.image_processor else ""
                raw_text_len = len(text) if text else 0
                cleaned_text_len = len(text.strip()) if text else 0
                
                # Debug: show what we're getting
                if i < 2 and raw_text_len > 0:  # Show first 2 frames
                    print(f"    Frame {i+1} raw OCR ({raw_text_len} chars): {text[:200]}")
                
                if cleaned_text_len > 0:
                    print(f"    Frame {i+1}: {raw_text_len} -> {cleaned_text_len} chars after cleaning")
                
                if text.strip():
                    # Simple deduplication based on text similarity
                    text_hash = hash(text[:200])  # Hash first 200 chars
                    if prev_text_hash is None or text_hash != prev_text_hash:
                        ocr_results.append(text.strip())
                        extracted_count += 1
                        prev_text_hash = text_hash
            
            # Clean up temp files
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            print(f"  Extracted and OCR'd {extracted_count} frames with readable text")
            
            # Combine and deduplicate OCR results
            if ocr_results:
                # Remove duplicates while preserving order
                unique_texts = []
                seen = set()
                for text in ocr_results:
                    # Use first 100 chars as key to avoid exact duplicates
                    key = text[:100].lower()
                    if key not in seen:
                        seen.add(key)
                        unique_texts.append(text)
                
                return "\n\n".join(unique_texts)
            
            return ""
            
        except Exception as e:
            print(f"  Error extracting frames: {str(e)}")
            return ""
    
    def _generate_summary(self, filename: str, audio_text: str, ocr_text: str, vision_description: str = "", minicpm_description: str = "") -> str:
        """
        Generate a concise summary of the video content using LLM.
        
        Args:
            filename: Name of the video file
            audio_text: Transcribed audio
            ocr_text: OCR text from video frames
            vision_description: Visual description from LLaVA
            minicpm_description: Visual description from MiniCPM-V
            
        Returns:
            One paragraph summary
        """
        # Build context for the LLM
        context_parts = [f"Video file: {filename}"]
        
        if vision_description:
            context_parts.append(f"\nLLaVA visual analysis:\n{vision_description}")
        
        if minicpm_description:
            context_parts.append(f"\nMiniCPM-V visual analysis:\n{minicpm_description}")
        
        if audio_text:
            context_parts.append(f"\nAudio transcription:\n{audio_text[:1000]}")  # Limit to first 1000 chars
        
        if ocr_text:
            context_parts.append(f"\nText visible on screen:\n{ocr_text[:1000]}")  # Limit to first 1000 chars
        
        context = "\n".join(context_parts)
        
        # Create prompt for summary
        prompt = f"""Based on the following video content, write a single concise paragraph (2-3 sentences) describing what this video is about. Focus on the main topic, what's being shown/discussed, and any key technical details.

{context}

Summary:"""
        
        return self.summary_generator.generate(prompt)


if __name__ == '__main__':
    import sys
    
    # Test video processor
    processor = VideoTranscriber()
    
    # Test with a file path from command line or use default
    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])
    else:
        test_path = Path("/Users/ryanhughes/Desktop/file-organizer-test")
        video_files = list(test_path.glob("*.mov")) + list(test_path.glob("*.mp4"))
        if video_files:
            test_path = video_files[2]
        else:
            print("No video files found in test directory")
            sys.exit(1)
    
    if not test_path.exists():
        print(f"Error: File not found: {test_path}")
        print("Usage: python videos.py <video_file>")
        sys.exit(1)
    
    print(f"Testing VideoTranscriber with: {test_path.name}")
    print("=" * 80)
    
    result = processor.process(test_path)
    
    if result['success']:
        print(f"\n✓ Successfully processed {test_path.name}")
        print(f"\nVideo summary:")
        print("=" * 80)
        print(result['summary'])
        print("=" * 80)
    else:
        print(f"\n✗ Error: {result.get('error', 'Unknown error')}")