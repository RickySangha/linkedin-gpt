class ScraperConfig:
    def __init__(self, use_proxy:bool):
        self.use_proxy = use_proxy
        self.profile_directory = "chrome_profile"
        self.driver_path = '"/Users/ricky/Documents/SeleniumDrivers/chromedriver"'