import argparse
from datetime import date
import requests
from bs4 import BeautifulSoup

def parse_args():
    parser = argparse.ArgumentParser(description='Scraping script for job search.')
    parser.add_argument('-t', '--title', type=str, required=True, help='The job title to search for.')
    parser.add_argument('-l' ,'--location', type=str, required=True, help='The location to search in.')
    return parser.parse_args()

def scrape_linkedin(keywords: list, location: str = None) -> list:
    base_url = "https://www.linkedin.com/jobs/search/"
    
    jobs = []

    params = {
        "keywords": " ".join(keywords[:2]),
        "location": location,
        "f_TPR": "r604800",   # Last week
        "sortBy": "DD",       # Sort by date
        "start": "0",
        "f_WT": "1%2C3"
    }

    try:
        response = requests.get(base_url, params=params, timeout=100)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.find_all("div", class_="base-card")

        for card in job_cards:
            try:
                title_element = card.find("h3", class_="base-search-card__title")
                title_text = title_element.text.strip() 

                company_element = card.find("h4", class_="base-search-card__subtitle")
                company_text = company_element.text.strip() 

                location_element = card.find("span", class_="job-search-card__location")
                location_text = location_element.text.strip() 

                if location.lower() not in location_text.lower():
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

            except Exception:
                continue

    except requests.RequestException as e:
        raise RuntimeError(f"LinkedIn Error : {e}")

    return jobs


def main():
    args = parse_args()
    print(f"Scraping for job title: {args.title} in location: {args.location}")
    jobs = scrape_linkedin(keywords=[args.title], location=args.location)
    for job in jobs:
        print(job)

if __name__ == "__main__":
    main()
