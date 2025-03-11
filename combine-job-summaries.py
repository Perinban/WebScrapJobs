import json
import glob
import os

def combine_job_summaries():
    combined_data = []

    # Iterate over all the job summary JSON files in the unzipped folder
    for file in glob.glob('job_summary_files/job_summary_*.json'):
        with open(file, 'r', encoding='utf-8') as f:
            combined_data.extend(json.load(f))

    # Write the combined data into a single job_summary.json file
    with open('job_summary.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4, ensure_ascii=False)

    print('Combined job_summary.json created.')


if __name__ == "__main__":
    combine_job_summaries()