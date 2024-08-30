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

            # Select the "Stories" checkbox based on the input's value attribute
            self.wait_until_element_is_visible('css:input[value="00000188-f942-d221-a78c-f9570e360000"]', timeout=10)
            stories_checkbox = self.get_webelement('css:input[value="00000188-f942-d221-a78c-f9570e360000"]')
            self.scroll_element_into_view(stories_checkbox)
            self.close_popup_if_present()  # Ensure no popup is blocking
            self.click_element(stories_checkbox)  # Click the checkbox directly
            print("Stories category checkbox selected")

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
    def select_sort_by_newest(self):
        try:
            # Scroll the "Sort by" dropdown into view and click it
            self.wait_until_element_is_visible('css:select[name="s"]', timeout=10)
            sort_by_dropdown = self.get_webelement('css:select[name="s"]')
            self.scroll_element_into_view(sort_by_dropdown)
            self.close_popup_if_present()  # Ensure no popup is blocking
            self.select_from_list_by_value(sort_by_dropdown, "3")  # Select "Newest" option
            print("Selected 'Newest' in Sort by dropdown")
            # Wait for the page to reload and URL to change
            time.sleep(5)
            # Check if the URL contains "s=3" to confirm the sorting change
            current_url = self.driver.current_url
            if "s=3" in current_url:
                print("Successfully sorted by 'Newest'")
                # Close any popups that might have appeared after the reload
                self.close_popup_if_present()
                # Take a screenshot after selecting "Newest"
                self.capture_page_screenshot("output/process/step_4_sort_by_newest.png")
            else:
                # If the URL did not change, refresh the page and try again
                print("Failed to change sorting to 'Newest', refreshing the page...")
                self.driver.refresh()
                time.sleep(5)
                self.select_sort_by_newest()  # Retry selecting "Newest"
        except Exception as e:
            print(f"Failed to select 'Newest' in Sort by dropdown: {e}")


    @keyword
    def extract_news_data_and_store(self):
        try:
            # Initialize Excel file
            excel = Files()
            output_path = "output/process/data/news_data.xlsx"
            excel.create_workbook(output_path)
            excel.append_rows_to_worksheet([
                ["Title", "Date", "Description", "Image Filename", "Search Phrases Count", "Contains Money"]
            ], header=True)

            # Locate all news articles on the page
            articles = self.get_webelements('css:.PageList-items-item')

            data = []
            for i, article in enumerate(articles):
                # Scroll to the article to ensure it's loaded
                self.scroll_element_into_view(article)
                time.sleep(1)  # Allow time for the element to load properly

                # Extract title
                try:
                    title_element = article.find_element("css selector", ".PagePromo-title span")
                    title = title_element.text if title_element else "N/A"
                except Exception as e:
                    title = "N/A"
                    print(f"Failed to extract title: {e}")

                # Extract description
                try:
                    description_element = article.find_element("css selector", ".PagePromo-description span")
                    description = description_element.text if description_element else "N/A"
                except Exception as e:
                    description = "N/A"
                    print(f"Failed to extract description: {e}")

                # Extract date
                try:
                    date_element = article.find_element("css selector", ".PagePromo-date span")
                    date = date_element.text if date_element else "N/A"
                except Exception as e:
                    date = "N/A"
                    print(f"Failed to extract date: {e}")

                # Extract and save the image
                try:
                    img_element = article.find_element("css selector", ".PagePromo-media img")
                    img_filename = self.save_image_from_element(img_element, title) if img_element else "N/A"
                except Exception as e:
                    img_filename = "N/A"
                    print(f"Failed to extract image: {e}")

                # Count occurrences of search phrases
                search_phrases_count = self.count_search_phrases(title, description, ["COVID"])

                # Check for monetary values in title and description
                contains_money = self.check_money_in_text(title + " " + description)

                # Append data for this article
                data.append([title, date, description, img_filename, search_phrases_count, contains_money])

                # Scroll a bit further down for the next article
                if i < len(articles) - 1:
                    next_article = articles[i + 1]
                    self.scroll_element_into_view(next_article)
                    time.sleep(1)

            # Write data to the Excel sheet
            excel.append_rows_to_worksheet(data, header=False)
            excel.save_workbook(output_path)
            excel.close_workbook()
            print(f"Data extracted and stored in {output_path}")

        except Exception as e:
            print(f"Failed to extract news data and store in Excel: {e}")


    @keyword
    def save_image_from_element(self, img_element, title):
        filename = f"{title[:50]}.png"  # Limit the filename to 50 characters
        filepath = os.path.join("output/process/data/images", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img_element.screenshot(filepath)
        return filename

    @keyword
    def count_search_phrases(self, title, description, phrases):
        count = 0
        for phrase in phrases:
            count += title.lower().count(phrase.lower())
            count += description.lower().count(phrase.lower())
        return count

    @keyword
    def check_money_in_text(self, text):
        money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?|(?:\d+\s(?:dollars|USD))'
        return bool(re.search(money_pattern, text, re.IGNORECASE))

    @keyword
    def print_webdriver_log(self, logtype):
        logs = self.driver.get_log(logtype)
        for entry in logs:
            print(entry)

    @keyword
    def quit_driver(self):
        if self.driver:
            self.driver.quit()
