#!/bin/bash
set -e  # Exit on error

# List files for debugging
ls -R

file_name="./job-urls/$1"  # Prepend job-urls path to file_name

# Extract chunk number from the file name (assumes chunk_N.json format)
chunk_number=$(echo "$1" | grep -oP '\d+')
output_file="job_summary_${chunk_number}.json"

echo "Processing file: $file_name"
echo "Output file: $output_file"

# Run the Python script with arguments
if ! python job-details-scraper.py "$file_name" "$output_file"; then
  echo "Job details scraper failed"
  exit 1
fi