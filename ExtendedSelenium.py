from RPA.Browser.Selenium import Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from SeleniumLibrary.base import keyword
import time

class ExtendedSelenium(Selenium):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ChromeService(ChromeDriverManager().install())
        self.options = self.create_options()

    def create_options(self):
        options = Options()
        # Enable headless mode for faster execution
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        # options.add_argument("--headless")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-infobars")
        # options.add_argument("--disable-popup-blocking")
        # options.add_argument("--disable-notifications")
        # options.add_argument("--disable-background-timer-throttling")
        # options.add_argument("--disable-backgrounding-occluded-windows")
        # options.add_argument("--disable-renderer-backgrounding")
        # options.add_argument("--ignore-certificate-errors")
        # options.add_argument("--mute-audio")  # Mute audio
        # options.add_argument("--start-maximized")  # Start maximized
        # Disable image loading to improve speed
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        return options

    @keyword
    def open_site(self, url):
        # Use create_webdriver with the driver_name parameter
        self.create_webdriver(driver_name="Chrome", service=self.service, options=self.options)
        self.driver.get(url)
        time.sleep(2)  # Short wait for the page to load

    @keyword
    def close_popup_if_present(self):
        try:
            self.wait_until_element_is_visible('xpath://a[@onclick="closeLightbox()"]', timeout=10)
            self.click_element('xpath://a[@onclick="closeLightbox()"]')
            time.sleep(1)  # Allow time for the popup to close
        except Exception as e:
            print("Popup not found or already closed.")

    @keyword
    def click_search_button(self):
        try:
            self.wait_until_element_is_visible('css:.SearchOverlay-search-button', timeout=10)
            self.click_element('css:.SearchOverlay-search-button')
            print("Search button clicked")
            time.sleep(1)  # Allow time for the search overlay to open
        except Exception as e:
            print("Search button not found or couldn't be clicked.")

    @keyword
    def print_webdriver_log(self, logtype):
        logs = self.driver.get_log(logtype)
        for entry in logs:
            print(entry)

    @keyword
    def quit_driver(self):
        if self.driver:
            self.driver.quit()
