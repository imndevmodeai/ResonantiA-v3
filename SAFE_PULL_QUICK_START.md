# Safe Pull Quick Start Guide

## Overview
The `safe_pull_from_branch.sh` script safely pulls **only new files** from a remote GitHub branch without overwriting your existing local modifications.

## Quick Usage

### Step 1: List Available Branches
```bash
./safe_pull_from_branch.sh
```
This will show all available remote branches.

### Step 2: Pull from a Specific Branch
```bash
./safe_pull_from_branch.sh <branch_name>
```

**Examples:**
```bash
# Pull from feature branch
./safe_pull_from_branch.sh feature/evolve-to-v4-orchestrator

# Pull from main
./safe_pull_from_branch.sh main

# Pull from synthesis branch
./safe_pull_from_branch.sh synthesis_branch
```

## What the Script Does

1. ✅ **Fetches** the latest changes from the remote branch
2. ✅ **Identifies** only NEW files (files that don't exist locally)
3. ✅ **Filters out** build artifacts, virtual environments, and temporary files:
   - `.next/` (Next.js build cache)
   - `arche_env/`, `venv/`, `.venv/` (Python virtual environments)
   - `node_modules/` (Node.js dependencies)
   - `__pycache__/`, `*.pyc` (Python cache)
   - `.log` files
   - Browser session data
4. ✅ **Shows preview** of files to be pulled
5. ✅ **Asks for confirmation** before pulling
6. ✅ **Pulls only new files** that don't exist locally
7. ✅ **Preserves** all your local modifications

## What Gets Filtered Out

The script automatically excludes:
- Build artifacts (`.next/`, `dist/`, `build/`)
- Virtual environments (`arche_env/`, `venv/`, `.venv/`)
- Cache files (`__pycache__/`, `*.pyc`, `*.pyo`)
- Log files (`*.log`)
- Browser session data
- OS files (`.DS_Store`, `Thumbs.db`)

## Safety Features

- ✅ **Never overwrites** existing local files
- ✅ **Interactive confirmation** before pulling
- ✅ **Preview** of what will be pulled
- ✅ **Clear warnings** about modified files that won't be touched

## After Running the Script

1. **Review what was pulled:**
   ```bash
   git status
   git diff --cached
   ```

2. **Commit the new files:**
   ```bash
   git commit -m "Add new files from <branch_name>"
   ```

3. **Or unstage if needed:**
   ```bash
   git restore --staged <file>
   ```

## Manual File Pulling

If you want to pull a specific file manually:
```bash
git checkout origin/<branch_name> -- <file_path>
```

## Troubleshooting

**Q: The script says "No new files found" but I know there are differences**
- The script only pulls files that are **completely new** (don't exist locally)
- Files that exist in both branches but differ are **not** pulled (to preserve your changes)
- To see all differences: `git diff --name-status HEAD origin/<branch_name>`

**Q: I want to see what files differ (including modified ones)**
```bash
git diff --name-status HEAD origin/<branch_name>
```

**Q: I accidentally pulled a file I didn't want**
```bash
git restore --staged <file>  # Unstage it
git restore <file>            # Discard the changes
```

## Available Remote Branches

Based on your repository, you have these remote branches:
- `origin/main`
- `origin/feature/evolve-to-v4-orchestrator`
- `origin/synthesis_branch`
- `origin/cursor/*` (various cursor-generated branches)

