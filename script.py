import os
import random
import json
import asyncio
import aiohttp
import cloudscraper
import logging
import requests
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ========================= Setup Logging =========================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========================= Download Existing Data =========================
RAW_URL = os.getenv("RAW_URL", "https://raw.githubusercontent.com/Perinban/join_companies/main/websites.json")
existing_data = []

try:
    response = requests.get(RAW_URL, timeout=10)
    response.raise_for_status()
    existing_data = response.json()
    company_list = [entry["company_name"] for entry in existing_data]
except requests.exceptions.RequestException as e:
    logger.error(f"Failed to fetch data from GitHub: {e}")
    company_list = []

# ========================= Process Extracted Company Names =========================
unique_company_list = list(set(company_list))
logger.info(f"Extracted {len(unique_company_list)} unique company names.")

# ========================= Setup Session with Headers =========================
session = cloudscraper.create_scraper()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
    "Accept-Language": "en-US,en;q=0.9"
}


# ========================= Extract Job Links =========================
def extract_job_links(soup):
    return [link.get('href') for link in
            soup.find_all('a', class_=lambda x: x and 'JobTile' in x and 'JobLink' in x, attrs={'data-testid': 'Link'})]


# ========================= Extract All Job Links =========================
def extract_all_job_links(company_name):
    url = f'https://join.com/companies/{company_name}'
    all_job_links = []
    page = 1

    while True:
        try:
            response = session.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            job_links = extract_job_links(soup)
            all_job_links.extend(job_links)

            next_page_link = soup.find('a', attrs={'aria-label': 'Next page'})
            if next_page_link:
                page += 1
                url = f'https://join.com/companies/{company_name}?page={page}'
            else:
                break

            time.sleep(random.uniform(2, 5))  # Randomized delay to avoid rate-limiting
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching jobs for {company_name}: {e}")
            break

    return all_job_links

# ========================= Scrape Job Links =========================
def scrape_company(company_name):
    logger.info(f"Scraping jobs for {company_name}...")
    job_links = extract_all_job_links(company_name)
    logger.info(f"Found {len(job_links)} job links for {company_name}")
    return job_links

# ========================= Execute Scraping in Parallel =========================
job_post_url = []

JOB_POST_URL_SOURCE = "https://raw.githubusercontent.com/Perinban/WebScrapJobs/main/job_post_url.txt"

try:
    response = requests.get(JOB_POST_URL_SOURCE, timeout=10)
    response.raise_for_status()
    job_post_url = response.text.splitlines()
except requests.exceptions.RequestException as e:
    logger.error(f"Failed to fetch job post URLs from GitHub: {e}")

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(scrape_company, company_name): company_name for company_name in unique_company_list}

    for future in as_completed(futures):
        company_name = futures[future]
        try:
            job_post_url.extend(future.result())
        except Exception as e:
            logger.error(f"Error scraping {company_name}: {e}")

# ========================= Save Extracted Job Links to File =========================
output_file = "job_post_url.txt"
with open(output_file, "w") as file:
    for url in job_post_url:
        file.write(url + "\n")

logger.info(f"Job post URLs saved successfully to {output_file}.")