#!/bin/bash
# Script to remove database folder from git history
# WARNING: This will rewrite git history!

echo "🚨 SECURITY FIX: Remove database folder from git history"
echo "========================================================"
echo ""
echo "⚠️  BEFORE RUNNING THIS SCRIPT:"
echo "1. ✓ Have you changed your AWS RDS password? (CRITICAL!)"
echo "2. ✓ Have you notified team members about force push?"
echo "3. ✓ Have you backed up your work?"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted. Please complete security steps first."
    exit 1
fi

echo ""
echo "Step 1: Removing database/ from git history..."
git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch database/' \
  --prune-empty --tag-name-filter cat -- --all

if [ $? -ne 0 ]; then
    echo "❌ Failed to remove database from history"
    exit 1
fi

echo ""
echo "Step 2: Removing from staging area..."
git rm -r --cached database/ 2>/dev/null || true

echo ""
echo "Step 3: Cleaning up git refs..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "Step 4: Committing .gitignore update..."
git add .gitignore
git commit -m "chore: Add database folder to .gitignore (remove sensitive data)"

echo ""
echo "✅ Database folder removed from git history!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Review changes: git log --oneline -10"
echo "2. Force push: git push origin main --force"
echo "3. Verify on GitHub that database/ folder is gone"
echo "4. Search GitHub for your password (should find nothing)"
echo ""
echo "⚠️  Team members will need to re-clone or reset their repos!"
echo ""

