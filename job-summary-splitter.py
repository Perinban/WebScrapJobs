# job_summary_splitter.py
import json
import requests

# ========================= Fetch Job URLs =========================
# Send a GET request to fetch the job URLs
response = requests.get("https://raw.githubusercontent.com/Perinban/WebScrapJobs/main/job_post_url.txt")

# Check if the request was successful
if response.status_code == 200:
    # Assign the content to job_post_url by splitting the response into lines
    job_post_url = response.text.splitlines()
else:
    print("Failed to retrieve the job URLs.")
    job_post_url = []

# Split into multiple files if more than 25,000 records
chunk_size = 25000
for i in range(0, len(job_post_url), chunk_size):
    chunk = job_post_url[i:i + chunk_size]
    output_file = f"job_urls_{i // chunk_size + 1}.json"  # Intermediate file naming
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(chunk, file, indent=4, ensure_ascii=False)
    print(f"Saved {output_file}")