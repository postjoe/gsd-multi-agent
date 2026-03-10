#!/bin/bash

echo "============================================="
echo "GSD Multi-Agent - GitHub Push Script"
echo "============================================="
echo ""
echo "This script will push your repository to GitHub."
echo ""
echo "STEP 1: First, create a new repository on GitHub:"
echo "  1. Go to https://github.com/new"
echo "  2. Repository name: gsd-multi-agent"
echo "  3. Description: Multi-agent workflow system for Claude Code with FREE tier optimization"
echo "  4. Choose Public or Private"
echo "  5. DO NOT initialize with README, .gitignore, or License"
echo "  6. Click 'Create repository'"
echo ""
echo "STEP 2: After creating, GitHub will show you the repository URL."
echo ""

read -p "Enter your GitHub username: " username
echo ""
echo "Choose connection type:"
echo "1. HTTPS (recommended, uses token)"
echo "2. SSH (requires SSH key setup)"
read -p "Enter 1 or 2: " connection

if [ "$connection" = "2" ]; then
    remote_url="git@github.com:${username}/gsd-multi-agent.git"
else
    remote_url="https://github.com/${username}/gsd-multi-agent.git"
fi

echo ""
echo "Adding remote: $remote_url"
git remote add origin "$remote_url"

echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -ne 0 ]; then
    echo ""
    echo "============================================="
    echo "Push failed. Possible issues:"
    echo ""
    echo "1. Authentication: You may need to:"
    echo "   - For HTTPS: Use a personal access token instead of password"
    echo "     Create one at: https://github.com/settings/tokens"
    echo "   - For SSH: Ensure your SSH key is added to GitHub"
    echo ""
    echo "2. Repository not created: Make sure you created the repo on GitHub first"
    echo ""
    echo "3. Wrong username: Check that the username is correct"
    echo "============================================="
    exit 1
fi

echo ""
echo "============================================="
echo "SUCCESS! Repository pushed to GitHub!"
echo "============================================="
echo ""
echo "Your repository is now available at:"
echo "https://github.com/${username}/gsd-multi-agent"
echo ""
echo "Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Add topics: claude-code, multi-agent, cost-optimization, opencode"
echo "3. Star the repository"
echo "4. Share with your other projects!"
echo ""
echo "To use in other projects:"
echo "  git clone $remote_url"
echo "  cp -r gsd-multi-agent /your-project/gsd_setup"
echo "  python gsd_setup/install.py --project-name 'YourProject'"
echo ""
