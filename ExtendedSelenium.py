# ExtendedSelenium.py
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from SeleniumLibrary.base import keyword
from RPA.Excel.Files import Files
import re
import os
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ExtendedSelenium(Selenium):
    """
    Extended Selenium class for custom web automation tasks.

    This class extends the Selenium library from the RPA Framework with
    additional methods to handle work items and custom interactions.
    """

    def __init__(self, work_item, *args, **kwargs):
        """
        Initialize the ExtendedSelenium instance.

        Args:
            work_item (WorkItems): The work item object for handling RPA tasks.
        """
        super().__init__(*args, **kwargs)
        self.service = ChromeService(ChromeDriverManager().install())
        self.work_item = work_item

    @keyword
    def save_screenshot_to_work_item(self, filename):
        """
        Capture a screenshot and save it to the work item.

        Args:
            filename (str): The path where the screenshot will be saved.

        Raises:
            Exception: If there is an error capturing the screenshot.
        """
        try:
            self.screenshot(filename=filename)
            self.work_item.add_work_item_file(path=filename)
            self.work_item.save_work_item()
            logging.info(f"Screenshot saved and added to work item: {filename}")
        except Exception as e:
            logging.error(f"Failed to save screenshot to work item: {e}")

    @keyword
    def accept_cookies(self):
        """
        Attempt to click the 'I Accept' button on cookie consent popups.

        This method looks for a specific button related to cookie consent and clicks it.

        Raises:
            Exception: If the cookie button cannot be found or clicked.
        """
        try:
            self.wait_until_element_is_visible(
                'xpath://button[contains(text(), "I Accept")]', timeout=10)
            self.click_element_with_retry('xpath://button[contains(text(), "I Accept")]')
            logging.info("Accepted cookies.")
        except Exception as e:
            logging.warning(f"Failed to accept cookies: {e}")


    @keyword
    def open_site(self, url):
        """
        Open a website using a headless Chrome browser and save a screenshot.

        Args:
            url (str): The URL of the website to be opened.
        """
        logging.info(f"Opening URL: {url}")
        try:
            self.open_chrome_browser(url=url, headless=True)
            self.go_to(url=url)
            # Wait until the page is loaded by checking for a common element or condition
            self.wait_until_page_contains_element('css:body', timeout=10)
            self.save_screenshot_to_work_item(
                filename="output/step_0-1_opened_site.png")
        except Exception as e:
            logging.error(f"Failed to open site {url}: {e}")


    def click_element_with_retry(self, selector, retries=3):
        """
        Click an element with a retry mechanism.

        Args:
            selector (str): The selector for the element to click.
            retries (int): Number of retry attempts if the click fails.
        """
        for attempt in range(retries):
            try:
                element = self.find_element(selector)
                self.wait_until_element_is_interactable(element, timeout=10)
                self.click_element(selector)
                logging.info(f"Clicked element: {selector}")
                return
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed to click element {selector}: {e}")
        logging.error(f"Failed to click element {selector} after {retries} attempts")




    def close_all_popups(self):
        """
        Close all detected popups using various strategies.
        """
        try:
            if self.is_element_visible('id:Close'):
                self.click_element_with_retry('id:Close')
            if self.is_element_visible('xpath://a[@onclick="closeLightbox()"]'):
                self.click_element_with_retry('xpath://a[@onclick="closeLightbox()"]')
            if self.is_element_visible('css:div.fancybox-overlay-fixed'):
                self.click_element_with_retry('css:a.fancybox-close')
            if self.is_element_visible('css:button[aria-label="Close"]'):
                self.click_element_with_retry('css:button[aria-label="Close"]')
            logging.info("All popups closed.")
        except Exception as e:
            logging.error(f"Failed to close all popups: {e}")


    @keyword
    def click_search_button(self):
        """
        Click the search button on the webpage.

        This method waits until the search button is clickable, attempts to click it,
        and then takes a screenshot before and after the click.

        Raises:
            Exception: If the search button is not found or cannot be clicked.
        """
        try:
            wait = WebDriverWait(self.driver, 10)
            search_button = wait.until(
                EC.element_to_be_clickable(('css selector', '.SearchOverlay-search-button'))
            )
            self.close_all_popups()
            self.save_screenshot_to_work_item(filename="output/step_1-1_search-pre_click_search_button.png")
            search_button.click()
            logging.info("Search button clicked")
        except Exception as e:
            logging.error("Search button not found or couldn't be clicked: %s", e)
        finally:
            self.close_all_popups()
            self.save_screenshot_to_work_item(filename="output/step_1-2_search-click_button.png")

    @keyword
    def type_and_submit_search_query(self, query):
        """
        Type a search query into the search input and submit it.

        Args:
            query (str): The search query to be entered and submitted.

        Raises:
            Exception: If the search query cannot be typed or submitted.
        """
        try:
            self.close_all_popups()
            self.wait_until_element_is_visible(
                'css:input.SearchOverlay-search-input', timeout=10)
            self.input_text('css:input.SearchOverlay-search-input', query)
            logging.info(f"Typed '{query}' into the search input.")
            self.save_screenshot_to_work_item(
                filename="output/step_2-1_search-typed_query.png")
            self.press_keys('css:input.SearchOverlay-search-input', 'ENTER')
            logging.info(f"Submitted '{query}' to the search input.")
            self.wait_until_element_is_visible(
                'css:.SearchResultsModule', timeout=10)
            self.save_screenshot_to_work_item(
                filename="output/step_2-2_search-after_submit.png")
        except Exception as e:
            logging.error(
                f"Failed to type and submit search query '{query}': {e}")

    @keyword
    def click_and_select_category(self, category_name):
        """
        Click the category filter dropdown and select a specific category.

        Args:
            category_name (str): The name of the category to be selected.

        Raises:
            Exception: If the category dropdown cannot be clicked or the category cannot be selected.
        """
        try:
            self.wait_until_element_is_visible(
                'css:.SearchFilter-heading', timeout=10)
            self.scroll_element_into_view('css:.SearchFilter-heading')
            if not self.is_element_visible('css:bsp-toggler[data-toggle-in="search-filter"]'):
                logging.info("Dropdown is already open, skipping it.")
            else:
                self.close_all_popups()
                try:
                    self.click_element_with_retry('css:.SearchFilter-heading')
                    logging.info("Category dropdown clicked")
                    self.save_screenshot_to_work_item(
                        filename="output/step_3-1_category-clicked.png")
                except Exception as e:
                    logging.error(f"Failed to click category: {e}")
                    return
            # Step 3-2: Click "See All" if it hasn't been clicked already
            if not self.is_element_visible('css:bsp-toggler[data-toggle-in="see-all"]'):
                try:
                    self.wait_until_element_is_visible(
                        'css:.SearchFilter-seeAll-button', timeout=10)
                    see_all_button = self.get_webelement(
                        'css:.SearchFilter-seeAll-button')
                    self.scroll_element_into_view(see_all_button)
                    self.wait_until_element_is_interactable(see_all_button, timeout=10)
                    self.close_all_popups()
                    self.click_element_with_retry(see_all_button)
                    logging.info('"See All" button clicked')
                    self.save_screenshot_to_work_item(
                        filename="output/step_3-2_see_all_clicked.png")
                except Exception as e:
                    logging.error(f"Failed to click 'See All': {e}")
                    return
            else:
                logging.info('"See All" already clicked, skipping.')

            # Step 3-3: Select the desired category
            for attempt in range(3):  # Retry up to 3 times to handle potential staleness
                try:
                    category_value = self.get_category_value(category_name)
                    category_checkbox = self.get_webelement(
                        f'css:input[value="{category_value}"]')
                    self.scroll_element_into_view(category_checkbox)
                    self.wait_until_element_is_visible(category_checkbox, timeout=10)
                    self.close_all_popups()
                    self.click_element_with_retry(category_checkbox)
                    logging.info(f"{category_name} category checkbox selected")

                    # Re-fetch the heading element after page updates
                    heading_element = self.find_element('css:.SearchFilter-heading')
                    self.wait_until_element_is_interactable(heading_element, timeout=10)
                    self.close_all_popups()
                    self.scroll_element_into_view(heading_element)
                    logging.info("Scrolled to dropdown")
                    self.save_screenshot_to_work_item(
                        filename=f"output/step_3-3_{category_name}_selected.png")
                    break  # Exit the loop if successful
                except Exception as e:
                    logging.error(f"Failed to select category on attempt {attempt + 1}: {e}")
                    if attempt == 2:  # If the last attempt fails, re-raise the exception
                        raise
        except Exception as e:
            logging.error(f"Failed to interact with category filter: {e}")



    @keyword
    def select_sort_by_newest(self):
        """
        Select 'Newest' in the sort by dropdown menu.

        This method ensures that the articles are sorted by the newest first.

        Raises:
            Exception: If the dropdown cannot be found or the sorting fails.
        """
        try:
            self.wait_until_element_is_visible(
                'css:select[name="s"]', timeout=10)
            sort_by_dropdown = self.get_webelement('css:select[name="s"]')
            self.scroll_element_into_view(sort_by_dropdown)
            self.wait_until_element_is_interactable(sort_by_dropdown, timeout=10)
            self.close_all_popups()
            self.select_from_list_by_value(sort_by_dropdown, "3")
            logging.info("Selected 'Newest' in Sort by dropdown")

            # Wait for the page to refresh and confirm it has applied the sort
            self.wait_until_element_is_visible('css:.SearchResultsModule', timeout=10)
            current_url = self.driver.current_url
            if "s=3" in current_url:
                logging.info("Successfully sorted by 'Newest'")
                self.close_all_popups()
                self.save_screenshot_to_work_item(
                    filename="output/step_4_sort_by_newest.png")
            else:
                logging.warning(
                    "Failed to change sorting to 'Newest', refreshing the page...")
                self.driver.refresh()
                self.select_sort_by_newest()
        except Exception as e:
            logging.error(
                f"Failed to select 'Newest' in Sort by dropdown: {e}")

    @keyword
    def extract_news_data_and_store(self):
        """
        Extract news data from the page and store it in an Excel file.

        This method collects the title, date, description, image filename, and other details
        from each news article on the page, and writes them to an Excel file.

        Raises:
            Exception: If there is an error during data extraction or file creation.
        """
        try:
            excel = Files()
            output_path = "output/news_data.xlsx"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
                # Explicit wait for the element to be interactable
                self.wait_until_element_is_interactable(article, timeout=10)

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
                    img_filename = "N/A"  # there is no image

                # Count occurrences of search phrases
                search_phrases_count = self.count_search_phrases(
                    title, description, ["COVID"])

                # Check for monetary values in title and description
                contains_money = self.check_money_in_text(
                    title + " " + description)

                # Append data for this article
                data.append([title, date, description, img_filename,
                            search_phrases_count, contains_money])

                # Scroll to the next article and wait for it to be interactable
                if i < len(articles) - 1:
                    next_article = articles[i + 1]
                    self.scroll_element_into_view(next_article)
                    self.wait_until_element_is_interactable(next_article, timeout=10)

            # Write data to the Excel sheet
            excel.append_rows_to_worksheet(data, header=False)
            excel.save_workbook(output_path)
            excel.close_workbook()
            logging.info(f"Data extracted and stored in {output_path}")

            # Add the Excel file to the work item
            self.work_item.add_work_item_file(path=output_path)
            self.work_item.save_work_item()
            logging.info(f"Excel file added to work item: {output_path}")

        except Exception as e:
            logging.error(f"Failed to extract news data and store in Excel: {e}")


    def save_image_from_element(self, img_element, title):
        """
        Save the image from a web element to a file.

        Args:
            img_element (WebElement): The image web element to capture.
            title (str): The title used to generate the filename.

        Returns:
            str: The filename where the image was saved.

        Raises:
            Exception: If there is an error while saving the image.
        """
        try:
            filename = f"image-{title[:50]}.png"
            filepath = os.path.join("output", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            img_element.screenshot(filepath)
            self.work_item.add_work_item_file(path=filepath)
            self.work_item.save_work_item()
            logging.info(f"Image saved and added to work item: {filepath}")
            return filename
        except Exception as e:
            logging.error(f"Failed to save image: {e}")
            return "N/A"

    def count_search_phrases(self, title, description, phrases):
        """
        Count occurrences of search phrases in the title and description.

        Args:
            title (str): The title of the article.
            description (str): The description of the article.
            phrases (list): A list of search phrases to count.

        Returns:
            int: The total count of search phrases in the title and description.
        """
        count = 0
        for phrase in phrases:
            count += title.lower().count(phrase.lower())
            count += description.lower().count(phrase.lower())
        return count

    def check_money_in_text(self, text):
        """
        Check if the text contains monetary values.

        Args:
            text (str): The text to check.

        Returns:
            bool: True if the text contains monetary values, False otherwise.
        """
        money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?|(?:\d+\s(?:dollars|USD))'
        return bool(re.search(money_pattern, text, re.IGNORECASE))

    def print_webdriver_log(self, logtype):
        """
        Print the WebDriver log of a specific type.

        Args:
            logtype (str): The type of log to retrieve (e.g., 'browser', 'driver').

        Raises:
            Exception: If there is an error retrieving the logs.
        """
        logs = self.driver.get_log(logtype)
        for entry in logs:
            logging.info(entry)

    def get_category_value(self, category_name):
        """
        Retrieve the value associated with a specific category name.

        Args:
            category_name (str): The name of the category.

        Returns:
            str: The value associated with the category name.
        """
        category_mapping = {
            "Live Blogs": "00000190-0dc5-d7b0-a1fa-dde7ec030000",
            "Sections": "00000189-9323-dce2-ad8f-bbe74c770000",
            "Stories": "00000188-f942-d221-a78c-f9570e360000",
            "Subsections": "00000189-9323-db0a-a7f9-9b7fb64a0000",
            "Videos": "00000188-d597-dc35-ab8d-d7bf1ce10000",
        }
        return category_mapping.get(category_name, "00000188-f942-d221-a78c-f9570e360000")


    def wait_until_element_is_interactable(self, element, timeout=10):
        """
        Wait until an element is interactable (clickable or input-ready).

        Args:
            element (WebElement): The web element to wait for.
            timeout (int): Maximum time to wait in seconds.

        Raises:
            TimeoutException: If the element is not interactable within the timeout period.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element)
            )
        except Exception as e:
            logging.error(f"Element not interactable after {timeout} seconds: {e}")
            raise

    @keyword
    def quit_driver(self):
        """
        Quit the WebDriver and close the browser.

        Raises:
            Exception: If there is an error while quitting the driver.
        """
        if self.driver:
            self.driver.quit()
