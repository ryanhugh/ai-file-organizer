"""
Video and audio transcription module using Whisper and OCR.
"""
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

from .images import ImageProcessor
from .summary import SummaryGenerator


class VideoTranscriber:
    """Transcribe audio from video and audio files using Whisper and OCR."""
    
    def __init__(self, model_size: str = "base", enable_ocr: bool = True, frame_interval: int = 5, llm_client=None):
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
            llm_client: Ollama client for generating summaries
        """
        print(f"Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print(f"Whisper model loaded!")
        
        self.enable_ocr = enable_ocr
        self.frame_interval = frame_interval
        self.image_processor = None
        self.llm_client = llm_client
        self.summary_generator = SummaryGenerator(llm_client=llm_client)
        
        if enable_ocr:
            print(f"Initializing ImageProcessor")
            # Initialize ImageProcessor
            self.image_processor = ImageProcessor()
            print(f"OCR enabled: extracting frames every {frame_interval} seconds")
        
    def transcribe_video(self, video_path: Path, max_duration: int = 300) -> Dict[str, Any]:
        """
        Transcribe audio from a video file.
        
        Args:
            video_path: Path to video file
            max_duration: Maximum duration to transcribe in seconds (default: 5 minutes)
            
        Returns:
            Dictionary with transcription and metadata
        """
        try:
            # Extract audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
            
            # Extract audio using ffmpeg (first N seconds)
            self._extract_audio(video_path, temp_audio_path, max_duration)
            
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
                ocr_text = self._extract_and_ocr_frames(video_path, max_duration)
                if ocr_text:
                    print(f"  🖼️  OCR Text from Video Frames:")
                    print(f"  {'-' * 70}")
                    print(f"  {ocr_text}")
                    print(f"  {'-' * 70}\n")
            
            # Combine transcription and OCR text
            combined_text = transcription_text
            if ocr_text:
                combined_text = f"{transcription_text}\n\n[Screen Text from Video]:\n{ocr_text}"
            
            # Generate a summary using LLM
            summary = self._generate_summary(video_path.name, transcription_text, ocr_text)
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
    
    def _extract_audio(self, video_path: Path, output_path: str, max_duration: int):
        """Extract audio from video using ffmpeg."""
        try:
            # Use ffmpeg to extract audio
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-t', str(max_duration),  # Limit duration
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
    
    def _extract_and_ocr_frames(self, video_path: Path, max_duration: int = 300) -> str:
        """
        Extract frames from video and perform OCR on them using ffmpeg.
        
        Args:
            video_path: Path to video file
            max_duration: Maximum duration to process in seconds
            
        Returns:
            Combined OCR text from all frames
        """
        if not self.image_processor:
            return ""
        
        try:
            print(f"  Extracting frames for OCR...")
            
            # Create temp directory for frames
            temp_dir = tempfile.mkdtemp()
            
            # Use ffmpeg to extract frames at intervals
            # Extract 1 frame every N seconds
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-t', str(max_duration),  # Limit duration
                '-vf', f'fps=1/{self.frame_interval}',  # 1 frame every N seconds
                '-q:v', '2',  # High quality
                '-f', 'image2',
                f'{temp_dir}/frame_%04d.jpg'
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
    
    def _generate_summary(self, filename: str, audio_text: str, ocr_text: str) -> str:
        """
        Generate a concise summary of the video content using LLM.
        
        Args:
            filename: Name of the video file
            audio_text: Transcribed audio
            ocr_text: OCR text from video frames
            
        Returns:
            One paragraph summary
        """
        # Build context for the LLM
        context_parts = [f"Video file: {filename}"]
        
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
