# Git Branch Operations Guide - Pulling from GitHub

## Current Status
- **Remote**: `origin` → `https://github.com/imndevmodeai/ResonantiA-v3`
- **Current Branch**: `cursor/abstract-zepto-spr-process-in-dev-mode-3123`
- **Status**: Up to date with remote

## Pulling the Current Branch

### Method 1: Simple Pull (Recommended)
```bash
git pull
```
This automatically pulls from the tracked remote branch.

### Method 2: Explicit Pull
```bash
git pull origin cursor/abstract-zepto-spr-process-in-dev-mode-3123
```
Explicitly specifies the remote and branch name.

### Method 3: Fetch + Merge (More Control)
```bash
# First, fetch all remote changes
git fetch origin

# Check what changed
git log HEAD..origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123

# Then merge if you want
git merge origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123
```

## Pulling a Different Branch

### Pull Another Branch into Current Branch
```bash
# Fetch all branches first
git fetch origin

# Pull a specific branch (e.g., main)
git pull origin main
```

### Switch to and Pull a Different Branch
```bash
# Fetch all branches
git fetch origin

# Switch to the branch (creates local tracking branch if it doesn't exist)
git checkout cursor/prime-arche-protocol-v3-5-dev-mode-3818

# Or use the newer syntax
git switch cursor/prime-arche-protocol-v3-5-dev-mode-3818

# Pull latest changes
git pull
```

### Create Local Branch from Remote Branch
```bash
# Fetch all branches
git fetch origin

# Create and switch to a new local branch tracking the remote
git checkout -b local-branch-name origin/remote-branch-name

# Or use the newer syntax
git switch -c local-branch-name origin/remote-branch-name
```

## Available Remote Branches

Based on current repository state:

### Main Branches
- `origin/main` - Main development branch
- `origin/feature/evolve-to-v4-orchestrator` - Feature branch

### Cursor Branches (Development)
- `origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123` (current)
- `origin/cursor/prime-arche-protocol-v3-5-dev-mode-3818` (new)
- `origin/cursor/arche-s-cognitive-immune-system-against-stagnation-d40e`
- `origin/cursor/commit-push-and-merge-changes-563c`
- `origin/cursor/perception-engine-and-arche-retrieval-253c`
- `origin/cursor/perception-engine-and-arche-retrieval-d4b0`
- `origin/cursor/process-prime-arche-protocol-v3-5-89fa`
- `origin/cursor/process-prime-arche-protocol-v3-5-9621`
- `origin/cursor/store-github-pat-in-env-97db`

### Other Branches
- `origin/synthesis_branch`

## Common Pull Scenarios

### Scenario 1: Pull Latest Changes to Current Branch
```bash
git pull
```

### Scenario 2: Pull and Rebase (Cleaner History)
```bash
git pull --rebase
```

### Scenario 3: Pull with Auto-Stash (Saves Uncommitted Changes)
```bash
git pull --autostash
```

### Scenario 4: Pull Specific Remote Branch
```bash
git pull origin branch-name
```

### Scenario 5: Force Pull (Overwrites Local Changes - USE WITH CAUTION)
```bash
# WARNING: This discards local changes
git fetch origin
git reset --hard origin/cursor/abstract-zepto-spr-process-in-dev-mode-3123
```

## Troubleshooting

### Issue: "Your branch and 'origin/branch' have diverged"
**Solution**: You have local commits that aren't on remote, and remote has commits you don't have.
```bash
# Option 1: Merge (creates merge commit)
git pull --no-rebase

# Option 2: Rebase (cleaner history)
git pull --rebase

# Option 3: See what's different first
git log HEAD..origin/branch-name  # Remote commits you don't have
git log origin/branch-name..HEAD  # Local commits not on remote
```

### Issue: "Cannot pull because you have uncommitted changes"
**Solution**: Commit or stash your changes first.
```bash
# Option 1: Stash changes, pull, then reapply
git stash
git pull
git stash pop

# Option 2: Commit changes first
git add .
git commit -m "WIP: Save current changes"
git pull
```

### Issue: "Remote branch not found"
**Solution**: Fetch first to update remote branch list.
```bash
git fetch origin
git pull origin branch-name
```

## Best Practices

1. **Always fetch first** to see what's available:
   ```bash
   git fetch origin
   ```

2. **Check status before pulling**:
   ```bash
   git status
   ```

3. **Review changes before merging**:
   ```bash
   git log HEAD..origin/branch-name
   ```

4. **Use rebase for cleaner history** (if working alone):
   ```bash
   git pull --rebase
   ```

5. **Pull regularly** to stay in sync:
   ```bash
   git pull  # Daily or before starting work
   ```

## Quick Reference Commands

```bash
# Fetch all remote branches
git fetch origin

# Pull current branch
git pull

# Pull specific branch
git pull origin branch-name

# See all remote branches
git branch -r

# See all branches (local + remote)
git branch -a

# Check current branch status
git status

# See what would be pulled
git fetch origin
git log HEAD..origin/branch-name
```
