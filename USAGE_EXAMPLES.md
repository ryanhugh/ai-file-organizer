# Usage Examples

Real-world examples of how to use the File Organizer.

## Example 1: Clean Up Downloads Folder

**Scenario:** Your Downloads folder is a mess with 100+ random files.

```bash
# Step 1: See what would happen (dry run)
python main.py ~/Downloads -o ~/Downloads/Organized --dry-run --max-files 20

# Step 2: Review the output, then organize for real
python main.py ~/Downloads -o ~/Downloads/Organized

# Result: Files organized into categories like:
# - Documents/
# - Images/
# - Code/
# - Archives/
# - etc.
```

## Example 2: Organize Project Files

**Scenario:** You have random files on your Desktop that belong to different projects.

**Setup:**
```
~/Projects/
├── WebApp/
│   └── README.md  (describes the web app project)
├── DataAnalysis/
│   └── README.md  (describes the data analysis project)
└── MobileApp/
    └── README.md  (describes the mobile app project)
```

**Command:**
```bash
python main.py ~/Desktop -o ~/Desktop/Organized -p ~/Projects

# Result: Files matched to projects:
# Organized/
# ├── WebApp/
# │   └── files/
# │       ├── index.html
# │       ├── app.js
# │       └── styles.css
# ├── DataAnalysis/
# │   └── files/
# │       ├── data.csv
# │       └── analysis.py
# └── MobileApp/
#     └── files/
#         └── MainActivity.java
```

## Example 3: Organize Documents Recursively

**Scenario:** Your Documents folder has nested subdirectories with files everywhere.

```bash
# Organize all files in Documents and subdirectories
python main.py ~/Documents -o ~/Documents/Organized -r

# This will:
# - Scan all subdirectories
# - Extract content from all files
# - Organize everything into categories
```

## Example 4: Move Instead of Copy

**Scenario:** You want to clean up a folder and remove the original files.

```bash
# Move files instead of copying (frees up space)
python main.py ~/Downloads -o ~/Organized --move

# WARNING: Original files will be moved (not copied)
# Use --dry-run first to be safe!
```

## Example 5: Organize Specific File Types

**Scenario:** You only want to organize certain files.

```bash
# First, move files you want to organize to a temp folder
mkdir ~/temp_organize
cp ~/Downloads/*.pdf ~/temp_organize/
cp ~/Downloads/*.docx ~/temp_organize/

# Then organize
python main.py ~/temp_organize -o ~/Documents/Organized
```

## Example 6: Test with Small Batch

**Scenario:** You want to test the organizer before running it on everything.

```bash
# Test with just 5 files
python main.py ~/Downloads -o ~/test_output --max-files 5 --dry-run

# Review the output, adjust if needed, then run for real
python main.py ~/Downloads -o ~/test_output --max-files 5
```

## Example 7: Use Faster Model for Large Batches

**Scenario:** You have 1000+ files and want faster processing.

```bash
# Download the smaller, faster model
ollama pull llama3.2:1b

# Use it for organization
python main.py ~/Downloads -o ~/Organized --model llama3.2:1b

# Trade-off: Faster but slightly less accurate categorization
```

## Example 8: Organize Media Files

**Scenario:** You have a folder full of photos and videos.

```bash
python main.py ~/Pictures/Random -o ~/Pictures/Organized

# Result: Images organized by:
# - Type (photos, screenshots, etc.)
# - Content (if EXIF data available)
# - Date (from metadata)
```

## Example 9: Organize Code Projects

**Scenario:** You have random code files and want to group them by project.

**Setup:** Create project READMEs:
```bash
mkdir -p ~/Projects/Python_Scripts
echo "# Python Scripts\nUtility scripts for automation" > ~/Projects/Python_Scripts/README.md

mkdir -p ~/Projects/Web_Dev
echo "# Web Development\nHTML, CSS, JS projects" > ~/Projects/Web_Dev/README.md
```

**Command:**
```bash
python main.py ~/Desktop/code_files -o ~/Organized -p ~/Projects

# Files will be matched to projects based on content
```

## Example 10: Organize Work Documents

**Scenario:** Organize work documents by project/client.

