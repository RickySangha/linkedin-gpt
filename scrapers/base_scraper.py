from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import random
import os
import shutil
import pickle

from scrapers.scraper_config import ScraperConfig


class BaseScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.user_agents = (
            self.load_user_agents()
        )  # Load a list of user agents from a file or list

    def create_chrome_driver(self):
        options = Options()
        self.setup_directory(self.config.profile_directory)
        options.add_argument(
            f"user-agent={random.choice(self.user_agents)}"
        )  # Set a random user agent
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument(
            "--disable-gpu"
        )  # Disable GPU (optional, for headless mode)
        options.add_argument(
            "--no-sandbox"
        )  # Bypass OS security model (optional, for headless mode)
        options.add_argument(
            "--disable-dev-shm-usage"
        )  # Overcome limited resource problems (optional, for headless mode)
        options.add_argument("referrer=https://www.google.com")  # Set a referrer header

        # Initialize the Chrome WebDriver with the service
        driver = webdriver.Chrome(options=options)

        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        self.driver = driver

        return driver

    def load_cookies_and_create_chrome_driver(
        self, cookies_file="linkedin_cookies.pkl"
    ):
        self.create_chrome_driver()

        # Load cookies if they exist
        if os.path.exists(cookies_file):
            with open(cookies_file, "rb") as cookies:
                cookies_list = pickle.load(cookies)
                for cookie in cookies_list:
                    self.driver.add_cookie(cookie)

        return self.driver

    def setup_directory(self, profile_directory):
        if os.path.exists(profile_directory):
            shutil.rmtree(profile_directory)
        # if not os.path.exists(directory_path):
        os.makedirs(profile_directory, exist_ok=True)

    @staticmethod
    def load_user_agents():
        user_agents = []
        with open("user_agents.txt", "r") as file:
            for line in file:
                if line.strip():
                    user_agents.append(line.strip())
        return user_agents
