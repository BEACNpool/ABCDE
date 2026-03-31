#!/bin/bash
# ABCDE GitHub Deployment Script
# Deploys genesis-founders dataset to https://github.com/BEACNpool/ABCDE

set -e

echo "=== ABCDE GitHub Deployment ==="
echo ""

# Configuration
REPO_URL="https://github.com/BEACNpool/ABCDE.git"
REPO_DIR="./ABCDE_repo"

# Check if git is configured
if ! git config user.name > /dev/null 2>&1; then
    echo "ERROR: Git user.name not configured"
    echo "Run: git config --global user.name 'Your Name'"
    exit 1
fi

if ! git config user.email > /dev/null 2>&1; then
    echo "ERROR: Git user.email not configured"
    echo "Run: git config --global user.email 'your@email.com'"
    exit 1
fi

# Clone repo (or use existing)
if [ -d "$REPO_DIR" ]; then
    echo "Using existing repo directory: $REPO_DIR"
    cd "$REPO_DIR"
    git pull origin main || git pull origin master
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
fi

# Copy all files from extracted zip
echo ""
echo "Copying files..."
cp -r ../ABCDE/* .

# Add all files
echo ""
echo "Staging files for commit..."
git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short

# Commit
echo ""
read -p "Enter commit message [Genesis founders dataset - initial release]: " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Genesis founders dataset - initial release"}

git commit -m "$COMMIT_MSG"

# Push
echo ""
echo "Pushing to GitHub..."
git push origin main || git push origin master

echo ""
echo "=== Deployment Complete ==="
echo "Repository: $REPO_URL"
echo ""
