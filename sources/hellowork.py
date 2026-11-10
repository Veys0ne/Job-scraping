import os
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import Source, make_job, polite_get, split_location

DEBUG = False

# Une annonce = un lien du type /fr-fr/emplois/12345678.html
LINK_RE = re.compile(r"/emplois/(\d+)\.html")

# À VÉRIFIER : valeur du paramètre de date dans l'URL après avoir filtré sur le site
DATE_PARAM = {"day": "d", "week": "w", "month": "m"}

# https://www.hellowork.com/fr-fr/emploi/recherche.html?k=chimiste&k_autocomplete=&l=france&l_autocomplete=
class HelloWork(Source):
    name = "hellowork"
    BASE = "https://www.hellowork.com"
    SEARCH_URL = BASE + "/fr-fr/emploi/recherche.html"

    def search(self, query, keywords, location, period):
        jobs, seen_ids = [], set()
        for kw in keywords:
            for loc in split_location(location):
                params = {"k": kw}
                if loc.lower() != "france":      # "France" = pas de filtre de lieu
                    params["l"] = loc
                if period:
                    params["d"] = DATE_PARAM[period]

                response = polite_get(self.SEARCH_URL, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                for a in soup.find_all("a", href=LINK_RE):
                    job_id = LINK_RE.search(a["href"]).group(1)
                    if job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    # À VÉRIFIER : structure d'une carte (titre / entreprise / lieu)
                    card = a.find_parent(["li", "article"]) or a.parent
                    if DEBUG and len(seen_ids) == 1:
                        print(card.prettify()[:3000])

                    heading = card.find(["h2", "h3"])
                    title = (heading or a).get_text(" ", strip=True)
                    if not title:
                        continue
                    lines = [t for t in card.stripped_strings if t != title]
                    company = lines[0] if lines else "N/A"
                    location_text = lines[1] if len(lines) > 1 else "N/A"

                    jobs.append(make_job(
                        self.name, job_id, title, company, location_text,
                        urljoin(self.BASE, a["href"]).split("?")[0],
                    ))
        return jobs