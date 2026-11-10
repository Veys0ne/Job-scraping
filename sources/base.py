import random
import time
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.5",
}

def split_location(location):
    return [l.strip() for l in location.split(",") if l.strip()]

def temporal_filter(period):
    if period == "day":
        return "r86400"  # Last 24 hours
    elif period == "week":
        return "r604800"  # Last week
    elif period == "month":
        return "r2592000" # Last month
    else:
        return None

def polite_get(url, **kwargs):
    """GET avec User-Agent, timeout et petite pause aléatoire."""
    time.sleep(random.uniform(1.0, 3.0))
    kwargs.setdefault("headers", HEADERS)
    kwargs.setdefault("timeout", 30)
    return requests.get(url, **kwargs)

def make_job(source, id, title, company=None, location=None, link=None, date=None):
    return {
            "source": source,
            "title": title,
            "company": company,
            "location": location,
            "link": link,
            "date": date,
            "id": str(id)
        }

class Source:

    @classmethod
    def enabled(cls) -> bool:
        """False si la source ne peut pas tourner"""
        return True

    def search(self, query: str, keywords: list, location: str, period: str | None):
        """
        query    : expression booléenne complète (sert au filtrage local ; LinkedIn la comprend aussi)
        keywords : termes simples à envoyer aux sites qui ne gèrent pas le booléen
        period   : "day" | "week" | "month" | None
        Renvoie des dicts : source, id, title, company, location, link, date.
        """
        raise NotImplementedError