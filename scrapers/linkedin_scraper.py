from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import random
import time
import pickle
from urllib.parse import urlparse

from scrapers.base_scraper import BaseScraper
from scrapers.scraper_config import ScraperConfig


class LinkedInScraper(BaseScraper):
    def __init__(self, config: ScraperConfig):
        super().__init__(config)

    def get_company_data(self, url):
        if not url:
            return {"error": "No URL provided"}

        # Validate the URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {"error": "Incorrect URL format"}

        self.create_chrome_driver()
        self.driver.get(url)

        # Initialize a dictionary with default values
        company_data = {
            "name": "N/A",
            "website": "N/A",
            "industry": "N/A",
            "company_size": "N/A",
            "headquarters": "N/A",
            "type": "N/A",
            "founded": "N/A",
            "specialties": "N/A",
            "about_us": "N/A",
        }

        try:
            # Add random wait time before each scrape
            time.sleep(random.uniform(2, 5))

            # Wait for the core section container to load
            section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/main/section[1]/div/section[1]/div")
                )
            )

            h1 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/main/section[1]/section/div/div[2]/div[1]/h1",
                    )
                )
            )
            company_data["name"] = h1.text

            # Get the HTML content of the section element
            section_html = section.get_attribute("outerHTML")

            # Parse the HTML with Beautiful Soup
            soup = BeautifulSoup(section_html, "html.parser")

            # Extract each piece of data using Beautiful Soup
            company_data["website"] = self.parse_text(
                "div[data-test-id='about-us__website'] a", soup
            )

            company_data["industry"] = self.parse_text(
                "div[data-test-id='about-us__industry'] dd", soup
            )
            company_data["company_size"] = self.parse_text(
                "div[data-test-id='about-us__size'] dd", soup
            )
            company_data["headquarters"] = self.parse_text(
                "div[data-test-id='about-us__headquarters'] dd", soup
            )
            company_data["type"] = self.parse_text(
                "div[data-test-id='about-us__organizationType'] dd", soup
            )
            company_data["founded"] = self.parse_text(
                "div[data-test-id='about-us__foundedOn'] dd", soup
            )
            company_data["specialties"] = self.parse_text(
                "div[data-test-id='about-us__specialties'] dd", soup
            )
            company_data["about_us"] = self.parse_text(
                "p[data-test-id='about-us__description']", soup
            )

        except Exception as e:
            error_message = f"Error occurred while getting Company data: {e}"
            print(error_message)
            return {"error": error_message}

        finally:
            self.driver.quit()
            return company_data

    @staticmethod
    def parse_text(css_selector, soup):
        try:
            text = (
                soup.select_one(css_selector).get_text(strip=True)
                if soup.select_one(css_selector)
                else "N/A"
            )
            return text
        except:
            return "N/A"

    @staticmethod
    def extract_name(full_string):
        # Check if there's a comma in the string
        if "," in full_string:
            # Split the string on commas and keep the first part, which contains the full name
            return full_string.split(",")[0]
        else:
            no_comment_string = full_string.split("<!--")[0]

            clean_string = no_comment_string.replace("\n", "").strip()

            clean_string = clean_string.strip("'")

            return clean_string

    def login_and_save_cookies(
        self, email, password, cookies_file="linkedin_cookies.pkl"
    ):
        self.create_chrome_driver()
        self.driver.get("https://www.linkedin.com/login")

        # Login process
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        email_input.send_keys(email)
        password_input.send_keys(password)
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "global-nav"))
        )

        # Save cookies to a file
        with open(cookies_file, "wb") as cookies:
            pickle.dump(self.driver.get_cookies(), cookies)

        self.driver.quit()
