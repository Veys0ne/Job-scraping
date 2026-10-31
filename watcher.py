import json
import os
import re
import sys
from argparse import Namespace
from pathlib import Path
import smtplib
from email.message import EmailMessage

from scraping import scrape_linkedin, filter_jobs 

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
    link = job["link"].split("?")[0]
    m = re.search(r"(\d{8,})", link)
    return m.group(1) if m else link


def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set) -> None:
    SEEN_FILE.write_text(json.dumps(sorted(seen)))


def notify_email(jobs: list) -> None:
    lines = []
    for job in jobs:
        lines.append(
            f"{job['title']}\n"
            f"  {job['company']} - {job['location']}\n"
            f"  {job['link'].split('?')[0]}\n"
        )
    body = "\n".join(lines)

    if not (SMTP_USER and SMTP_PASSWORD and MAIL_TO):
        print(body)  # mode test sans mail
        return

    msg = EmailMessage()
    msg["Subject"] = f"{len(jobs)} nouvelle(s) offre(s) LinkedIn"
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(MAIL_TO)
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def main() -> None:
    first_run = not SEEN_FILE.exists()
    seen = load_seen()
    new_jobs = []

    for s in SEARCHES:
        args = Namespace(
            title=s["title"],
            location=s["location"],
            day=s.get("day", False),
            week=s.get("week", False),
            month=s.get("month", False),
        )
        try:
            jobs = filter_jobs(scrape_linkedin(args), args.title)
        except Exception as e:
            print(f"Erreur sur la recherche {s['title']!r} : {e}", file=sys.stderr)
            continue

        for job in jobs:
            jid = job_id(job)
            if jid not in seen:
                seen.add(jid)
                new_jobs.append(job)

    # Premier lancement : on mémorise l'existant sans spammer
    if first_run:
        print(f"Initialisation : {len(new_jobs)} offres mémorisées, aucune notification.")
    else:
        if new_jobs:
            notify_email(new_jobs)
        print(f"{len(new_jobs)} nouvelle(s) offre(s) notifiée(s).")

    save_seen(seen)


if __name__ == "__main__":
    main()