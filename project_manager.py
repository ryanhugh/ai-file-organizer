"""
Project management and file organization logic.
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional


class ProjectManager:
    """Manage projects and organize files into project folders."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize the project manager.
        
        Args:
            output_dir: Directory where organized files will be placed
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_projects(self, projects_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Load existing projects from a projects directory.
        
        Args:
            projects_dir: Directory containing project folders with README files
            
        Returns:
            List of project dictionaries with name and description
        """
        projects = []
        
        if not projects_dir or not projects_dir.exists():
            return projects
        
        # Scan for project folders
        for item in projects_dir.iterdir():
            if item.is_dir():
                # Look for README file
                readme_files = list(item.glob('README*')) + list(item.glob('readme*'))
                
                if readme_files:
                    readme_path = readme_files[0]
                    try:
                        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                            description = f.read(5000)  # Read first 5000 chars
                        
                        projects.append({
                            'name': item.name,
                            'path': item,
                            'readme_path': readme_path,
                            'description': description
                        })
                    except Exception as e:
                        print(f"Error reading README for {item.name}: {str(e)}")
        
        return projects
    
    def organize_files(
        self, 
        categorized_files: Dict[str, List[Dict[str, Any]]],
        copy_mode: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Organize files into the output directory structure.
        
        Args:
            categorized_files: Dictionary mapping categories to file lists
            copy_mode: If True, copy files; if False, move files
            dry_run: If True, don't actually move/copy files
            
        Returns:
            Dictionary with organization statistics
        """
        stats = {
            'total_files': 0,
            'organized': 0,
            'errors': 0,
            'categories': {}
        }
        
        for category, files in categorized_files.items():
            category_dir = self.output_dir / category
            files_dir = category_dir / 'files'
            
            stats['categories'][category] = {
                'count': len(files),
                'path': str(category_dir)
            }
            
            if not dry_run:
                category_dir.mkdir(parents=True, exist_ok=True)
                files_dir.mkdir(parents=True, exist_ok=True)
                
                # Create a README for this category
                self._create_category_readme(category_dir, category, files)
            
            # Organize each file
            for file_info in files:
                stats['total_files'] += 1
                
                try:
                    source_path = Path(file_info['path'])
                    dest_path = files_dir / source_path.name
                    
                    # Handle name conflicts
                    if dest_path.exists():
                        dest_path = self._get_unique_path(dest_path)
                    
                    if not dry_run:
                        if copy_mode:
                            shutil.copy2(source_path, dest_path)
                        else:
                            shutil.move(str(source_path), str(dest_path))
                    
                    stats['organized'] += 1
                    
                    if dry_run:
                        print(f"  [DRY RUN] Would organize: {source_path.name} -> {category}/files/")
                    
                except Exception as e:
                    stats['errors'] += 1
                    print(f"Error organizing {file_info['name']}: {str(e)}")
        
        return stats
    
    def _create_category_readme(
        self, 
        category_dir: Path, 
        category_name: str, 
        files: List[Dict[str, Any]]
    ):
        """Create a README file for a category."""
        readme_path = category_dir / 'README.md'
        
        # Check if this is a matched project
        is_project = files[0].get('matched_project', False) if files else False
        
        if is_project:
            # Don't overwrite existing project READMEs
            if readme_path.exists():
                return
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {category_name}\n\n")
            
            if is_project:
                f.write("This is a project folder. Files have been organized here based on their relevance to this project.\n\n")
            else:
                f.write(f"This folder contains files categorized as: **{category_name}**\n\n")
            
            f.write(f"## Files ({len(files)})\n\n")
            
            # Group by file type
            by_type = {}
            for file_info in files:
                file_type = file_info.get('type', 'unknown')
                if file_type not in by_type:
                    by_type[file_type] = []
                by_type[file_type].append(file_info)
            
            for file_type, type_files in sorted(by_type.items()):
                f.write(f"### {file_type.title()} Files\n\n")
                for file_info in sorted(type_files, key=lambda x: x['name']):
                    f.write(f"- `{file_info['name']}`")
                    if file_info.get('size', 0) > 0:
                        size_kb = file_info['size'] / 1024
                        if size_kb > 1024:
                            f.write(f" ({size_kb/1024:.1f} MB)")
                        else:
                            f.write(f" ({size_kb:.1f} KB)")
                    f.write("\n")
                f.write("\n")
    
    def _get_unique_path(self, path: Path) -> Path:
        """Generate a unique file path if the original exists."""
        if not path.exists():
            return path
        
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def create_summary_report(
        self, 
        stats: Dict[str, Any], 
        output_path: Optional[Path] = None
    ):
        """Create a summary report of the organization process."""
        if output_path is None:
            output_path = self.output_dir / 'ORGANIZATION_REPORT.md'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# File Organization Report\n\n")
            f.write(f"**Total Files Processed:** {stats['total_files']}\n")
            f.write(f"**Successfully Organized:** {stats['organized']}\n")
            f.write(f"**Errors:** {stats['errors']}\n\n")
            
            f.write("## Categories\n\n")
            
            for category, info in sorted(stats['categories'].items()):
                f.write(f"### {category}\n")
                f.write(f"- **Files:** {info['count']}\n")
                f.write(f"- **Location:** `{info['path']}`\n\n")
        
        print(f"\nSummary report created: {output_path}")
