"""
Local LLM integration using Ollama for intelligent file categorization.
"""
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class LLMCategorizer:
    """Use local LLM to categorize files intelligently."""
    
    def __init__(self, model: str = "llama3.2:3b"):
        """
        Initialize the LLM categorizer.
        
        Args:
            model: Ollama model to use (default: llama3.2:3b for speed and efficiency)
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama package not installed. Install with: pip install ollama")
            
        self.model = model
        self.client = ollama
        
        # Test if Ollama is running
        try:
            self.client.list()
        except Exception as e:
            raise RuntimeError(
                "Ollama is not running. Please install and start Ollama:\n"
                "1. Install from https://ollama.ai\n"
                "2. Run: ollama pull llama3.2:3b\n"
                f"Error: {str(e)}"
            )
    
    def match_to_project(
        self, 
        file_info: Dict[str, Any], 
        projects: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Match a file to the most relevant project.
        
        Args:
            file_info: Dictionary containing file metadata and content
            projects: List of project dictionaries with 'name' and 'description'
            
        Returns:
            Best matching project dictionary or None if no good match
        """
        if not projects:
            return None
            
        # Build prompt
        prompt = self._build_matching_prompt(file_info, projects)
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    'temperature': 0.1,  # Low temperature for consistent results
                    'num_predict': 100
                }
            )
            
            result_text = response['response'].strip()
            
            # Parse response
            project_match = self._parse_match_response(result_text, projects)
            return project_match
            
        except Exception as e:
            print(f"Error matching file to project: {str(e)}")
            return None
    
    def categorize_file(self, file_info: Dict[str, Any]) -> str:
        """
        Categorize a file into a general category.
        
        Args:
            file_info: Dictionary containing file metadata and content
            
        Returns:
            Category name as a string
        """
        prompt = self._build_categorization_prompt(file_info)
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    'temperature': 0.1,
                    'num_predict': 50
                }
            )
            
            category = response['response'].strip()
            
            # Clean up the response
            category = category.split('\n')[0]  # Take first line
            category = category.strip('.,!?"\' ')
            
            # Sanitize for folder name
            category = self._sanitize_folder_name(category)
            
            return category if category else "Uncategorized"
            
        except Exception as e:
            print(f"Error categorizing file: {str(e)}")
            return "Uncategorized"
    
    def _build_matching_prompt(
        self, 
        file_info: Dict[str, Any], 
        projects: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for project matching."""
        file_desc = f"""
File: {file_info['name']}
Type: {file_info['type']}
Extension: {file_info['extension']}
Content preview: {file_info['content'][:1000]}
"""
        
        projects_desc = "\n".join([
            f"{i+1}. {p['name']}: {p['description'][:500]}"
            for i, p in enumerate(projects)
        ])
        
        prompt = f"""You are a file organization assistant. Match the following file to the most relevant project.

FILE INFORMATION:
{file_desc}

AVAILABLE PROJECTS:
{projects_desc}

Respond with ONLY the project number (1-{len(projects)}) if there's a clear match, or "NONE" if the file doesn't belong to any project.
Consider the file name, type, and content when matching.

Response:"""
        
        return prompt
    
    def _build_categorization_prompt(self, file_info: Dict[str, Any]) -> str:
        """Build prompt for general categorization."""
        file_desc = f"""
File: {file_info['name']}
Type: {file_info['type']}
Extension: {file_info['extension']}
Content preview: {file_info['content'][:800]}
"""
        
        prompt = f"""You are a file organization assistant. Categorize the following file into a descriptive category.

FILE INFORMATION:
{file_desc}

Provide a short, descriptive category name (1-3 words) that best describes this file.
Examples: "Documents", "Images", "Code", "Data Files", "Configuration", "Media", "Archives", etc.

Respond with ONLY the category name, nothing else.

Category:"""
        
        return prompt
    
    def _parse_match_response(
        self, 
        response: str, 
        projects: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Parse the LLM response for project matching."""
        response = response.strip().upper()
        
        # Check for "NONE"
        if "NONE" in response:
            return None
        
        # Try to extract project number
        for i in range(len(projects)):
            if str(i + 1) in response.split()[0]:  # Check first word
                return projects[i]
        
        return None
    
    def _sanitize_folder_name(self, name: str) -> str:
        """Sanitize a string to be a valid folder name."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')
        
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        
        # Limit length
        name = name[:50]
        
        # Ensure it's not empty
        if not name:
            name = "Uncategorized"
            
        return name
    
    def batch_categorize(
        self, 
        files: List[Dict[str, Any]], 
        projects: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize multiple files, matching to projects or general categories.
        
        Args:
            files: List of file information dictionaries
            projects: List of project dictionaries
            
        Returns:
            Dictionary mapping category/project names to lists of files
        """
        categorized = {}
        
        for file_info in files:
            print(f"Processing: {file_info['name']}")
            
            # First try to match to a project
            project = self.match_to_project(file_info, projects)
            
            if project:
                category = project['name']
                file_info['matched_project'] = True
            else:
                # Categorize generally
                category = self.categorize_file(file_info)
                file_info['matched_project'] = False
            
            if category not in categorized:
                categorized[category] = []
            
            categorized[category].append(file_info)
        
        return categorized
