# File Grouping by Semantic Similarity

## Overview

The file grouper uses **sentence transformers** to create embeddings of file descriptions, then clusters them using **HDBSCAN** to discover natural groupings. An LLM then generates descriptive names for each group.

## How It Works

1. **Process files** → Generate summaries for each file
2. **Vectorize** → Convert summaries to 384-dimensional embeddings
3. **Cluster** → Use HDBSCAN to find similar files
4. **Name groups** → LLM generates specific, descriptive folder names

## Key Features

✅ **Specific grouping** - Finds fine-grained topics like "Rupa Health Dashboard", "Ecojoy Client Work"  
✅ **Automatic discovery** - No need to specify number of groups  
✅ **Fully local** - Embeddings run on your machine  
✅ **Smart naming** - LLM generates descriptive folder names based on content

## Usage

```bash
# Process files AND group them
python process_desktop_media.py --group

# Or with custom process count
python process_desktop_media.py -p 16 --group
```

## Output

### 1. Summary Log
`media_summaries_YYYYMMDD_HHMMSS.txt` - All file summaries

### 2. Groups JSON
`file_groups_YYYYMMDD_HHMMSS.json` - Clustered files with structure:
```json
{
  "Rupa Health Dashboard": [
    {
      "filename": "screenshot1.png",
      "summary": "Screenshot showing Rupa Health dashboard..."
    }
  ],
  "Python Code Examples": [
    {
      "filename": "example.py",
      "summary": "Python script demonstrating..."
    }
  ]
}
```

### 3. Console Output
```
📁 Rupa Health Dashboard (5 files)
   - screenshot1.png
   - screenshot2.png
   - dashboard_mockup.png
   ... and 2 more

📁 Ecojoy Client Work (3 files)
   - ecojoy_proposal.pdf
   - ecojoy_wireframes.png
   - ecojoy_notes.txt
```

## Configuration

### Clustering Parameters

In `file_grouper.py`:
- `min_cluster_size=2` - Minimum files to form a group
- `cluster_selection_epsilon=0.3` - How tight clusters should be (lower = more specific)

### Embedding Model

Default: `all-MiniLM-L6-v2` (fast, 384 dims)

Alternative: `all-mpnet-base-v2` (better quality, 768 dims, slower)

## Examples

### Input Files
- `Screenshot 2024-03-15 at 2.30.45 PM.png`
- `Screenshot 2024-03-15 at 2.31.12 PM.png`
- `rupa_health_mockup.png`
- `ecojoy_landing_page.png`
- `ecojoy_about_us.png`
- `python_tutorial_part1.mp4`
- `python_tutorial_part2.mp4`

### Output Groups
```
📁 Rupa Health Dashboard (3 files)
   - Screenshot 2024-03-15 at 2.30.45 PM.png
   - Screenshot 2024-03-15 at 2.31.12 PM.png
   - rupa_health_mockup.png

📁 Ecojoy Website Design (2 files)
   - ecojoy_landing_page.png
   - ecojoy_about_us.png

📁 Python Programming Tutorials (2 files)
   - python_tutorial_part1.mp4
   - python_tutorial_part2.mp4
```

## Technical Details

### Embedding Model
- **Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Size**: ~80MB
- **Speed**: ~1000 sentences/second on CPU

### Clustering Algorithm
- **Algorithm**: HDBSCAN (Hierarchical Density-Based Spatial Clustering)
- **Benefits**:
  - Automatic cluster count
  - Handles noise (uncategorized files)
  - Finds clusters of varying density
  - No need to specify K

### Group Naming
- Uses Ollama LLM (`llama3.2:3b`)
- Analyzes up to 5 sample summaries per group
- Generates specific, descriptive 2-4 word names
- Prioritizes client/project names when present

## Performance

- **Embedding**: ~1 second per 100 files
- **Clustering**: <1 second for 1000 files
- **Naming**: ~2 seconds per group (LLM call)

**Total**: ~5-10 seconds for 100 files with 10 groups
