# Safe Pull Guide: Pulling Files from Remote Branch Without Overwriting Local Changes

## Overview
This guide provides multiple strategies to safely pull files from a GitHub branch while preserving your local enhancements.

## Prerequisites
✅ Backup branch created: `backup-before-pull-*` (already created)
✅ Current branch: `main`
✅ Remote: `origin`

## Method 1: Automated Script (Recommended)
Use the provided script to automatically pull only new files:

```bash
# Pull from a specific branch (defaults to feature/evolve-to-v4-orchestrator)
./safe_pull_from_branch.sh <branch_name>

# Example:
./safe_pull_from_branch.sh feature/evolve-to-v4-orchestrator
./safe_pull_from_branch.sh synthesis_branch
```

The script will:
- ✅ Only pull files that don't exist locally (new files)
- ✅ Skip files you've modified locally
- ✅ Show you what will be pulled before doing it

## Method 2: Manual Selective Checkout (Most Control)

### Step 1: See what files differ
```bash
# See all files that differ between local and remote branch
git diff --name-status HEAD origin/<branch_name>

# See only new files in remote (not in local)
git diff --name-only --diff-filter=A HEAD origin/<branch_name>

# See only modified files (in both)
git diff --name-only --diff-filter=M HEAD origin/<branch_name>
```

### Step 2: Pull specific files one by one
```bash
# Pull a single new file from remote branch
git checkout origin/<branch_name> -- <path/to/file>

# Example:
git checkout origin/feature/evolve-to-v4-orchestrator -- Three_PointO_ArchE/new_file.py
```

### Step 3: Review before committing
```bash
# See what was staged
git status
git diff --cached

# If you don't like a change, unstage it
git restore --staged <file>
```

## Method 3: Merge Strategy (Preserve Local Changes)

### Option A: Merge with "ours" strategy for conflicts
```bash
# This will merge but prefer your local changes when conflicts occur
git merge -X ours origin/<branch_name>
```

### Option B: Merge with manual conflict resolution
```bash
# Merge and resolve conflicts manually
git merge origin/<branch_name>

# If conflicts occur, Git will mark them. You can then:
# - Keep your version: git checkout --ours <file>
# - Use remote version: git checkout --theirs <file>
# - Manually edit and resolve
```

## Method 4: Stash Your Changes, Pull, Then Reapply

```bash
# 1. Stash your local changes
git stash push -m "My local enhancements before pulling"

# 2. Pull from remote branch
git checkout origin/<branch_name> -- <specific_files>

# 3. Reapply your stashed changes
git stash pop

# 4. Resolve any conflicts that arise
```

## Available Remote Branches

Based on your repository, here are the available branches:

- `feature/evolve-to-v4-orchestrator` - Main feature branch
- `synthesis_branch` - Synthesis branch
- `cursor/prime-arche-protocol-v3-5-dev-mode-3818` - Protocol dev branch
- `cursor/process-prime-arche-protocol-v3-5-89fa` - Process branch
- `cursor/process-prime-arche-protocol-v3-5-9621` - Process branch variant
- `cursor/abstract-zepto-spr-process-in-dev-mode-3123` - SPR process branch
- `cursor/arche-s-cognitive-immune-system-against-stagnation-d40e` - Cognitive system branch
- `cursor/perception-engine-and-arche-retrieval-253c` - Perception engine branch
- `cursor/perception-engine-and-arche-retrieval-d4b0` - Perception engine variant
- `cursor/store-github-pat-in-env-97db` - PAT storage branch

## Quick Reference Commands

```bash
# See what branch you want to pull from
git branch -r

# Fetch latest from all remotes
git fetch origin

# See differences between local and remote branch
git diff --name-status HEAD origin/<branch_name>

# Pull a specific file from remote branch
git checkout origin/<branch_name> -- <file_path>

# See what files are new in remote (safe to pull)
git diff --name-only --diff-filter=A HEAD origin/<branch_name>

# See what files you've modified locally (will be skipped)
git status

# Create a comparison report
git diff --stat HEAD origin/<branch_name> > branch_comparison.txt
```

## Safety Checklist

Before pulling:
- [x] Backup branch created
- [ ] Identify which branch to pull from
- [ ] Review files that will be pulled
- [ ] Ensure important local changes are committed or stashed

After pulling:
- [ ] Review `git status` to see what changed
- [ ] Test your code to ensure nothing broke
- [ ] Commit the pulled files if satisfied

## Recovery

If something goes wrong:
```bash
# Restore from backup branch
git checkout backup-before-pull-*

# Or restore specific files
git checkout HEAD -- <file_path>

# Or reset to before the pull
git reset --hard HEAD@{1}
```

