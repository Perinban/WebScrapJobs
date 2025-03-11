#!/bin/bash
# list_job_urls.sh

unzip job-urls.zip -d job_urls

files=$(ls job_urls/job_urls*.json | jq -R -s -c 'split("\n")[:-1] | map({"file": .})')
if [ "$files" == "[]" ]; then
  echo "No job URL chunks found"
  exit 1
fi
echo "files=$files" >> $GITHUB_OUTPUT