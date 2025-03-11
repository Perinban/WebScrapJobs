#!/bin/bash
# list_job_urls.sh

cd /home/runner/work/WebScrapJobs/WebScrapJobs/

# Check if the zip file exists in the job-urls directory
if [ ! -f "/job-urls/job-urls.zip" ]; then
  echo "job-urls.zip not found in the job-urls directory!"
  exit 1
fi

# Unzip job-urls.zip into the current directory (or specific directory)
echo "Unzipping job-urls.zip..."
unzip ./job-urls/job-urls.zip -d ./job-urls

# Check if unzip was successful
if [ $? -ne 0 ]; then
  echo "Unzip failed!"
  exit 1
fi

# List the files in the job-urls directory after unzip
echo "Listing files in job-urls directory:"
ls -al ./job-urls

# Get all the JSON files from the job-urls directory and format them into JSON
files=$(ls ./job-urls/job_urls*.json | jq -R -s -c 'split("\n")[:-1] | map({"file": .})')

# If no files are found, exit with an error
if [ "$files" == "[]" ]; then
  echo "No job URL chunks found"
  exit 1
fi

# Output the file list to GitHub actions
echo "files=$files" >> $GITHUB_OUTPUT