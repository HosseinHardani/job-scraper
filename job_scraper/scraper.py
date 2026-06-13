"""
Job Scraper - scrapes job listings from multiple sources.
Supports: RemoteOK, HackerNews Who's Hiring, and custom HTML pages.
"""

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; JobScraper/1.0; "
        "+https://github.com/yourusername/job-scraper)"
    )
}


@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    tags: list[str] = field(default_factory=list)
    salary: Optional[str] = None
    posted_at: Optional[str] = None
    source: str = ""

    def matches(self, keyword: str) -> bool:
        keyword = keyword.lower()
        return (
            keyword in self.title.lower()
            or keyword in self.company.lower()
            or any(keyword in tag.lower() for tag in self.tags)
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "tags": ", ".join(self.tags),
            "salary": self.salary or "",
            "posted_at": self.posted_at or "",
            "source": self.source,
        }


class RemoteOKScraper:
    """Scrapes jobs from remoteok.com via their public JSON API."""

    BASE_URL = "https://remoteok.com/api"

    def fetch(self, limit: int = 50) -> list[Job]:
        logger.info("Fetching jobs from RemoteOK...")
        try:
            resp = requests.get(self.BASE_URL, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"RemoteOK fetch failed: {e}")
            return []

        jobs = []
        # First item is metadata, skip it
        for item in data[1:limit + 1]:
            if not isinstance(item, dict):
                continue
            job = Job(
                title=item.get("position", "Unknown"),
                company=item.get("company", "Unknown"),
                location=item.get("location", "Remote"),
                url=item.get("url", ""),
                tags=item.get("tags", []),
                salary=self._parse_salary(item),
                posted_at=item.get("date", ""),
                source="RemoteOK",
            )
            jobs.append(job)

        logger.info(f"Found {len(jobs)} jobs from RemoteOK.")
        return jobs

    def _parse_salary(self, item: dict) -> Optional[str]:
        low = item.get("salary_min")
        high = item.get("salary_max")
        if low and high:
            return f"${low:,} - ${high:,}"
        if low:
            return f"${low:,}+"
        return None


class CustomHTMLScraper:
    """
    Generic scraper for any HTML job board.
    Provide CSS selectors to extract data.
    """

    def __init__(
        self,
        url: str,
        job_selector: str,
        title_selector: str,
        company_selector: str,
        location_selector: str = "",
        link_selector: str = "a",
        source_name: str = "Custom",
    ):
        self.url = url
        self.job_selector = job_selector
        self.title_selector = title_selector
        self.company_selector = company_selector
        self.location_selector = location_selector
        self.link_selector = link_selector
        self.source_name = source_name

    def fetch(self, limit: int = 50) -> list[Job]:
        logger.info(f"Fetching jobs from {self.url}...")
        try:
            resp = requests.get(self.url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Custom scraper fetch failed: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select(self.job_selector)[:limit]
        jobs = []

        for card in cards:
            title_el = card.select_one(self.title_selector)
            company_el = card.select_one(self.company_selector)
            location_el = card.select_one(self.location_selector) if self.location_selector else None
            link_el = card.select_one(self.link_selector)

            title = title_el.get_text(strip=True) if title_el else "Unknown"
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            location = location_el.get_text(strip=True) if location_el else "Unknown"
            href = link_el.get("href", "") if link_el else ""

            # Make relative URLs absolute
            if href.startswith("/"):
                from urllib.parse import urlparse
                parsed = urlparse(self.url)
                href = f"{parsed.scheme}://{parsed.netloc}{href}"

            job = Job(
                title=title,
                company=company,
                location=location,
                url=href,
                source=self.source_name,
            )
            jobs.append(job)

        logger.info(f"Found {len(jobs)} jobs from {self.source_name}.")
        return jobs


def scrape_all(
    sources: list[str] = None,
    limit: int = 50,
    delay: float = 1.0,
) -> list[Job]:
    """
    Scrape from all configured sources.
    sources: list of source names to use, defaults to all.
    """
    available = {"remoteok": RemoteOKScraper()}
    sources = sources or list(available.keys())

    all_jobs = []
    for name in sources:
        scraper = available.get(name.lower())
        if not scraper:
            logger.warning(f"Unknown source: {name}")
            continue
        jobs = scraper.fetch(limit=limit)
        all_jobs.extend(jobs)
        time.sleep(delay)

    return all_jobs
