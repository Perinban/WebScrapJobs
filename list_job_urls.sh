#!/bin/bash
# list_job_urls.sh

echo "Listing all files..."
ls -R

# Print current working directory
echo "Current working directory: $(pwd)"

# If job-urls.zip exists, unzip it; otherwise, assume files are already extracted
if [ -f "./job-urls/job-urls.zip" ]; then
  echo "Found job-urls.zip. Unzipping..."
  unzip -o ./job-urls/job-urls.zip -d ./job-urls

  # Check if unzip was successful
  if [ $? -ne 0 ]; then
    echo "Unzip failed!"
    exit 1
  fi
else
  echo "job-urls.zip not found. Assuming files are already extracted."
fi

# Get all the JSON files from the job-urls directory, remove the prefix, and format them into JSON
files=$(ls ./job-urls/job_urls*.json 2>/dev/null | sed 's|./job-urls/||' | jq -R -s -c 'split("\n") | map(select(length > 0)) | map({"file": .})')

# Print the JSON files list
echo "Extracted JSON files:"
echo "$files" | jq .

# Check if `files` is empty
if [ "$files" == "[]" ] || [ -z "$files" ]; then
  echo "No job URL chunks found"
  exit 1
fi

# Output the file list to GitHub actions
{
  echo "files=$files"
} >> "$GITHUB_OUTPUT"

echo "Writing to GITHUB_OUTPUT -> files=$files"