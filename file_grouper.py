"""
Group files by semantic similarity using embeddings.
"""
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN
from collections import defaultdict
import json

from llm_client import get_llm_client


class FileGrouper:
    """Group files based on semantic similarity of their descriptions."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the file grouper.
        
        Args:
            model_name: Sentence transformer model to use
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✓ Embedding model loaded")
    
    def group_files(self, file_results: List[Dict[str, Any]], min_cluster_size: int = 2) -> Dict[str, List[Dict]]:
        """
        Group files by semantic similarity.
        
        Args:
            file_results: List of dicts with 'filename' and 'summary' keys
            min_cluster_size: Minimum files to form a cluster
            
        Returns:
            Dictionary mapping group names to lists of files
        """
        if not file_results:
            return {}
        
        # Extract summaries
        summaries = [r['summary'] for r in file_results]
        filenames = [r['filename'] for r in file_results]
        
        print(f"\nGenerating embeddings for {len(summaries)} files...")
        embeddings = self.model.encode(summaries, show_progress_bar=True)
        
        print(f"Clustering files...")
        # Use HDBSCAN for automatic cluster discovery
        # Lower min_cluster_size for more fine-grained groups
        clusterer = HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=1,  # More sensitive to small groups
            metric='euclidean',
            cluster_selection_epsilon=0.3  # Allow tighter clusters
        )
        labels = clusterer.fit_predict(embeddings)
        
        # Group files by cluster
        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            clusters[label].append({
                'filename': filenames[idx],
                'summary': summaries[idx],
                'embedding': embeddings[idx]
            })
        
        print(f"✓ Found {len([l for l in clusters.keys() if l != -1])} clusters")
        
        # Generate descriptive names for each cluster using LLM
        named_groups = {}
        llm_client = get_llm_client()
        
        for cluster_id, files in clusters.items():
            if cluster_id == -1:
                # Unclustered files
                group_name = "Uncategorized"
            else:
                # Generate a descriptive name based on the summaries
                group_name = self._generate_group_name(files, llm_client)
            
            named_groups[group_name] = files
        
        return named_groups
    
    def _generate_group_name(self, files: List[Dict], llm_client) -> str:
        """
        Generate a descriptive name for a group of files using LLM.
        
        Args:
            files: List of file dicts with summaries
            llm_client: Ollama client
            
        Returns:
            Descriptive group name
        """
        # Take up to 5 representative summaries
        sample_summaries = [f['summary'][:200] for f in files[:5]]
        
        prompt = f"""Based on these file descriptions, suggest a SPECIFIC, DESCRIPTIVE folder name (10 words max).

Be specific - if they mention a company/client name/project name, use that.
If they're about a specific topic (like "Python tutorials", "Health dashboard"), use that.
Avoid generic names like "Screenshots" or "Documents".

Files:
{chr(10).join(f'- {s}' for s in sample_summaries)}

Folder name (just the name, nothing else):"""
        
        try:
            response = llm_client.generate(
                model='llama3.2:3b',
                prompt=prompt
            )
            
            # Clean up the response
            name = response['response'].strip()
            # Remove quotes if present
            name = name.strip('"\'')
            # Limit length
            if len(name) > 50:
                name = name[:50]
            
            return name
            
        except Exception as e:
            print(f"  Warning: Could not generate group name: {e}")
            return f"Group_{len(files)}_files"
    
    def save_groups(self, groups: Dict[str, List[Dict]], output_file: Path):
        """
        Save grouped files to a JSON file.
        
        Args:
            groups: Dictionary of group names to file lists
            output_file: Path to output JSON file
        """
        # Remove embeddings before saving (too large)
        groups_to_save = {}
        for group_name, files in groups.items():
            groups_to_save[group_name] = [
                {'filename': f['filename'], 'summary': f['summary']}
                for f in files
            ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(groups_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved groups to: {output_file}")
    
    def print_groups(self, groups: Dict[str, List[Dict]]):
        """Print a summary of the groups."""
        print(f"\n{'='*80}")
        print("FILE GROUPS")
        print(f"{'='*80}\n")
        
        # Sort by group size (largest first)
        sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        for group_name, files in sorted_groups:
            print(f"📁 {group_name} ({len(files)} files)")
            for file_info in files[:3]:  # Show first 3 files
                print(f"   - {file_info['filename']}")
            if len(files) > 3:
                print(f"   ... and {len(files) - 3} more")
            print()
