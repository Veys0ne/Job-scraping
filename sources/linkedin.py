import re
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup

from .base import Source, make_job, polite_get, split_location, temporal_filter

class LinkedIn(Source):
    name = "linkedin"
    base_url = "https://www.linkedin.com/jobs/search/"

    def search(self, query, keywords, location, period):
        jobs = []
    
        for loc in split_location(location):
            params = {
                "keywords": query,
                "location": loc,
                "sortBy": "DD",       # Sort by date
                "start": "0",
                "f_WT": "1,3"
            }

            if period:
                params["f_TPR"] = f"r{temporal_filter(period)}"

            url = self.base_url + "?" + urlencode(params, quote_via=quote)
            response = polite_get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for card in soup.find_all("div", class_="base-card"):
                try:
                    title_element = card.find("h3", class_="base-search-card__title")
                    title_text = title_element.text.strip() if title_element else "N/A"

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

                    m = re.search(r"(\d{8,})", link_text)
                    job_id = m.group(1) if m else link_text
                    

                    jobs.append(make_job(self.name, job_id, title_text, company_text, location_text, link_text,
                        date_element.get("datetime", "N/A") if date_element else "N/A"))

                except Exception:
                    continue
        return jobs
