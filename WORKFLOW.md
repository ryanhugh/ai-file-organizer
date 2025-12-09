# File Organizer Workflow

Visual guide to how the file organizer works.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR MACBOOK                            │
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │   Messy      │         │   Ollama     │                │
│  │   Folder     │         │   (Local     │                │
│  │              │         │    LLM)      │                │
│  └──────┬───────┘         └──────▲───────┘                │
│         │                        │                         │
│         │                        │                         │
│         ▼                        │                         │
│  ┌─────────────────────────────┴──────┐                  │
│  │   File Organizer                   │                  │
│  │   (This Program)                   │                  │
│  └─────────────────┬──────────────────┘                  │
│                    │                                       │
│                    ▼                                       │
│  ┌──────────────────────────────────┐                    │
│  │   Organized Folder               │                    │
│  │   ├── Project A/                 │                    │
│  │   ├── Documents/                 │                    │
│  │   └── Images/                    │                    │
│  └──────────────────────────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Step-by-Step Process

### Step 1: Scan Files
```
Source Folder
├── file1.pdf
├── file2.py
├── file3.jpg
├── file4.docx
└── file5.json
         │
         ▼
    [Scanning...]
         │
         ▼
   5 files found
```

### Step 2: Extract Content
```
For each file:
┌─────────────┐
│  file1.pdf  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Extract text from   │
│ PDF pages 1-10      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ "This is a report   │
│  about project X... │
│  contains data..."  │
└─────────────────────┘
```

### Step 3: Load Projects (Optional)
```
Projects Folder
├── ProjectA/
│   └── README.md → "Web app using React..."
├── ProjectB/
│   └── README.md → "Data analysis with Python..."
└── ProjectC/
    └── README.md → "Mobile app for iOS..."
         │
         ▼
   3 projects loaded
```

### Step 4: AI Categorization
```
For each file:

┌──────────────────────────────────────────────┐
│  File: file1.pdf                             │
│  Content: "This is a report about project X" │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│         Send to Local LLM (Ollama)           │
│                                              │
│  Prompt: "Match this file to a project:     │
│   1. ProjectA: Web app using React...       │
│   2. ProjectB: Data analysis with Python... │
│   3. ProjectC: Mobile app for iOS..."       │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────┐
│  LLM Response: "2" (ProjectB)                │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
        File matched to ProjectB!
```

### Step 5: Organize Files
```
Organized Folder
├── ORGANIZATION_REPORT.md
├── ProjectB/
│   ├── README.md
│   └── files/
│       └── file1.pdf  ← Copied/Moved here
├── Code/
│   ├── README.md
│   └── files/
│       └── file2.py
├── Images/
│   ├── README.md
│   └── files/
│       └── file3.jpg
└── Documents/
    ├── README.md
    └── files/
        ├── file4.docx
        └── file5.json
```

## Decision Flow

```
                    Start
                      │
                      ▼
            ┌─────────────────┐
            │  Scan Files     │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Extract Content │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ Projects Exist? │
            └────┬────────┬───┘
                 │        │
            Yes  │        │ No
                 │        │
                 ▼        ▼
        ┌────────────┐  ┌────────────┐
        │ Try Match  │  │ Categorize │
        │ to Project │  │ by Content │
        └─────┬──────┘  └─────┬──────┘
              │               │
              ▼               │
        ┌──────────┐          │
        │ Matched? │          │
        └─┬─────┬──┘          │
          │     │             │
     Yes  │     │ No          │
          │     │             │
          │     └─────────────┘
          │                   │
          ▼                   ▼
    ┌──────────┐      ┌──────────────┐
    │ Add to   │      │ Add to       │
    │ Project  │      │ Category     │
    └────┬─────┘      └──────┬───────┘
         │                   │
         └──────────┬────────┘
                    │
                    ▼
            ┌──────────────┐
            │ Copy/Move    │
            │ File         │
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ Create       │
            │ README       │
            └──────┬───────┘
                   │
                   ▼
                  Done
```

## File Type Handling

