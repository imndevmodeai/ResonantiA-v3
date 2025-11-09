# How to Preview Changes Before Pulling a Branch

## Quick Commands Summary

```bash
# 1. Fetch remote changes (doesn't modify your working directory)
git fetch origin

# 2. View commits that would be pulled
git log HEAD..origin/branch-name --oneline

# 3. View file changes summary
git diff HEAD..origin/branch-name --stat

# 4. View detailed file changes
git diff HEAD..origin/branch-name

# 5. View changes for specific files
git diff HEAD..origin/branch-name -- path/to/file
```

## Step-by-Step Process

### Step 1: Fetch Remote Changes
First, fetch the latest changes from GitHub without modifying your working directory:

```bash
git fetch origin
```

This downloads all remote branch updates but doesn't merge them into your local branch.

### Step 2: View Commits That Would Be Pulled
See what commits are on the remote that you don't have locally:

```bash
# For current branch
git log HEAD..origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123 --oneline

# For any branch
git log HEAD..origin/branch-name --oneline
```

**Output shows:**
- Commit hashes (short)
- Commit messages
- Only commits you don't have locally

**More detailed view:**
```bash
git log HEAD..origin/branch-name --pretty=format:"%h - %an, %ar : %s"
```

**Graphical view:**
```bash
git log HEAD..origin/branch-name --graph --oneline --decorate
```

### Step 3: View File Changes Summary
See which files would be changed and how many lines:

```bash
# Summary of changes
git diff HEAD..origin/branch-name --stat

# Example output:
#  file1.py    | 15 +++++++++------
#  file2.py    |  8 ++++++++
#  file3.md    |  3 +++
#  3 files changed, 26 insertions(+), 6 deletions(-)
```

### Step 4: View Detailed File Changes
See the actual code/text changes:

```bash
# All changes
git diff HEAD..origin/branch-name

# Specific file
git diff HEAD..origin/branch-name -- path/to/file.py

# Specific directory
git diff HEAD..origin/branch-name -- directory/

# Only show file names (no content)
git diff HEAD..origin/branch-name --name-only

# Show file names with status (Added, Modified, Deleted)
git diff HEAD..origin/branch-name --name-status
```

### Step 5: View Changes Side-by-Side
For easier comparison:

```bash
git diff HEAD..origin/branch-name --word-diff
```

## Advanced Preview Options

### View Changes in a Specific File
```bash
git diff HEAD..origin/branch-name -- path/to/specific/file.py
```

### View Only Added Files
```bash
git diff HEAD..origin/branch-name --diff-filter=A --name-only
```

### View Only Modified Files
```bash
git diff HEAD..origin/branch-name --diff-filter=M --name-only
```

### View Only Deleted Files
```bash
git diff HEAD..origin/branch-name --diff-filter=D --name-only
```

### View Changes with Context Lines
```bash
# Show 10 lines of context around each change
git diff HEAD..origin/branch-name -U10
```

### View Changes in a Specific Directory
```bash
git diff HEAD..origin/branch-name -- Three_PointO_ArchE/
```

## Compare Different Branches

### Compare Current Branch with Main
```bash
git fetch origin
git log HEAD..origin/main --oneline
git diff HEAD..origin/main --stat
```

### Compare Two Remote Branches
```bash
git fetch origin
git log origin/branch1..origin/branch2 --oneline
git diff origin/branch1..origin/branch2 --stat
```

## Practical Examples

### Example 1: Preview Changes Before Pulling Current Branch
```bash
# Fetch latest
git fetch origin

# See what commits would come in
git log HEAD..origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123 --oneline

# See file summary
git diff HEAD..origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123 --stat

# See actual changes (if any)
git diff HEAD..origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123

# If satisfied, pull
git pull
```

### Example 2: Preview Changes from Main Branch
```bash
# Fetch latest
git fetch origin

# See what's in main that you don't have
git log HEAD..origin/main --oneline

# See file changes
git diff HEAD..origin/main --stat

# See changes in specific directory
git diff HEAD..origin/main -- Three_PointO_ArchE/ --stat
```

