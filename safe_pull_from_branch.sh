#!/bin/bash
# Safe Pull Script: Pulls new files from a remote branch without overwriting local changes
# Usage: ./safe_pull_from_branch.sh [branch_name]
# Example: ./safe_pull_from_branch.sh feature/evolve-to-v4-orchestrator
#          ./safe_pull_from_branch.sh  # Will prompt for branch selection

set -e  # Exit on error

REMOTE="origin"

# Function to filter out build artifacts, virtual environments, and temporary files
filter_artifacts() {
    grep -v -E '^\.next/' \
    | grep -v -E '^arche_env/' \
    | grep -v -E '^node_modules/' \
    | grep -v -E '^\.venv/' \
    | grep -v -E '^venv/' \
    | grep -v -E '^__pycache__/' \
    | grep -v -E '\.pyc$' \
    | grep -v -E '\.pyo$' \
    | grep -v -E '\.log$' \
    | grep -v -E '^\.git/' \
    | grep -v -E '^ResonantiA/browser_automationz_clone/\.chrome_dev_session/' \
    | grep -v -E '\.DS_Store$' \
    | grep -v -E 'Thumbs\.db$' || true
}

# Step 0: Determine which branch to pull from
if [ -z "$1" ]; then
    echo "=========================================="
    echo "Safe Pull from Remote Branch"
    echo "=========================================="
    echo ""
    echo "Available remote branches:"
    git fetch ${REMOTE} 2>/dev/null || true
    git branch -r | grep ${REMOTE} | grep -v HEAD | sed 's/^/  /' | sed "s|${REMOTE}/||"
    echo ""
    echo "Please specify the branch name:"
    echo "  ./safe_pull_from_branch.sh <branch_name>"
    echo ""
    echo "Example: ./safe_pull_from_branch.sh feature/evolve-to-v4-orchestrator"
    exit 1
fi

BRANCH_NAME="$1"
REMOTE_BRANCH_REF="${REMOTE}/${BRANCH_NAME}"

echo "=========================================="
echo "Safe Pull from Remote Branch"
echo "=========================================="
echo "Target Branch: ${REMOTE_BRANCH_REF}"
echo "Current Branch: $(git branch --show-current)"
echo ""

# Step 1: Verify branch exists remotely
if ! git ls-remote --heads ${REMOTE} ${BRANCH_NAME} | grep -q ${BRANCH_NAME}; then
    echo "ERROR: Branch ${REMOTE_BRANCH_REF} does not exist remotely."
    echo ""
    echo "Available remote branches:"
    git branch -r | grep ${REMOTE} | sed 's/^/  /'
    exit 1
fi

# Step 2: Fetch latest from remote
echo "Step 1: Fetching latest from ${REMOTE}..."
git fetch ${REMOTE} ${BRANCH_NAME}

# Step 3: Show what files differ between local and remote
echo ""
echo "Step 2: Analyzing differences..."
echo "----------------------------------------"

LOCAL_BRANCH="HEAD"

# Get new files (that exist in remote but not locally)
echo "Identifying new files in remote branch..."
NEW_FILES=$(git diff --name-only --diff-filter=A ${LOCAL_BRANCH} ${REMOTE_BRANCH_REF} 2>/dev/null | filter_artifacts || true)

# Get modified files (that exist in both but differ)
echo "Identifying modified files (potential conflicts)..."
MODIFIED_FILES=$(git diff --name-only ${LOCAL_BRANCH} ${REMOTE_BRANCH_REF} 2>/dev/null | filter_artifacts | head -30 || true)

if [ -n "$MODIFIED_FILES" ]; then
    echo ""
    echo "⚠️  WARNING: Files that differ between local and remote (will NOT be overwritten):"
    echo "$MODIFIED_FILES" | sed 's/^/  - /' | head -20
    if [ $(echo "$MODIFIED_FILES" | wc -l) -gt 20 ]; then
        echo "  ... and $(($(echo "$MODIFIED_FILES" | wc -l) - 20)) more"
    fi
    echo ""
    echo "These files will be preserved as-is. Only NEW files will be pulled."
fi

# Step 4: Show preview of files to pull
echo ""
echo "Step 3: Preview of new files to pull..."
echo "----------------------------------------"

if [ -z "$NEW_FILES" ]; then
    echo "✅ No new source files found in remote branch that don't exist locally."
    echo ""
    echo "All files in the remote branch either:"
    echo "  - Already exist locally (your version will be preserved)"
    echo "  - Are build artifacts/virtual env files (filtered out)"
    echo ""
    echo "To see all differences (including modified files):"
    echo "  git diff --name-status ${LOCAL_BRANCH} ${REMOTE_BRANCH_REF} | filter_artifacts"
    exit 0
fi

echo "New files that will be pulled (these don't exist locally):"
echo "$NEW_FILES" | sed 's/^/  ✓ /'
echo ""

# Step 5: Confirm before pulling
read -p "Proceed with pulling these files? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Pull cancelled by user."
    exit 0
fi

# Step 6: Pull only the new files
echo ""
echo "Step 4: Pulling new files (this will NOT overwrite your local changes)..."
echo "----------------------------------------"

PULLED_COUNT=0
SKIPPED_COUNT=0

echo "$NEW_FILES" | while IFS= read -r file; do
    if [ -z "$file" ]; then
        continue
    fi
    
    # Check if file exists locally
    if [ -f "$file" ]; then
        echo "  ⚠️  Skipping: $file (already exists locally - preserving your version)"
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    else
        # Check if parent directory exists, create if needed
        dir=$(dirname "$file")
        if [ "$dir" != "." ] && [ ! -d "$dir" ]; then
            mkdir -p "$dir"
        fi
        
        # Checkout the file from remote branch
        if git checkout ${REMOTE_BRANCH_REF} -- "$file" 2>/dev/null; then
            echo "  ✓ Pulled: $file"
            PULLED_COUNT=$((PULLED_COUNT + 1))
        else
            echo "  ✗ Failed: $file (may be in .gitignore or deleted)"
        fi
    fi
done

# Note: Variables set in while loop don't persist, so we'll use git status instead
echo ""
echo "Step 5: Summary"
echo "----------------------------------------"
echo "✅ Safe pull operation completed!"
echo ""
echo "Files pulled from: ${REMOTE_BRANCH_REF}"
echo "Your local modifications have been preserved."
echo ""
echo "Review the changes:"
echo "  git status                    # See what was added"
echo "  git diff --cached            # See content of new files"
echo ""

# Show what was actually staged
STAGED_NEW=$(git diff --cached --name-only --diff-filter=A 2>/dev/null || true)
if [ -n "$STAGED_NEW" ]; then
    echo "New files staged for commit:"
    echo "$STAGED_NEW" | sed 's/^/  - /'
    echo ""
    echo "To commit these new files:"
    echo "  git commit -m 'Add new files from ${BRANCH_NAME}'"
    echo ""
    echo "To unstage if needed:"
    echo "  git restore --staged <file>"
fi

echo ""
echo "=========================================="
echo "Safe Pull Complete"
echo "=========================================="
echo ""
echo "Additional commands:"
echo "  git diff --name-status ${LOCAL_BRANCH} ${REMOTE_BRANCH_REF}  # See all differences"
echo "  git checkout ${REMOTE_BRANCH_REF} -- <specific_file>         # Pull a specific file manually"

