from scrapers.scraper_config import ScraperConfig
from scrapers.linkedin_scraper import LinkedInScraper
from scripts.csv_helpers import read_urls_from_csv, write_data_to_csv


def scrape_candidates_from_urls(input_csv_path):
    # Configuration and CSV paths
    config = ScraperConfig(use_proxy=False)

    output_csv_path = "data/candidates.csv"
    csv_header = [
        "Name",
        "Website",
        "Industry",
        "Company Size",
        "Headquarters",
        "Type",
        "Founded",
        "Specialties",
        "About Us",
        "Error",
    ]

    # Initialize Scraper
    scraper = LinkedInScraper(config)
    urls = read_urls_from_csv(input_csv_path)
    scraped_data = []

    # Scrape data for each URL and handle errors
    for url in urls:
        try:
            candidate_data = scraper.get_company_data(url)
            record = [
                candidate_data.get("name", "N/A"),
                candidate_data.get("website", "N/A"),
                candidate_data.get("industry", "N/A"),
                candidate_data.get("company_size", "N/A"),
                candidate_data.get("headquarters", "N/A"),
                candidate_data.get("type", "N/A"),
                candidate_data.get("founded", "N/A"),
                candidate_data.get("specialties", "N/A"),
                candidate_data.get("about_us", "N/A"),
                "",  # No error
            ]
        except Exception as e:
            record = [url] + [""] * (len(csv_header) - 2) + [str(e)]  # Log the error
        finally:
            scraped_data.append(record)
            write_data_to_csv(
                output_csv_path, scraped_data, csv_header
            )  # Save after each scrape