### Example 3: Preview Changes in Specific Files
```bash
# Fetch first
git fetch origin

# Preview changes in action_registry.py
git diff HEAD..origin/branch-name -- Three_PointO_ArchE/action_registry.py

# Preview changes in all Python files
git diff HEAD..origin/branch-name -- '*.py'
```

## Using Git Tools for Better Visualization

### Using Git Log with More Details
```bash
# Detailed commit view
git log HEAD..origin/branch-name --pretty=fuller

# One-line summary with author
git log HEAD..origin/branch-name --pretty=format:"%h - %an, %ar : %s" --graph

# Show files changed in each commit
git log HEAD..origin/branch-name --stat --oneline
```

### Using Git Show for Specific Commits
```bash
# First, get the commit hash from git log
git log HEAD..origin/branch-name --oneline

# Then view that specific commit
git show <commit-hash>

# View just the file changes in that commit
git show <commit-hash> --stat
```

## Safety Check: What Would Happen?

### Dry Run (Simulation)
Git doesn't have a true "dry run" for pull, but you can simulate:

```bash
# 1. Fetch (safe, doesn't change anything)
git fetch origin

# 2. See what would merge
git log --oneline --graph --decorate HEAD origin/branch-name

# 3. See if there would be conflicts
git merge-tree $(git merge-base HEAD origin/branch-name) HEAD origin/branch-name
```

### Check for Potential Conflicts
```bash
# This shows if there would be merge conflicts
git merge --no-commit --no-ff origin/branch-name

# If it succeeds, abort to keep your branch clean
git merge --abort
```

## Quick Reference Cheat Sheet

```bash
# === FETCH (Safe - doesn't modify anything) ===
git fetch origin                    # Fetch all branches
git fetch origin branch-name       # Fetch specific branch

# === VIEW COMMITS ===
git log HEAD..origin/branch-name --oneline              # Commit list
git log HEAD..origin/branch-name --stat                 # Commits + files
git log HEAD..origin/branch-name --graph --oneline      # Visual graph

# === VIEW FILE CHANGES ===
git diff HEAD..origin/branch-name --stat                # Summary
git diff HEAD..origin/branch-name                       # Full diff
git diff HEAD..origin/branch-name -- path/to/file       # Specific file
git diff HEAD..origin/branch-name --name-only           # File names only
git diff HEAD..origin/branch-name --name-status         # Files + status

# === VIEW SPECIFIC CHANGES ===
git diff HEAD..origin/branch-name --diff-filter=A       # Added files
git diff HEAD..origin/branch-name --diff-filter=M       # Modified files
git diff HEAD..origin/branch-name --diff-filter=D       # Deleted files

# === AFTER REVIEWING, PULL ===
git pull                                                # Pull current branch
git pull origin branch-name                            # Pull specific branch
```

## Current Branch Status

For your current branch (`cursor/abstract-zepto-spr-process-in-dev-mode-3123`):

```bash
# Check if there are any new commits
git fetch origin
git log HEAD..origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123 --oneline

# If empty output = no new commits (already up to date)
# If shows commits = those would be pulled
```

## Best Practices

1. **Always fetch first** before checking differences:
   ```bash
   git fetch origin
   ```

2. **Review commits** to understand what changed:
   ```bash
   git log HEAD..origin/branch-name --oneline
   ```

3. **Check file summary** to see scope of changes:
   ```bash
   git diff HEAD..origin/branch-name --stat
   ```

4. **Review critical files** before pulling:
   ```bash
   git diff HEAD..origin/branch-name -- important_file.py
   ```

5. **Pull only after reviewing**:
   ```bash
   git pull
   ```

## Troubleshooting

### "No commits to show"
- Your branch is already up to date
- No changes to pull

### "fatal: ambiguous argument"
- Make sure you've fetched first: `git fetch origin`
- Check branch name spelling

### Too many changes to review
- Use `--stat` for summary first
- Focus on specific files: `git diff HEAD..origin/branch-name -- path/to/file`
- Use `--name-only` to see just file names
