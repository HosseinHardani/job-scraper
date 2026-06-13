"""
Export job listings to CSV, JSON, or plain table output.
"""

import csv
import json
from typing import List
from .scraper import Job


COLUMNS = ["title", "company", "location", "tags", "salary", "posted_at", "url", "source"]


def export_csv(jobs: List[Job], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for job in jobs:
            writer.writerow({k: job.to_dict()[k] for k in COLUMNS})


def export_json(jobs: List[Job], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([job.to_dict() for job in jobs], f, ensure_ascii=False, indent=2)


def print_table(jobs: List[Job]) -> None:
    col_widths = {
        "title": 35,
        "company": 20,
        "location": 15,
        "salary": 18,
        "source": 10,
    }

    header = (
        f"{'Title':<{col_widths['title']}}"
        f"{'Company':<{col_widths['company']}}"
        f"{'Location':<{col_widths['location']}}"
        f"{'Salary':<{col_widths['salary']}}"
        f"{'Source':<{col_widths['source']}}"
    )
    separator = "-" * len(header)

    print(separator)
    print(header)
    print(separator)

    for job in jobs:
        title = job.title[:col_widths["title"] - 2].ljust(col_widths["title"])
        company = job.company[:col_widths["company"] - 2].ljust(col_widths["company"])
        location = job.location[:col_widths["location"] - 2].ljust(col_widths["location"])
        salary = (job.salary or "N/A")[:col_widths["salary"] - 2].ljust(col_widths["salary"])
        source = job.source[:col_widths["source"] - 2].ljust(col_widths["source"])
        print(f"{title}{company}{location}{salary}{source}")

    print(separator)
    print(f"Total: {len(jobs)} jobs")
