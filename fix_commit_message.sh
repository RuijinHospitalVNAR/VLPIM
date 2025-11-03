#!/bin/bash
# Script to fix commit message encoding issue
# This will rewrite Git history - use with caution!

echo "=========================================="
echo "Fix Commit Message Encoding Script"
echo "=========================================="
echo ""
echo "This script will fix the garbled commit message in commit ed954d6"
echo "Original message: feat: 瀹屾暣鏇存柊VLPIM椤圭洰閰嶇疆"
echo "New message: feat: Complete update VLPIM project configuration"
echo ""
echo "⚠️  WARNING: This will rewrite Git history!"
echo "⚠️  After running this, you MUST force push: git push --force origin main"
echo "⚠️  This will affect all collaborators - coordinate with your team first!"
echo ""
read -p "Do you want to proceed? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Operation cancelled."
    exit 1
fi

# Get the parent commit of ed954d6
PARENT=$(git log --format=%H ed954d6^1 | head -1)

echo "Starting interactive rebase..."
echo "You will be shown an editor - change 'pick' to 'reword' for the commit with garbled message"
echo "Then save the file, and you'll be prompted to enter the new commit message"
echo ""
read -p "Press Enter to continue..."

git rebase -i $PARENT

echo ""
echo "If the rebase was successful, you can now force push with:"
echo "  git push --force origin main"
echo ""
echo "If something went wrong, you can abort with:"
echo "  git rebase --abort"

