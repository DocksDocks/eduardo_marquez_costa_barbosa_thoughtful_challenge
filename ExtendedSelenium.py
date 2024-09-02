# ExtendedSelenium.py
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from SeleniumLibrary.base import keyword
from RPA.Excel.Files import Files
import re
import os
import time
import logging


class ExtendedSelenium(Selenium):

    def __init__(self, headless=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ChromeService(ChromeDriverManager().install())
        self.options = self.create_options(headless)

    def create_options(self, headless):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
        options.add_experimental_option("prefs", { "profile.default_content_setting_values.notifications": 2})
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        return options

    @keyword
    def open_site(self, url, wait_time=10):
        logging.info(f"Opening url= {url}")
        time.sleep(wait_time)  # Wait to ensure any initial popups appear
        self.create_webdriver(driver_name="Chrome",
                              service=self.service, options=self.options)
        self.driver.get(url)
        time.sleep(2)  # Short wait for the page to load

    @keyword
    def close_popup_if_present(self):
        try:
            time.sleep(1)  # Allow time for the popup to show
            logging.info("Attempting to close possible popups.")
            # Attempt to close any generic "Close" button first
            if self.is_element_visible('id:Close'):
                self.click_element('id:Close')
                logging.info("Popup closed using generic 'Close' button")

            # Close the lightbox popup if present
            if self.is_element_visible('xpath://a[@onclick="closeLightbox()"]'):
                self.click_element('xpath://a[@onclick="closeLightbox()"]')
                logging.info("Initial popup closed")
            # Close any other fancybox overlays if present
            if self.is_element_visible('css:div.fancybox-overlay-fixed'):
                if self.is_element_visible('css:a.fancybox-close'):
                    self.click_element('css:a.fancybox-close')
                    logging.info("Fancybox overlay closed")
            # Close any other buttons with aria-label="Close"
            if self.is_element_visible('css:button[aria-label="Close"]'):
                self.click_element('css:button[aria-label="Close"]')
                logging.info("Additional popup closed")

        except Exception as e:
            logging.error(f"Failed to close popup: {e}")


    @keyword
    def click_search_button(self):
        try:
            time.sleep(5)  # Wait for the page to load
            self.close_popup_if_present()
            self.capture_page_screenshot("output/screenshots/step_1-1_search-pre_click_search_button.png")
            self.wait_until_element_is_visible(
                'css:.SearchOverlay-search-button', timeout=10)
            self.click_element('css:.SearchOverlay-search-button')
            logging.info("Search button clicked")
            time.sleep(1)
        except Exception as e:
            logging.error("Search button not found or couldn't be clicked.")
        finally:
            self.close_popup_if_present()
            self.capture_page_screenshot(
                "output/process/screenshots/step_1-2_search-click_button.png")

    @keyword
    def type_and_submit_search_query(self, query):
        try:
            self.close_popup_if_present()
            self.wait_until_element_is_visible(
                'css:input.SearchOverlay-search-input', timeout=10)
            self.input_text('css:input.SearchOverlay-search-input', query)
            logging.info(f"Typed '{query}' into the search input.")
            self.capture_page_screenshot(
                "output/process/screenshots/step_2-1_search-typed_query.png")
            self.press_keys('css:input.SearchOverlay-search-input', 'ENTER')
            logging.info(f"Submitted '{query}' to the search input.")
            self.wait_until_element_is_visible(
                'css:.SearchResultsModule', timeout=10)
            self.capture_page_screenshot(
                "output/process/screenshots/step_2-2_search-after_submit.png")
        except Exception as e:
            logging.error(
                f"Failed to type and submit search query '{query}': {e}")

    @keyword
    def click_and_select_category(self, category_name):
        try:
            # Step 3-1: Interact with the category filter dropdown
            self.wait_until_element_is_visible(
                'css:.SearchFilter-heading', timeout=10)
            self.scroll_element_into_view('css:.SearchFilter-heading')
            # Dropdown is not open
            if not self.is_element_visible('css:bsp-toggler[data-toggle-in="search-filter"]'):
                logging.info("Dropdown is already open, skipping it.")
            else:
                self.close_popup_if_present()
                try:
                    self.click_element('css:.SearchFilter-heading')
                    logging.info("Category dropdown clicked")
                    self.capture_page_screenshot(
                        "output/process/screenshots/step_3-1_category-clicked.png")
                except Exception as e:
                    logging.error(f"Failed to click category: {e}")
                    return
            # Step 3-2: Click "See All" if it hasn't been clicked already
            # See All is not clicked
            if not self.is_element_visible('css:bsp-toggler[data-toggle-in="see-all"]'):
                try:
                    self.wait_until_element_is_visible(
                        'css:.SearchFilter-seeAll-button', timeout=10)
                    see_all_button = self.get_webelement(
                        'css:.SearchFilter-seeAll-button')
                    self.scroll_element_into_view(see_all_button)
                    self.close_popup_if_present()
                    self.click_element(see_all_button)
                    logging.info('"See All" button clicked')
                    self.capture_page_screenshot(
                        "output/process/screenshots/step_3-2_see_all_clicked.png")
                except Exception as e:
                    logging.error(f"Failed to click 'See All': {e}")
                    return
            else:
                logging.info('"See All" already clicked, skipping.')
            # Step 3-3: Select the desired category
            try:
                category_value = self.get_category_value(category_name)
                category_checkbox = self.get_webelement(
                    f'css:input[value="{category_value}"]')
                self.scroll_element_into_view(category_checkbox)
                self.close_popup_if_present()
                self.click_element(category_checkbox)
                logging.info(f"{category_name} category checkbox selected")
                time.sleep(3)
                self.close_popup_if_present()
                self.scroll_element_into_view('css:.SearchFilter-heading')
                logging.info("Scrolled to dropdown")
                self.capture_page_screenshot(
                    f"output/process/screenshots/step_3-3_{category_name}_selected.png")
            except Exception as e:
                logging.error(f"Failed to select category: {e}")
        except Exception as e:
            logging.error(f"Failed to interact with category filter: {e}")

    @keyword
    def select_sort_by_newest(self):
        try:
            self.wait_until_element_is_visible(
                'css:select[name="s"]', timeout=10)
            sort_by_dropdown = self.get_webelement('css:select[name="s"]')
            self.scroll_element_into_view(sort_by_dropdown)
            self.close_popup_if_present()
            self.select_from_list_by_value(sort_by_dropdown, "3")
            logging.info("Selected 'Newest' in Sort by dropdown")
            time.sleep(5)
            current_url = self.driver.current_url
            if "s=3" in current_url:
                logging.info("Successfully sorted by 'Newest'")
                self.close_popup_if_present()
                self.capture_page_screenshot(
                    "output/process/screenshots/step_4_sort_by_newest.png")
            else:
                logging.warning(
                    "Failed to change sorting to 'Newest', refreshing the page...")
                self.driver.refresh()
                time.sleep(5)
                self.close_popup_if_present()
                self.select_sort_by_newest()
        except Exception as e:
            logging.error(
                f"Failed to select 'Newest' in Sort by dropdown: {e}")

    @keyword
    def extract_news_data_and_store(self):
        try:
            excel = Files()
            output_path = "output/process/data/news_data.xlsx"
            excel.create_workbook(output_path)
            excel.append_rows_to_worksheet([
                ["Title", "Date", "Description", "Image Filename",
                    "Search Phrases Count", "Contains Money"]
            ], header=True)

            articles_container = self.get_webelement(
                'css:.SearchResultsModule-results .PageList-items')
            articles = articles_container.find_elements(
                "css selector", ".PageList-items-item")

            data = []
            for i, article in enumerate(articles):
                self.scroll_element_into_view(article)
                time.sleep(1)

                title, description, date, img_filename = "N/A", "N/A", "N/A", "N/A"
                try:
                    title_element = article.find_element(
                        "css selector", ".PagePromo-title span")
                    title = title_element.text if title_element else "N/A"
                except Exception as e:
                    logging.warning("Failed to extract title.")

                try:
                    description_element = article.find_element(
                        "css selector", ".PagePromo-description span")
                    description = description_element.text if description_element else "N/A"
                except Exception as e:
                    logging.warning("Failed to extract description.")

                try:
                    date_element = article.find_element(
                        "css selector", ".PagePromo-date span")
                    date = date_element.text if date_element else "N/A"
                except Exception as e:
                    logging.warning("Failed to extract date.")

                try:
                    img_element = article.find_element(
                        "css selector", ".PagePromo-media img")
                    img_filename = self.save_image_from_element(
                        img_element, title) if img_element else "N/A"
                except Exception as e:

                    img_filename = "N/A"
                    logging.warning(
                        "Failed to extract image: there is no image.")

                # Count occurrences of search phrases
                search_phrases_count = self.count_search_phrases(
                    title, description, ["COVID"])

                # Check for monetary values in title and description
                contains_money = self.check_money_in_text(
                    title + " " + description)

                # Append data for this article
                data.append([title, date, description, img_filename,
                            search_phrases_count, contains_money])

                # Scroll a bit further down for the next article
                if i < len(articles) - 1:
                    next_article = articles[i + 1]
                    self.scroll_element_into_view(next_article)
                    time.sleep(1)

            # Write data to the Excel sheet
            excel.append_rows_to_worksheet(data, header=False)
            excel.save_workbook(output_path)
            excel.close_workbook()
            logging.info(f"Data extracted and stored in {output_path}")

        except Exception as e:
            logging.error(
                f"Failed to extract news data and store in Excel: {e}")

    def save_image_from_element(self, img_element, title):
        try:
            # Limit the filename to 50 characters
            filename = f"{title[:50]}.png"
            filepath = os.path.join("output/process/data/images", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            img_element.screenshot(filepath)
            return filename
        except Exception as e:
            logging.error(f"Failed to save image: {e}")
            return "N/A"

    def count_search_phrases(self, title, description, phrases):
        count = 0
        for phrase in phrases:
            count += title.lower().count(phrase.lower())
            count += description.lower().count(phrase.lower())
        return count

    def check_money_in_text(self, text):
        money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?|(?:\d+\s(?:dollars|USD))'
        return bool(re.search(money_pattern, text, re.IGNORECASE))

    def print_webdriver_log(self, logtype):
        logs = self.driver.get_log(logtype)
        for entry in logs:
            logging.info(entry)

    def get_category_value(self, category_name):
        category_mapping = {
            "Live Blogs": "00000190-0dc5-d7b0-a1fa-dde7ec030000",
            "Sections": "00000189-9323-dce2-ad8f-bbe74c770000",
            "Stories": "00000188-f942-d221-a78c-f9570e360000",
            "Subsections": "00000189-9323-db0a-a7f9-9b7fb64a0000",
            "Videos": "00000188-d597-dc35-ab8d-d7bf1ce10000",
        }
        # Default to Stories
        return category_mapping.get(category_name, "00000188-f942-d221-a78c-f9570e360000")

    @keyword
    def quit_driver(self):
        if self.driver:
            self.driver.quit()
