"""
Archive file processor (zip, tar, etc.)
"""

try:
    from . import _import_fix
except ImportError:
    import _import_fix

from pathlib import Path
import zipfile
import tarfile
import tempfile
from typing import Optional, Dict, Any


class ArchiveProcessor:
    """Process archive files."""
    
    def __init__(self, max_text_size: int = 50000, extract_text_files: bool = True):
        """
        Initialize archive processor.
        
        Args:
            max_text_size: Maximum characters to extract from text files
            extract_text_files: Whether to extract and read text files inside archives
        """
        self.max_text_size = max_text_size
        self.extract_text_files = extract_text_files
        self.other_processors = None  # Will be set by FileExtractor
    
    def process(self, file_path: Path, llm_client=None) -> str:
        """
        Extract information about archive contents.
        
        Args:
            file_path: Path to archive file
            llm_client: Optional LLM client for generating summaries
            
        Returns:
            Description of archive contents
        """
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.zip':
                return self._process_zip(file_path, llm_client)
            elif ext in ['.tar', '.gz', '.bz2']:
                return self._process_tar(file_path, llm_client)
            else:
                return f"Archive file: {file_path.name} (format not fully supported)"
        except Exception as e:
            return f"Archive file: {file_path.name}\nError reading archive: {str(e)}"
    
    def _process_zip(self, file_path: Path, llm_client=None) -> str:
        """Process ZIP archive."""
        with zipfile.ZipFile(file_path, 'r') as zf:
            file_list = zf.namelist()
            total_size = sum(info.file_size for info in zf.filelist)
            
            # Categorize files by type
            file_types = {}
            text_files = []
            has_folders = False
            has_nested_archives = False
            actual_files = []  # Files excluding system files
            
            for name in file_list:
                # Skip macOS system files
                if '/__MACOSX/' in name or name.startswith('__MACOSX/') or '._' in name:
                    continue
                
                # Check if it's a directory
                if name.endswith('/'):
                    has_folders = True
                    continue
                
                actual_files.append(name)
                file_ext = Path(name).suffix.lower()
                
                if file_ext:
                    file_types[file_ext] = file_types.get(file_ext, 0) + 1
                
                # Check for nested archives
                if file_ext in ['.zip', '.tar', '.gz', '.rar', '.7z', '.bz2']:
                    has_nested_archives = True
                
                # Track text files for potential extraction
                if self.extract_text_files and file_ext in ['.txt', '.md', '.json', '.csv', '.log', '.py', '.js', '.html', '.css']:
                    text_files.append(name)
            
            # Decide whether to deeply process files
            should_deep_process = self._should_deep_process(
                len(actual_files), has_folders, has_nested_archives, file_types, llm_client
            )

            print(f"Should deep process: {should_deep_process}, {file_types}")
            
            # Build description
            description = f"Archive file: {file_path.name}\n"
            description += f"Contains {len(file_list)} files, total size: {total_size / (1024*1024):.2f} MB\n\n"
            
            if file_types:
                description += "File types:\n"
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                    description += f"  {ext}: {count} files\n"
            
            # Process files if decision says we should
            extracted_content = []
            if should_deep_process and self.other_processors:
                description += f"\n🔍 Deep processing {len(actual_files)} files...\n"
                
                # Extract to temp directory and process each file
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    for file_name in actual_files[:10]:  # Limit to 10 files
                        try:
                            file_info = zf.getinfo(file_name)
                            if file_info.file_size > 10 * 1024 * 1024:  # Skip files > 10MB
                                continue
                            
                            # Extract file
                            extracted_path = Path(temp_dir) / Path(file_name).name
                            with open(extracted_path, 'wb') as f:
                                f.write(zf.read(file_name))
                            
                            # Process based on file type using the unified process() method
                            file_ext = extracted_path.suffix.lower()
                            result = None
                            
                            # Determine which processor to use
                            if file_ext in self.other_processors['text'].SUPPORTED_EXTENSIONS:
                                result = self.other_processors['text'].process(extracted_path)
                            elif file_ext in self.other_processors['document'].SUPPORTED_EXTENSIONS:
                                result = self.other_processors['document'].process(extracted_path)
                            elif file_ext in self.other_processors['image'].SUPPORTED_EXTENSIONS:
                                result = self.other_processors['image'].process(extracted_path)
                            elif file_ext in self.other_processors['video'].SUPPORTED_EXTENSIONS:
                                result = self.other_processors['video'].process(extracted_path)
                            
                            # Extract summary from result
                            if result and result.get('success'):
                                content = result['summary']
                                if content and len(content.strip()) > 0:
                                    # Truncate long content but keep full summary for images/videos
                                    preview = content[:1000] if len(content) > 1000 else content
                                    extracted_content.append(f"\n--- {file_name} ---\n{preview}")
                        except Exception as e:
                            print(f"Error processing {file_name}: {e}")
                            pass
                
                if extracted_content:
                    description += "\nProcessed file contents:\n"
                    description += "\n".join(extracted_content)
            elif self.extract_text_files and text_files:
                # Fallback to simple text extraction
                description += f"\n📄 Found {len(text_files)} readable text files\n"
                
                for text_file in text_files[:5]:
                    try:
                        file_info = zf.getinfo(text_file)
                        if file_info.file_size > 100000:  # Skip files > 100KB
                            continue
                        
                        content = zf.read(text_file).decode('utf-8', errors='ignore')
                        if content.strip():
                            extracted_content.append(f"\n--- Content of {text_file} ---\n{content[:1000]}")
                    except Exception as e:
                        print (e)
                        pass
                
                if extracted_content:
                    description += "\nExtracted text file contents:\n"
                    description += "\n".join(extracted_content)
            
            # List some file names (first 20)
            if file_list:
                description += f"\n\nSample files:\n"
                for name in file_list[:20]:
                    description += f"  - {name}\n"
                if len(file_list) > 20:
                    description += f"  ... and {len(file_list) - 20} more files\n"
            
            # Generate summary if LLM is available
            if llm_client:
                summary = self._generate_summary(file_path.name, description, llm_client)
                if summary:
                    description = f"Archive file: {file_path.name}\n\n📋 Summary: {summary}\n\n" + description
            
            return description
    
    def _process_tar(self, file_path: Path, llm_client=None) -> str:
        """Process TAR archive."""
        with tarfile.open(file_path, 'r:*') as tf:
            members = tf.getmembers()
            total_size = sum(m.size for m in members)
            
            # Categorize files by type
            file_types = {}
            text_files = []
            
            for member in members:
                if member.isfile():
                    file_ext = Path(member.name).suffix.lower()
                    if file_ext:
                        file_types[file_ext] = file_types.get(file_ext, 0) + 1
                    
                    # Track text files
                    if self.extract_text_files and file_ext in ['.txt', '.md', '.json', '.csv', '.log', '.py', '.js', '.html', '.css']:
                        text_files.append(member)
            
            # Build description
            description = f"Archive file: {file_path.name}\n"
            description += f"Contains {len(members)} items, total size: {total_size / (1024*1024):.2f} MB\n\n"
            
            if file_types:
                description += "File types:\n"
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                    description += f"  {ext}: {count} files\n"
            
            # Extract and read text files if enabled
            extracted_content = []
            if self.extract_text_files and text_files:
                description += f"\n📄 Found {len(text_files)} readable text files\n"
                
                for member in text_files[:5]:
                    try:
                        if member.size > 100000:  # Skip files > 100KB
                            continue
                        
                        f = tf.extractfile(member)
                        if f:
                            content = f.read().decode('utf-8', errors='ignore')
                            if content.strip():
                                extracted_content.append(f"\n--- Content of {member.name} ---\n{content[:1000]}")
                    except:
                        pass
                
                if extracted_content:
                    description += "\nExtracted text file contents:\n"
                    description += "\n".join(extracted_content)
            
            # List some file names (first 20)
            file_members = [m for m in members if m.isfile()]
            if file_members:
                description += f"\n\nSample files:\n"
                for member in file_members[:20]:
                    description += f"  - {member.name}\n"
                if len(file_members) > 20:
                    description += f"  ... and {len(file_members) - 20} more files\n"
            
            # Generate summary if LLM is available
            if llm_client:
                summary = self._generate_summary(file_path.name, description, llm_client)
                if summary:
                    description = f"Archive file: {file_path.name}\n\n📋 Summary: {summary}\n\n" + description
            
            return description
    
    def _should_deep_process(self, num_files: int, has_folders: bool, has_nested_archives: bool, 
                             file_types: Dict[str, int], llm_client) -> bool:
        """
        Decide whether to deeply process files in the archive.
        
        Rules:
        1. If < 5 files, no folders, no nested archives -> always process
        2. If simple structure (few files, common types) -> process
        3. Otherwise, ask LLM to decide
        """
        # Rule 1: Simple case - few files, flat structure, no nested archives
        if num_files < 5 and not has_folders and not has_nested_archives:
            return True
        
        # Rule 2: Small number of processable files
        processable_types = {'.txt', '.md', '.json', '.csv', '.log', '.py', '.js', '.html', '.css', '.pdf', '.docx', '.doc'}
        processable_count = sum(count for ext, count in file_types.items() if ext in processable_types)
        
        if processable_count > 0 and processable_count <= 5 and not has_nested_archives:
            return True
        
        # Rule 3: Large or complex archive - ask LLM
        if llm_client and num_files > 5:
            try:
                file_types_str = ", ".join([f"{count} {ext} files" for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:5]])
                
                prompt = f"""You are analyzing an archive file to decide if we should extract and process its contents.

Archive info:
- Number of files: {num_files}
- Has subdirectories: {has_folders}
- Has nested archives: {has_nested_archives}
- File types: {file_types_str}

Should we extract and deeply process the files inside this archive? Answer with just "yes" or "no" and a brief reason.

Consider:
- If it's a small backup or export with a few documents/text files -> yes
- If it's a large codebase or complex project structure -> no
- If it has many nested archives or binary files -> no
- If it's clearly documentation or data files -> yes

Answer:"""
                
                response = llm_client.generate(
                    model='llama3.2:3b',
                    prompt=prompt
                )
                
                answer = response['response'].strip().lower()
                return 'yes' in answer[:20]  # Check first 20 chars for "yes"
            except:
                pass
        
        # Default: don't deep process large/complex archives
        return False
    
    def _generate_summary(self, filename: str, content: str, llm_client) -> Optional[str]:
        """Generate a summary of the archive using LLM."""
        try:
            prompt = f"""Based on the following archive file information, write a single concise paragraph (2-3 sentences) describing what this archive contains and what it might be used for.

{content[:2000]}

Summary:"""
            
            response = llm_client.generate(
                model='llama3.2:3b',
                prompt=prompt
            )
            
            return response['response'].strip()
        except Exception as e:
            return None

if __name__ == '__main__':
    # Test archive processor
    import sys
    from pathlib import Path
    from llm_client import get_llm_client
    
    # Initialize processor
    processor = ArchiveProcessor()
    
    # Initialize other processors for deep processing
    from processors.images import ImageProcessor
    from processors.videos import VideoTranscriber
    from processors.documents import DocumentProcessor
    from processors.text import TextProcessor
    
    processor.other_processors = {
        'image': ImageProcessor(),
        'video': VideoTranscriber(model_size="base", enable_ocr=True, frame_interval=5),
        'document': DocumentProcessor(),
        'text': TextProcessor()
    }
    
    # Test with a file path from command line or use default
    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])
    else:
        test_path = Path("/Users/ryanhughes/Desktop/file-organizer-test/a zip file.zip")
    
    if not test_path.exists():
        print(f"Error: File not found: {test_path}")
        print("Usage: python archives.py <archive_file>")
        sys.exit(1)
    
    print(f"Testing ArchiveProcessor with: {test_path.name}")
    print("=" * 80)
    
    result = processor.process(test_path, get_llm_client())
    print(result)