**Setup:**
```bash
# Create project folders with descriptions
mkdir -p ~/Work/Projects/ClientA
cat > ~/Work/Projects/ClientA/README.md << EOF
# Client A Project
Marketing campaign for Client A.
Includes proposals, designs, and reports.
EOF

mkdir -p ~/Work/Projects/ClientB
cat > ~/Work/Projects/ClientB/README.md << EOF
# Client B Project
Website redesign for Client B.
Includes wireframes, mockups, and documentation.
EOF
```

**Command:**
```bash
python main.py ~/Desktop/work_files -o ~/Work/Organized -p ~/Work/Projects
```

## Example 11: Batch Processing Large Folders

**Scenario:** You have 5000+ files and want to process in batches.

```bash
# Process first 500 files
python main.py ~/Downloads -o ~/Organized --max-files 500

# Move organized files
mv ~/Organized/* ~/Final_Organized/

# Process next 500 files
python main.py ~/Downloads -o ~/Organized --max-files 500

# Repeat until done
```

## Example 12: Organize by File Type First

**Scenario:** Pre-organize by file type, then use AI for deeper categorization.

```bash
# Step 1: Manually group by type
mkdir -p ~/temp/{documents,images,code}
mv ~/Downloads/*.{pdf,docx,doc} ~/temp/documents/
mv ~/Downloads/*.{jpg,png,gif} ~/temp/images/
mv ~/Downloads/*.{py,js,java} ~/temp/code/

# Step 2: AI organize each group
python main.py ~/temp/documents -o ~/Organized/Documents
python main.py ~/temp/images -o ~/Organized/Images
python main.py ~/temp/code -o ~/Organized/Code
```

## Tips for Best Results

### 1. Good Project READMEs

**Bad:**
```markdown
# My Project
A project.
```

**Good:**
```markdown
# E-commerce Website
A full-stack e-commerce platform built with React and Node.js.
Features include user authentication, product catalog, shopping cart,
payment processing, and order management. Uses MongoDB for database
and AWS S3 for image storage.
```

### 2. Dry Run First

Always test with `--dry-run` before organizing:
```bash
python main.py ~/folder -o ~/output --dry-run
```

### 3. Start Small

Test with a few files first:
```bash
python main.py ~/folder -o ~/output --max-files 10
```

### 4. Use Copy Mode

Default is copy mode (safer):
```bash
python main.py ~/folder -o ~/output  # Copies files
```

Only use move if you're sure:
```bash
python main.py ~/folder -o ~/output --move  # Moves files
```

### 5. Review the Report

After organizing, check:
```bash
cat ~/output/ORGANIZATION_REPORT.md
```

### 6. Adjust Model Based on Needs

- **Fast:** `llama3.2:1b` - Good for large batches
- **Balanced:** `llama3.2:3b` - Default, good balance
- **Accurate:** `llama3.1:8b` - Best accuracy, slower

## Common Workflows

### Workflow 1: Weekly Downloads Cleanup
```bash
# Every week, organize new downloads
python main.py ~/Downloads -o ~/Downloads/Organized_$(date +%Y%m%d)
```

### Workflow 2: Project File Collection
```bash
# Collect files related to a project
python main.py ~/Desktop -o ~/Projects/MyProject/collected -p ~/Projects
```

### Workflow 3: Archive Old Files
```bash
# Organize old files before archiving
python main.py ~/OldFiles -o ~/Archive/$(date +%Y) -r
```

## Automation Ideas

### Cron Job (Weekly Cleanup)
```bash
# Add to crontab (crontab -e)
0 0 * * 0 cd ~/ryan-file-organizer && python main.py ~/Downloads -o ~/Downloads/Organized_$(date +\%Y\%m\%d)
```

### Shell Alias
```bash
# Add to ~/.zshrc or ~/.bashrc
alias organize='python ~/ryan-file-organizer/main.py'

# Usage:
organize ~/Downloads -o ~/Organized
```

### Shell Function
```bash
# Add to ~/.zshrc or ~/.bashrc
organize_folder() {
    python ~/ryan-file-organizer/main.py "$1" -o "${1}/Organized" --dry-run
    read -p "Proceed with organization? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python ~/ryan-file-organizer/main.py "$1" -o "${1}/Organized"
    fi
}

# Usage:
organize_folder ~/Downloads
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you have issues
- Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
