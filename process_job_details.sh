#!/bin/bash
set -e  # Exit on error

file_name="$1"  # Take the first command-line argument as file_name

# Extract chunk number from the file name (assumes chunk_N.json format)
chunk_number=$(echo "$file_name" | grep -oP '\d+')
output_file="job_summary_${chunk_number}.json"

echo "Processing file: $file_name"
echo "Output file: $output_file"

# Run the Python script with arguments
if ! python job-details-scraper.py "$file_name" "$output_file"; then
  echo "Job details scraper failed"
  exit 1
fi