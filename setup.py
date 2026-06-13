from setuptools import setup, find_packages

setup(
    name="job-scraper",
    version="1.0.0",
    description="A CLI tool to scrape and filter remote job listings",
    author="Your Name",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "job-scraper=job_scraper.cli:main",
        ],
    },
)
