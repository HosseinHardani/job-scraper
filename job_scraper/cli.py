"""
Command-line interface for Job Scraper.
"""

import argparse
import sys
from .scraper import scrape_all
from .exporter import export_csv, export_json, print_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-scraper",
        description="Scrape remote job listings and export them to CSV or JSON.",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=["remoteok"],
        metavar="SOURCE",
        help="Sources to scrape (default: remoteok)",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="Filter jobs by keyword (title, company, or tags)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="N",
        help="Max jobs to fetch per source (default: 50)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        metavar="FILE",
        help="Output file path (.csv or .json)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json", "table"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between source requests (default: 1.0)",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    jobs = scrape_all(
        sources=args.sources,
        limit=args.limit,
        delay=args.delay,
    )

    if args.keyword:
        jobs = [j for j in jobs if j.matches(args.keyword)]
        print(f"Filtered to {len(jobs)} jobs matching '{args.keyword}'.")

    if not jobs:
        print("No jobs found.")
        sys.exit(0)

    if args.format == "csv":
        path = args.output or "jobs.csv"
        export_csv(jobs, path)
        print(f"Saved {len(jobs)} jobs to {path}")
    elif args.format == "json":
        path = args.output or "jobs.json"
        export_json(jobs, path)
        print(f"Saved {len(jobs)} jobs to {path}")
    else:
        print_table(jobs)


if __name__ == "__main__":
    main()
