# ExtendedSelenium.py
from RPA.Browser.Selenium import Selenium
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
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        return options

    @keyword
    def open_site(self, url):
        time.sleep(10)  # Wait 10 seconds before starting to ensure the popup appears
        self.create_webdriver(driver_name="Chrome", service=self.service, options=self.options)
        self.driver.get(url)
        time.sleep(2)  # Short wait for the page to load

    @keyword
    def close_popup_if_present(self):
        try:
            # Check and close the first popup
            if self.is_element_visible('xpath://a[@onclick="closeLightbox()"]'):
                self.click_element('xpath://a[@onclick="closeLightbox()"]')
                time.sleep(1)  # Allow time for the popup to close

            # Check and close any additional popups that may appear later
            if self.is_element_visible('css:button[aria-label="Close"]'):
                self.click_element('css:button[aria-label="Close"]')
                time.sleep(1)  # Allow time for the popup to close

        except Exception as e:
            print("Popup not found or already closed.")

    @keyword
    def click_search_button(self):
        try:
            time.sleep(5) # wait page to load
            self.close_popup_if_present()  # Close any popup before clicking
            self.wait_until_element_is_visible('css:.SearchOverlay-search-button', timeout=10)
            self.click_element('css:.SearchOverlay-search-button')
            print("Search button clicked")
            time.sleep(1)  # Allow time for the search overlay to open
        except Exception as e:
            print("Search button not found or couldn't be clicked.")
        finally:
            self.close_popup_if_present()  # Ensure no popup is blocking the screenshot
            self.capture_page_screenshot("output/process/step_1_search-click_button.png")

    @keyword
    def type_and_submit_search_query(self, query):
        try:
            self.close_popup_if_present()  # Close any popup before typing
            self.wait_until_element_is_visible('css:input.SearchOverlay-search-input', timeout=10)
            self.input_text('css:input.SearchOverlay-search-input', query)
            print(f"Typed '{query}' into the search input.")

            self.close_popup_if_present()  # Ensure no popup is blocking the screenshot
            self.capture_page_screenshot("output/process/step_2-1_search-typed_query.png")
            self.press_keys('css:input.SearchOverlay-search-input', 'ENTER')

            self.wait_until_element_is_visible('css:.SearchResultsModule', timeout=10)
            self.close_popup_if_present()  # Ensure no popup is blocking the screenshot
            self.capture_page_screenshot("output/process/step_2-2_search-after_submit.png")

        except Exception as e:
            print(f"Failed to type and submit search query '{query}': {e}")

    @keyword
    def click_and_select_category(self):
        try:
            time.sleep(1)
            # Scroll the "Category" dropdown into view and click to expand it
            self.wait_until_element_is_visible('css:.SearchFilter-heading', timeout=10)
            self.scroll_element_into_view('css:.SearchFilter-heading')
            self.close_popup_if_present()  # Ensure no popup is blocking
            self.click_element('css:.SearchFilter-heading')
            print("Category dropdown clicked")
            time.sleep(1)  # Allow time for the dropdown to expand

            # Scroll the "Stories" checkbox into view and select it
            self.wait_until_element_is_visible('xpath://label/span[text()="Stories"]', timeout=10)
            stories_checkbox = self.get_webelement('xpath://label/span[text()="Stories"]/../input')
            self.scroll_element_into_view(stories_checkbox)
            self.close_popup_if_present()  # Ensure no popup is blocking
            self.execute_javascript("arguments[0].click();", stories_checkbox)
            print("Stories category selected")

            # Wait for the page to reload
            time.sleep(5)

            # Close any popups that might have appeared after the reload
            self.close_popup_if_present()

            # Scroll to the "Sort by" dropdown before taking the final screenshot
            self.wait_until_element_is_visible('css:.Select.SearchFilterAsDropdown', timeout=10)
            self.scroll_element_into_view('css:.Select.SearchFilterAsDropdown')
            print("Scrolled to 'Sort by' dropdown")

            # Take a screenshot after the category has been selected
            self.capture_page_screenshot("output/process/step_3-2_category-selected.png")

        except Exception as e:
            print(f"Failed to click and select category: {e}")




    @keyword
    def print_webdriver_log(self, logtype):
        logs = self.driver.get_log(logtype)
        for entry in logs:
            print(entry)

    @keyword
    def quit_driver(self):
        if self.driver:
            self.driver.quit()