```
Input File
    │
    ▼
┌─────────────────┐
│ Check Extension │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬─────────┬──────────┐
    │         │         │         │          │
    ▼         ▼         ▼         ▼          ▼
  .pdf     .docx      .jpg      .py       .json
    │         │         │         │          │
    ▼         ▼         ▼         ▼          ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐
│PyPDF2│ │python│ │Pillow│ │ Text │ │   JSON   │
│      │ │-docx │ │(EXIF)│ │Reader│ │  Parser  │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └────┬─────┘
   │        │        │        │          │
   └────────┴────────┴────────┴──────────┘
                     │
                     ▼
              ┌─────────────┐
              │  Extracted  │
              │   Content   │
              └─────────────┘
```

## Example: Organizing 5 Files

```
Before:
~/Downloads/
├── report.pdf
├── script.py
├── photo.jpg
├── notes.docx
└── data.json

Command:
$ python main.py ~/Downloads -o ~/Organized -p ~/Projects

Process:
1. Scan: Found 5 files
2. Extract:
   - report.pdf → "Q3 sales report..."
   - script.py → "import pandas..."
   - photo.jpg → [Image: 1920x1080]
   - notes.docx → "Meeting notes..."
   - data.json → {"sales": [...]}

3. Match to Projects:
   - report.pdf → ProjectA (Sales)
   - script.py → ProjectB (Data Analysis)
   - photo.jpg → No match → "Images"
   - notes.docx → No match → "Documents"
   - data.json → ProjectB (Data Analysis)

4. Organize:

After:
~/Organized/
├── ORGANIZATION_REPORT.md
├── ProjectA/
│   ├── README.md
│   └── files/
│       └── report.pdf
├── ProjectB/
│   ├── README.md
│   └── files/
│       ├── script.py
│       └── data.json
├── Images/
│   ├── README.md
│   └── files/
│       └── photo.jpg
└── Documents/
    ├── README.md
    └── files/
        └── notes.docx
```

## Command Flow

```
┌──────────────────────────────────────────┐
│ $ python main.py ~/Downloads -o ~/Out    │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│ Parse Arguments                          │
│ - source: ~/Downloads                    │
│ - output: ~/Out                          │
│ - copy_mode: True (default)              │
│ - dry_run: False (default)               │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│ Initialize Components                    │
│ - FileExtractor                          │
│ - LLMCategorizer (connect to Ollama)    │
│ - ProjectManager                         │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│ Run Organization                         │
│ [1/5] Load projects                      │
│ [2/5] Scan files                         │
│ [3/5] Extract content                    │
│ [4/5] Categorize with AI                 │
│ [5/5] Organize files                     │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│ Generate Reports                         │
│ - ORGANIZATION_REPORT.md                 │
│ - Category README files                  │
└───────────────┬──────────────────────────┘
                │
                ▼
              Done!
```

## Dry Run vs Real Run

### Dry Run (--dry-run)
```
┌─────────────┐
│ Scan Files  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Extract     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Categorize  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ SIMULATE organize   │
│ (don't move files)  │
│ (don't create dirs) │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Show what WOULD     │
│ happen              │
└─────────────────────┘
```

### Real Run
```
┌─────────────┐
│ Scan Files  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Extract     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Categorize  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ ACTUALLY organize   │
│ - Create dirs       │
│ - Copy/move files   │
│ - Create READMEs    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Files organized!    │
└─────────────────────┘
```

## Privacy Flow

```
┌────────────────────────────────────────┐
│         YOUR COMPUTER ONLY             │
│                                        │
│  ┌──────────┐      ┌──────────┐      │
│  │  Files   │──────▶│ Extractor│      │
│  └──────────┘      └─────┬────┘      │
│                           │            │
│                           ▼            │
│                    ┌──────────┐       │
│                    │  Ollama  │       │
│                    │  (Local) │       │
│                    └─────┬────┘       │
│                          │             │
│                          ▼             │
│                   ┌──────────┐        │
│                   │ Organize │        │
│                   └──────────┘        │
│                                        │
│  NO INTERNET CONNECTION NEEDED!        │
│  NO DATA LEAVES YOUR MACHINE!          │
└────────────────────────────────────────┘
```

## Quick Reference

### Basic Command
```bash
python main.py <source> -o <output>
```

### With Projects
```bash
python main.py <source> -o <output> -p <projects>
```

### Safe Testing
```bash
python main.py <source> -o <output> --dry-run --max-files 5
```

### Fast Processing
```bash
python main.py <source> -o <output> --model llama3.2:1b
```

---

For more details, see:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Real examples
