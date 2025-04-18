import json
import glob
import os

def combine_job_summaries():
    combined_data = []

    # Ensure the folder exists
    folder_path = 'job-summaries'
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Iterate over all the directories and look for JSON files
    for dir_path in glob.glob(os.path.join(folder_path, 'job-summary*')):
        if os.path.isdir(dir_path):  # Only process directories
            # Look for JSON files inside each directory
            for file in glob.glob(os.path.join(dir_path, '*.json')):
                if os.path.isfile(file):  # Ensure it's a file, not a directory
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            combined_data.extend(json.load(f))
                        print(f"Successfully loaded data from {file}")
                    except Exception as e:
                        print(f"Error reading {file}: {e}")
                else:
                    print(f"Skipping {file}, as it is not a file.")

    if combined_data:
        # Write the combined data into a single job_summary.json file in the current directory
        try:
            with open('./job_summary.json', 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=4, ensure_ascii=False)
            print('Combined job_summary.json created in the current directory.')
        except Exception as e:
            print(f"Error writing to job_summary.json: {e}")
    else:
        print("No data to combine.")

if __name__ == "__main__":
    combine_job_summaries()