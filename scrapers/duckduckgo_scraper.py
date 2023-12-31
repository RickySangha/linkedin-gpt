from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
import time
import random
import pandas as pd

from .base_scraper import BaseScraper
from .scraper_config import ScraperConfig


class DuckDuckGoScraper(BaseScraper):
    def __init__(self, config: ScraperConfig):
        super().__init__(config)

    def get_html(self, query):
        self.create_chrome_driver()

        url = f"https://duckduckgo.com/?va=k&t=hp&q={query}&ia=web"
        self.driver.get(url)

        try:
            # Add random wait time before each scrape
            time.sleep(random.uniform(2, 5))

            # Wait for the core section container to load
            section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div[2]/div[5]/div[4]/div/div/div/div/section[1]/ol",
                    )
                )
            )
            return section.get_attribute("innerHTML")
        except Exception as e:
            print(f"HTTP error occurred: {e}")
            return None

    def parse_linkedin_url(self, html):
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        # Find the first <ol> tag with the class 'react-results--main'
        search_results = soup.find_all("li", {"data-layout": "organic"})

        if search_results:
            # Iterate through each <li> tag in the ordered list
            for result in search_results:
                # Find the <a> tag with the LinkedIn URL
                link = result.find("a", href=True, class_="Rn_JXVtoPVAFyGkcaXyK")
                if link and "linkedin.com/company" in link["href"]:
                    return link["href"]

        return None

    def get_linkedin_url(self, company):
        try:
            html = self.get_html(f"{company}+LinkedIn")
            linkedin_url = self.parse_linkedin_url(html)
            if linkedin_url:
                return linkedin_url
            else:
                error_message = "LinkedIn URL not found"
                return {"error": error_message}
        except Exception as e:
            error_message = f"Error occurred while getting LinkedIn URL: {e}"
            return {"error": error_message}

    def update_csv_with_linkedin_urls(
        self,
        csv_file,
        output_file="data/updated/Software, $1M-$10M,1-19-LinkedIn-URLs.csv",
    ):
        # TODO: if outfile file already exist send an alert asking if your sure you want to over-write. If not specify different name.

        df = pd.read_csv(csv_file)
        # df["LinkedIn URL"] = None  # Create a new column for LinkedIn URLs
        # df["Error"] = None  # Create a new column for recording errors

        if not df["Company linkedin url"]:
            for index, row in df.iterrows():
                try:
                    company_url = row["Company domain"]
                    linkedin_url = self.get_linkedin_url(company_url)
                    if linkedin_url:
                        df.at[index, "Company linkedin url"] = linkedin_url
                    else:
                        df.at[index, "Error"] = "LinkedIn URL not found"
                except Exception as e:
                    print(f"Error occurred: {e}")
                    df.at[index, "Error"] = str(e)  # Record the error in the CSV
                finally:
                    df.to_csv(
                        output_file, index=False
                    )  # Save progress after each company
                    print(linkedin_url)

    @staticmethod
    def load_user_agents():
        user_agents = []
        with open("user_agents.txt", "r") as file:
            for line in file:
                if line.strip():
                    user_agents.append(line.strip())
        return user_agents


# Example Usage
# config = ScraperConfig(use_proxy=False)
# scraper = DuckDuckGoScraper(config)
# scraper.update_csv_with_linkedin_urls("data/raw/Software, $1M-$10M,1-19.csv")
