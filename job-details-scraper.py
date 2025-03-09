# job-details-scraper.py
import asyncio
import random
import json
import requests
import nest_asyncio
from bs4 import BeautifulSoup
import aiohttp
import os
import sys

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

async def extract_job_details(session, url, progress, total_urls):
    async with SEMAPHORE:
        reject_reason = None
        try:
            async with session.get(url, headers=HEADERS, timeout=10) as response:
                if response.status != 200:
                    reject_reason = f"HTTP {response.status} on {url}"
                    return {"reject_reason": reject_reason}
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                job_url = url
                company_name = soup.find('span').text.strip() if soup.find('span') else None
                logo_img = soup.find('img')
                logo_url = 'https:' + logo_img['src'] if logo_img else None
                job_title = soup.find('h1').text.strip() if soup.find('h1') else None
                job_info_divs = soup.find_all('div', class_=lambda x: x and 'JobTopperData' in x)
                job_info_val = [div for div in job_info_divs if div.find_previous_sibling('i')]
                location, job_type, job_domain, job_salary = None, None, None, None
                for div in job_info_val:
                    prev_i_tag = div.find_previous_sibling('i')
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
                about_job_section = soup.find('div', id='about-job')
                sectioned_content = []
                if about_job_section:
                    first_tag = about_job_section.find(['p', 'h2'])
                    if first_tag:
                        parent_div = first_tag.find_parent('div')
                        target_div_content = parent_div.get_text(separator="\n").strip()
                        sectioned_content.append({"header": "About the Company", "content": target_div_content})
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
                footer = soup.find('div', class_=lambda x: x and 'Meta-elements' in x and 'StyledFlex' in x)
                last_updated_time = footer.find('div').text.strip() if footer else None
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
            await asyncio.sleep(random.uniform(2, 5))
        return {"reject_reason": reject_reason}

async def process_all_urls(job_urls):
    progress = [0]
    total_urls = len(job_urls)
    async with aiohttp.ClientSession() as session:
        tasks = [extract_job_details(session, url, progress, total_urls) for url in job_urls]
        results = await asyncio.gather(*tasks)
    return results

async def process_single_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        job_urls = json.load(file)
    results = await process_all_urls(job_urls)
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
    print(f"Processed and saved {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python job-details-scraper.py <input_file> <output_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    asyncio.run(process_single_file(input_file, output_file))