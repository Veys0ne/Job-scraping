import json
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

from scraping import search_all
from filters import delete_duplicates
from sources import get_sources

# ---------- Configuration ----------
LOC = "France"
SEARCHES = [
    {"title": '("stage" OR "stagiaire" OR "intern") AND ("cyber" OR "cybersécurité" OR "cybersecurity" OR "SOC" OR "pentest")',
     "location": LOC, "week": True},
    {"title": '("cdi" OR "contrat" OR "cdd") AND ("cyber" OR "cybersécurité" OR "cybersecurity" OR "SOC" OR "pentest")',
     "location": LOC, "week": True}
]

SEEN_FILE = Path(__file__).with_name("seen_jobs.json")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
MAIL_TO = [m.strip() for m in os.environ.get("MAIL_TO", "").split(",") if m.strip()]
# -----------------------------------


def job_id(job: dict) -> str:
    """Identifiant stable : l'ID numérique LinkedIn, sinon le lien sans paramètres."""
    return job['id']


def load_seen() -> set:
    if not SEEN_FILE.exists():
        return set(), set()
    data = json.loads(SEEN_FILE.read_text())
    return set(data["jobs"]), set(data["sources"])


def save_seen(seen: set, sources: set) -> None:
    SEEN_FILE.write_text(json.dumps({"jobs": sorted(seen), "sources": sorted(sources)}))


def notify_email(jobs: list) -> None:
    lines = []
    for job in jobs:
        lines.append(
            f"[{job['source']}] {job['title']}\n"
            f"  {job['company']} - {job['location']}\n"
            f"  {job['link'].split('?')[0]}\n"
        )
    body = "\n".join(lines)

    if not (SMTP_USER and SMTP_PASSWORD and MAIL_TO):
        print(body)  # mode test sans mail
        return

    msg = EmailMessage()
    msg["Subject"] = f"{len(jobs)} nouvelle(s) offre(s)"
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(MAIL_TO)
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def main() -> None:
    seen, known_sources = load_seen()
    sources = get_sources()
    ok_sources = set()
    new_jobs, silent = [], 0

    for s in SEARCHES:
        jobs = search_all(s["title"], s["location"], s.get("period"), s.get("keywords"), sources, ok_sources)
        for job in jobs:
            jid = job_id(job)
            if jid in seen:
                continue
            seen.add(jid)
            if job["source"] in known_sources:
                new_jobs.append(job)
            else:
                silent += 1
    if silent:
            print(f"Initialisation de nouvelles sources : {silent} offres mémorisées, sans notifications.")

    new_jobs = delete_duplicates(new_jobs)
    if new_jobs:
        notify_email(new_jobs)
    print(f"{len(new_jobs)} nouvelle(s) offre(s) notifiée(s).")

    save_seen(seen, known_sources | ok_sources)


if __name__ == "__main__":
    main()