"""
Archive file processor (zip, tar, etc.)
"""
from pathlib import Path
import zipfile
import tarfile
import tempfile
from typing import Optional


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
            
            for name in file_list:
                file_ext = Path(name).suffix.lower()
                if file_ext:
                    file_types[file_ext] = file_types.get(file_ext, 0) + 1
                
                # Track text files for potential extraction
                if self.extract_text_files and file_ext in ['.txt', '.md', '.json', '.csv', '.log', '.py', '.js', '.html', '.css']:
                    text_files.append(name)
            
            # Build description
            description = f"Archive file: {file_path.name}\n"
            description += f"Contains {len(file_list)} files, total size: {total_size / (1024*1024):.2f} MB\n\n"
            
            if file_types:
                description += "File types:\n"
                for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                    description += f"  {ext}: {count} files\n"
            
            # Extract and read text files if enabled
            extracted_content = []
            if self.extract_text_files and text_files:
                description += f"\n📄 Found {len(text_files)} readable text files\n"
                
                # Extract up to 5 text files
                for text_file in text_files[:5]:
                    try:
                        # Skip if file is too large
                        file_info = zf.getinfo(text_file)
                        if file_info.file_size > 100000:  # Skip files > 100KB
                            continue
                        
                        content = zf.read(text_file).decode('utf-8', errors='ignore')
                        if content.strip():
                            extracted_content.append(f"\n--- Content of {text_file} ---\n{content[:1000]}")
                    except:
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
