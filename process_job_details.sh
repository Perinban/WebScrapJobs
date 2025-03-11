#!/bin/bash

# process_job_details.sh
file_name="${{ matrix.file.file }}"
chunk_number=$(echo "$file_name" | grep -oP '\d+')
output_file="job_summary_${chunk_number}.json"

# Run the Python script with arguments
if ! python job-details-scraper.py "$file_name" "$output_file"; then
  echo "Job details scraper failed"
  exit 1
fi