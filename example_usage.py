#!/usr/bin/env python3
"""
Example usage script demonstrating the file organizer capabilities.
"""
from pathlib import Path
from main import FileOrganizer


def create_test_files(test_dir: Path):
    """Create some test files for demonstration."""
    test_dir.mkdir(exist_ok=True)
    
    # Create various test files
    files = {
        'notes.txt': 'Meeting notes from the project planning session.',
        'data.json': '{"name": "test", "value": 123}',
        'script.py': 'print("Hello, World!")\n# Python script',
        'report.md': '# Project Report\n\nThis is a markdown report.',
        'config.txt': 'API_KEY=abc123\nDEBUG=true',
    }
    
    for filename, content in files.items():
        file_path = test_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
    
    print(f"Created {len(files)} test files in {test_dir}")


def create_test_projects(projects_dir: Path):
    """Create example project folders with READMEs."""
    projects_dir.mkdir(exist_ok=True)
    
    projects = {
        'WebApp': """# WebApp Project

A web application built with React and Node.js.
This project includes frontend and backend code,
configuration files, and documentation.
""",
        'DataAnalysis': """# Data Analysis Project

Python-based data analysis using pandas and matplotlib.
Includes Jupyter notebooks, CSV data files, and
analysis scripts for processing sales data.
""",
        'Documentation': """# Documentation Project

Technical documentation and guides.
Contains markdown files, diagrams, and
reference materials for various projects.
"""
    }
    
    for project_name, readme_content in projects.items():
        project_dir = projects_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        readme_path = project_dir / 'README.md'
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    
    print(f"Created {len(projects)} test projects in {projects_dir}")


def example_basic_usage():
    """Example 1: Basic file organization without projects."""
    print("\n" + "="*60)
    print("Example 1: Basic Organization")
    print("="*60)
    
    # Setup
    test_dir = Path('./test_files')
    output_dir = Path('./test_output/basic')
    
    create_test_files(test_dir)
    
    # Run organizer
    organizer = FileOrganizer(
        source_dir=test_dir,
        output_dir=output_dir,
        copy_mode=True,
        dry_run=True  # Dry run for demonstration
    )
    
    organizer.organize()
    
    print("\nTo actually organize files, remove the dry_run=True parameter")


def example_with_projects():
    """Example 2: Organization with project matching."""
    print("\n" + "="*60)
    print("Example 2: Organization with Project Matching")
    print("="*60)
    
    # Setup
    test_dir = Path('./test_files')
    projects_dir = Path('./test_projects')
    output_dir = Path('./test_output/with_projects')
    
    create_test_files(test_dir)
    create_test_projects(projects_dir)
    
    # Run organizer
    organizer = FileOrganizer(
        source_dir=test_dir,
        output_dir=output_dir,
        projects_dir=projects_dir,
        copy_mode=True,
        dry_run=True
    )
    
    organizer.organize()
    
    print("\nFiles will be matched to projects based on content similarity")


def example_with_custom_model():
    """Example 3: Using a different LLM model."""
    print("\n" + "="*60)
    print("Example 3: Custom Model")
    print("="*60)
    
    test_dir = Path('./test_files')
    output_dir = Path('./test_output/custom_model')
    
    # Use a smaller, faster model
    organizer = FileOrganizer(
        source_dir=test_dir,
        output_dir=output_dir,
        model='llama3.2:1b',  # Faster model
        copy_mode=True,
        dry_run=True
    )
    
    organizer.organize(max_files=5)  # Limit to 5 files for demo


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("File Organizer - Example Usage")
    print("="*60)
    print("\nThis script demonstrates various ways to use the file organizer.")
    print("All examples run in DRY RUN mode (no files actually moved).")
    
    try:
        # Example 1: Basic usage
        example_basic_usage()
        
        # Example 2: With projects
        example_with_projects()
        
        # Example 3: Custom model
        example_with_custom_model()
        
        print("\n" + "="*60)
        print("Examples Complete!")
        print("="*60)
        print("\nTo run the actual organizer, use:")
        print("  python main.py /path/to/folder -o /path/to/output")
        
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        print("\nMake sure:")
        print("  1. Ollama is installed and running (ollama serve)")
        print("  2. Model is downloaded (ollama pull llama3.2:3b)")
        print("  3. Dependencies are installed (pip install -r requirements.txt)")


if __name__ == '__main__':
    main()
