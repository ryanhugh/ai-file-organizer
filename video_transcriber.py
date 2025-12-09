"""
Video and audio transcription module using Whisper and OCR.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class VideoTranscriber:
    """Transcribe audio from video and audio files using Whisper and OCR."""
    
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
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "Whisper not installed. Install with: pip install openai-whisper\n"
                "Also requires ffmpeg: brew install ffmpeg"
            )
        
        print(f"Loading Whisper model '{model_size}'...")
        self.model = whisper.load_model(model_size)
        print(f"Whisper model loaded!")
        
        self.enable_ocr = enable_ocr
        self.frame_interval = frame_interval
        
        if enable_ocr:
            if not CV2_AVAILABLE:
                print("Warning: OpenCV not available. Frame extraction disabled.")
                self.enable_ocr = False
            elif not OCR_AVAILABLE:
                print("Warning: pytesseract not available. OCR disabled.")
                self.enable_ocr = False
            else:
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
            
            # Clean up temp file
            try:
                os.unlink(temp_audio_path)
            except:
                pass
            
            return {
                'text': combined_text,
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
            
            import json
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
        Extract frames from video and perform OCR on them.
        
        Args:
            video_path: Path to video file
            max_duration: Maximum duration to process in seconds
            
        Returns:
            Combined OCR text from all frames
        """
        if not CV2_AVAILABLE or not OCR_AVAILABLE:
            return ""
        
        try:
            print(f"  Extracting frames for OCR...")
            
            # Open video
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return ""
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Limit duration
            process_duration = min(duration, max_duration)
            
            # Calculate frame interval
            frame_interval = int(fps * self.frame_interval)  # Extract every N seconds
            
            ocr_results = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Check if we've exceeded max duration
                current_time = frame_count / fps
                if current_time > process_duration:
                    break
                
                # Extract frame at intervals
                if frame_count % frame_interval == 0:
                    # Perform OCR on frame
                    text = self._ocr_frame(frame)
                    if text.strip():
                        ocr_results.append(text.strip())
                        extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            
            print(f"  Extracted and OCR'd {extracted_count} frames")
            
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
    
    def _ocr_frame(self, frame) -> str:
        """
        Perform OCR on a single video frame with preprocessing.
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            Extracted text
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing to improve OCR quality
            # 1. Increase contrast
            gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
            
            # 2. Denoise
            gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # 3. Apply adaptive thresholding to handle varying lighting
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Convert to PIL Image
            pil_image = Image.fromarray(binary)
            
            # Perform OCR with better configuration
            # PSM 6 = Assume a single uniform block of text
            # PSM 11 = Sparse text. Find as much text as possible in no particular order
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%&*()_+-=[]{}:;"\'/\| '
            text = pytesseract.image_to_string(pil_image, config=custom_config)
            
            # Clean up the text
            text = self._clean_ocr_text(text)
            
            return text
            
        except Exception as e:
            return ""
    
    def _clean_ocr_text(self, text: str) -> str:
        """
        Clean up OCR output to remove garbage.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that are mostly non-alphanumeric (likely garbage)
            alphanumeric_count = sum(c.isalnum() for c in line)
            if len(line) > 0 and alphanumeric_count / len(line) < 0.3:
                continue
            
            # Skip very short lines (likely noise)
            if len(line) < 3:
                continue
            
            # Skip lines with too many repeated characters (likely artifacts)
            if any(line.count(char) > len(line) * 0.5 for char in set(line)):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
