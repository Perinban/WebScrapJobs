import asyncio
import random
import json
import requests
import nest_asyncio
from bs4 import BeautifulSoup
import aiohttp

# ========================= Fetch Job URLs =========================
# Send a GET request to fetch the job URLs
response = requests.get("https://raw.githubusercontent.com/Perinban/WebScrapJobs/main/job_post_url.txt")

# Check if the request was successful
if response.status_code == 200:
    # Assign the content to job_post_url by splitting the response into lines
    job_post_url = response.text.splitlines()
else:
    print("Failed to retrieve the job URLs.")

# Apply nest_asyncio to handle nested event loops, useful in interactive environments like Jupyter notebooks
nest_asyncio.apply()

# Define request headers to mimic a real browser and avoid bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
    "Accept-Language": "en-US,en;q=0.9"
}

# Set up a semaphore to limit concurrent requests, preventing server bans
SEMAPHORE = asyncio.Semaphore(10)

# Lock to ensure progress updates safely without race conditions
progress_lock = asyncio.Lock()

# ========================= Job Details Extraction Function =========================
async def extract_job_details(session, url, progress, total_urls):
    """Extracts job details from a given job posting URL."""
    async with SEMAPHORE:  # Limit concurrent requests
        reject_reason = None  # Default rejection reason

        try:
            # Send an asynchronous GET request with headers and timeout handling
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status != 200:
                    reject_reason = f"HTTP {response.status} on {url}"
                    return {"reject_reason": reject_reason}

                # Parse HTML response using BeautifulSoup
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract job URL (same as input URL)
                job_url = url

                # Extract company name if available
                company_name = soup.find('span').text.strip() if soup.find('span') else None

                # Extract company logo URL if an image is present
                logo_img = soup.find('img')
                logo_url = 'https:' + logo_img['src'] if logo_img else None

                # Extract job title if available
                job_title = soup.find('h1').text.strip() if soup.find('h1') else None

                # Extract additional job details (location, type, domain, salary)
                job_info_divs = soup.find_all('div', class_=lambda x: x and 'JobTopperData' in x)
                job_info_val = [div for div in job_info_divs if div.find_previous_sibling('i')]

                location, job_type, job_domain, job_salary = None, None, None, None

                for div in job_info_val:
                    prev_i_tag = div.find_previous_sibling('i')  # Identify the corresponding icon
                    svg_tag = prev_i_tag.find('svg') if prev_i_tag else None

                    if svg_tag:
                        icon_name = svg_tag.get('name')
                        if icon_name == 'LocationPinIcon':
                            location = div.text.strip()
                        elif icon_name == 'BriefcaseIcon':
                            job_type = div.text.strip()
                        elif icon_name == 'FolderIcon':
                            job_domain = div.text.strip()
                        elif icon_name == 'SalaryIcon':
                            job_salary = div.text.strip()

                # Extract 'about-job' section
                about_job_section = soup.find('div', id='about-job')
                sectioned_content = []

                if about_job_section:
                    first_tag = about_job_section.find(['p', 'h2'])
                    if first_tag:
                        parent_div = first_tag.find_parent('div')
                        target_div_content = parent_div.get_text(separator="\n").strip()
                        sectioned_content.append({"header": "About the Company", "content": target_div_content})

                        # Iterate through job description sections
                        current_tag = parent_div.find_next_sibling(['h2', 'p'])
                        while current_tag:
                            header_text = current_tag.get_text(strip=True)
                            next_div = current_tag.find_next_sibling('div')
                            if next_div:
                                div_content = "\n".join(
                                    element.get_text(separator="\n").strip()
                                    for element in next_div.contents if element.name in ["p", "ul"]
                                )
                                sectioned_content.append({"header": header_text, "content": div_content})
                            current_tag = current_tag.find_next_sibling(['h2', 'p'])

                # Extract last updated timestamp
                footer = soup.find('div', class_=lambda x: x and 'Meta-elements' in x and 'StyledFlex' in x)
                last_updated_time = footer.find('div').text.strip() if footer else None

                # Safely update progress with a lock to avoid race conditions
                async with progress_lock:
                    progress[0] += 1
                    print(f"Processed {progress[0]}/{total_urls} URLs")

                return {
                    "Company_Name": company_name,
                    "Company_Logo_Url": logo_url,
                    "Job_URL": job_url,
                    "Job_Title": job_title,
                    "Job_Location": location,
                    "Job_Status": job_type,
                    "Job_Domain": job_domain,
                    "Job_Salary": job_salary,
                    "Job_Details": sectioned_content,
                    "Last_Updated": last_updated_time,
                    "reject_reason": reject_reason
                }

        except asyncio.TimeoutError:
            reject_reason = f"Timeout on {url}"
        except Exception as e:
            reject_reason = f"Failed to process {url}: {str(e)}"
        finally:
            await asyncio.sleep(random.uniform(2, 5))  # Random delay to prevent detection

        return {"reject_reason": reject_reason}

# ========================= Process URLs in Parallel =========================
async def process_all_urls(urls):
    """Processes all job URLs concurrently and returns extracted job details."""
    progress = [0]  # Mutable container for tracking progress
    total_urls = len(urls)
    results = []

    # Use aiohttp session for efficient asynchronous requests
    async with aiohttp.ClientSession() as session:
        tasks = [extract_job_details(session, url, progress, total_urls) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    return results

# ========================= Main Execution =========================
if __name__ == "__main__":
    # Run the asynchronous job processing function
    job_summary = asyncio.run(process_all_urls(job_post_url))

    # ========================= Overwrite with New Job Summary Data =========================
    update_response = requests.put(raw_url, data=json.dumps(job_summary, indent=4, ensure_ascii=False))

    # Check for success in updating
    try:
        update_response.raise_for_status()  # Raise an exception if the response status is not OK
        print("New job summary saved successfully to GitHub.")
    except requests.RequestException as e:
        print(f"Failed to save new job summary to GitHub: {e}")