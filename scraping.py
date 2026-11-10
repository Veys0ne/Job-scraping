import argparse
import sys

from filters import delete_duplicates, filter_jobs
from sources import ALL_SOURCES, get_sources

BOLD = "\033[1m"
CLASSIC = "\033[0m"
LINK = "\033[2m"

def parse_args():
    parser = argparse.ArgumentParser(description='Scraping script for job search.')
    parser.add_argument('-t', '--title', type=str, required=True, help='The job title to search for.')
    parser.add_argument('-l' ,'--location', type=str, required=True, help='The location to search in, comma separated.')
    parser.add_argument('-k', '--keywords', type=str, help="Simple keywords sent to non-boolean sites, comma seperated (default: the title)")
    parser.add_argument('-s', '--sources', type=str, help=f'comma separated, among {", ".join(ALL_SOURCES)} (default: all).')
    parser.add_argument('-d', '--day', action='store_true', help='Search for jobs posted in the last 24 hours.')
    parser.add_argument('-w', '--week', action='store_true', help='Search for jobs posted in the last week.')
    parser.add_argument('-m', '--month', action='store_true', help='Search for jobs posted in the last month.')
    return parser.parse_args()



def period_from_args(args):
    if args.day:
        return "day"  
    elif args.week:
        return "week"  
    elif args.month:
        return "month" 
    else:
        return None

def search_all(query, location, period=None, keywords=None, sources=None, ok=None) -> list:
    """Ask each sources one by one. If one sources fails, it doesn't impact the other sources"""
    jobs = []
    for src in (sources if sources is not None else get_sources()):
        try:
            found = src.search(query, keywords or [query], location, period)
        except Exception as e:
            print(f"[{src.name}] error : {e}, file=sys.stderr")
            continue
        if ok is not None:
            ok.add(src.name)
        found = filter_jobs(found, query)
        print(f"[{src.name}] {len(found)} offre(s)")
        jobs += found
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
    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else None
    names = [s.strip() for s in args.sources.split(",")] if args.sources else None
    
    jobs = search_all(args.title, args.location, period_from_args(args), keywords, get_sources(names))
    jobs = delete_duplicates(jobs) 
    print(f"\nafter deleting duplicates, {len(jobs)} jobs found: ")
    display_jobs(jobs)
 
if __name__ == "__main__":
    main()