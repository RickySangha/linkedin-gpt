import pandas as pd
from scraper_config import ScraperConfig
from linkedin_scraper import LinkedInScraper


def scrape_companies_from_urls(input_csv_path):
    # Configuration and output CSV path
    config = ScraperConfig(use_proxy=False)
    output_csv_path = "data/updated/Software, $1M-$10M,1-19-About-us.csv"

    # Initialize Scraper
    scraper = LinkedInScraper(config)

    # Read CSV into DataFrame
    df = pd.read_csv(input_csv_path)

    # Scrape data for each URL and handle errors
    for index, row in df.iterrows():
        try:
            url = row["LinkedIn URL"]  # Assuming 'URL' is the column name for URLs
            if url:
                company_data = scraper.get_company_data(url)
                # Update existing columns or add new ones
                # df.at[index, "Company name"] = company_data.get("name", "N/A")
                # df.at[index, "Company domain"] = company_data.get("website", "N/A")
                # df.at[index, "Company industry"] = company_data.get("industry", "N/A")
                # df.at[index, "Company employees"] = company_data.get("company_size", "N/A")
                # df.at[index, "Headquarters"] = company_data.get("headquarters", "N/A")
                # df.at[index, "Type"] = company_data.get("type", "N/A")
                # df.at[index, "Founded"] = company_data.get("founded", "N/A")
                # df.at[index, "Specialties"] = company_data.get("specialties", "N/A")
                df.at[index, "About us"] = company_data.get("about_us", "N/A")
                df.at[index, "Error"] = ""  # No error
            else:
                df.at[index, "About us"] = "No LinkedIn URL"  # No error
        except Exception as e:
            print(f"Error occurred: {e}")
            df.at[index, "Error"] = str(e)  # Log the error
        finally:
            print(index)
            df.to_csv(
                output_csv_path, index=False
            )  # Append without header for subsequent rows


# Example Usage
scrape_companies_from_urls(
    "data/updated/Software, $1M-$10M,1-19-LinkedIn-URLs (final).csv"
)
