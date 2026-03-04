import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Scraping script for job search.')
    parser.add_argument('-t', '--title', type=str, required=True, help='The job title to search for.')
    parser.add_argument('-l' ,'--location', type=str, required=True, help='The location to search in.')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    print(f"Scraping for job title: {args.job_title} in location: {args.location}")
