#!/bin/bash

# Set up Git configuration
git config --global user.name "GitHub Actions"
git config --global user.email "actions@github.com"

# Check if job_post_url.txt has changes
if ! git diff --quiet job_post_url.txt; then
  git add job_post_url.txt
  git commit -m "Auto-update job_post_url.txt"
  git push origin main || echo "Push failed, possibly due to conflicts or branch protection."
fi