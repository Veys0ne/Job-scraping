import argparse
from datetime import date
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote
import re

BOLD = "\033[1m"
CLASSIC = "\033[0m"
LINK = "\033[2m"

# for LinkedIn scraping, we need to set a user-agent to mimic a real browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

def parse_args():
    parser = argparse.ArgumentParser(description='Scraping script for job search.')
    parser.add_argument('-t', '--title', type=str, required=True, help='The job title to search for.')
    parser.add_argument('-l' ,'--location', type=str, required=True, help='The location to search in.')
    return parser.parse_args()

def filter_jobs(jobs: list, query: str) -> list:
    def tokenize(q):
        return re.findall(r'"[^"]*"|AND|OR|NOT|\(|\)|\S+', q)

    def parse(tokens, i=0):
        left, i = parse_and(tokens, i)
        while i < len(tokens) and tokens[i] == "OR":
            right, i = parse_and(tokens, i + 1)
            left = ("OR", left, right)
        return left, i

    def parse_and(tokens, i):
        left, i = parse_atom(tokens, i)
        while i < len(tokens) and tokens[i] == "AND":
            right, i = parse_atom(tokens, i + 1)
            left = ("AND", left, right)
        return left, i

    def parse_atom(tokens, i):
        if tokens[i] == "NOT":
            child, i = parse_atom(tokens, i + 1)
            return ("NOT", child), i
        if tokens[i] == "(":
            expr, i = parse(tokens, i + 1)
            return expr, i + 1 
        return ("WORD", tokens[i].strip('"').lower()), i + 1

    def match(node, text):
        if node[0] == "WORD": return node[1] in text
        if node[0] == "AND":  return match(node[1], text) and match(node[2], text)
        if node[0] == "OR":   return match(node[1], text) or match(node[2], text)
        if node[0] == "NOT":  return not match(node[1], text)

    tree, _ = parse(tokenize(query))
    return [job for job in jobs if match(tree, job["title"].lower())]


def create_url(params, base_url):
    return base_url + "?" + urlencode(params, quote_via=quote)


def scrape_linkedin(title: str, location: list) -> list:
    base_url = "https://www.linkedin.com/jobs/search/"
    
    jobs = []

    for loc in location.replace(" ", "").split(","):
        cpt = 0
        params = {
            "keywords": title,
            "location": loc,
            "f_TPR": "r604800",   # Last week
            # "f_TPR": "r86400",    # Last 24 hours
            "sortBy": "DD",       # Sort by date
            "start": "0",
            "f_WT": "1,3"
        }

        url = create_url(params, base_url)

        try:
            response = requests.get(url, headers=HEADERS, timeout=100)
            print(f"LinkedIn URL: {response.url}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            job_cards = soup.find_all("div", class_="base-card")

            for card in job_cards:
                try:
                    title_element = card.find("h3", class_="base-search-card__title")
                    title_text = title_element.text.strip() if title_element else "N/A"

                    if "stage" in title.lower() or "stagiaire" in title.lower() or "intern" in title.lower():
                        if "stage" not in title_text.lower() and "stagiaire" not in title_text.lower() and "intern" not in title_text.lower():
                            continue

                    company_element = card.find("h4", class_="base-search-card__subtitle")
                    company_text = company_element.text.strip() if company_element else "N/A"

                    location_element = card.find("span", class_="job-search-card__location")
                    location_text = location_element.text.strip() if location_element else "N/A"

                    if loc.lower() not in location_text.lower():
                        continue
                        
                    link_element = card.find("a", class_="base-card__full-link")
                    link_text = link_element.get("href", "N/A") 

                    date_element = card.find("time")
                    date_text = date_element.get("datetime", "N/A")
                    

                    jobs.append({
                        "source": "LinkedIn",
                        "title": title_text,
                        "company": company_text,
                        "location": location_text,
                        "link": link_text,
                        "date": date_text,
                    })
                    cpt += 1

                except Exception:
                    continue

        except requests.RequestException as e:
            raise RuntimeError(f"LinkedIn Error : {e}")
        print(f"Found {cpt} jobs in {loc}")

    return jobs

def display_jobs(jobs):
    for idx, job in enumerate(jobs, 1):
        print(f"{BOLD}[{idx}]. {job['title']}{CLASSIC}")
        print(f"\t{job['company']}")
        print(f"\t{job['location']}")
        print(f"\tLink: {LINK}{job['link']}{CLASSIC}\n")

def main():
    args = parse_args()
    print(f"Scraping for job title: {args.title} in location: {args.location}\n")
    jobs = scrape_linkedin(title=args.title, location=args.location)
    jobs = filter_jobs(jobs, args.title)
    display_jobs(jobs)
 
if __name__ == "__main__":
    main()