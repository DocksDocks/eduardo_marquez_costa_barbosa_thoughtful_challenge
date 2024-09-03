# tasks.py
import logging
import os
from dotenv import load_dotenv
from RPA.Robocorp.WorkItems import WorkItems, State
from ExtendedSelenium import ExtendedSelenium

# Load environment variables from .env file
load_dotenv()

# def the_process():
#     work_item = WorkItems()
#     work_item.get_input_work_item()
#     search_phrase = work_item.get_work_item_variable("search_phrase", "COVID")
#     news_category = work_item.get_work_item_variable("news_category", "Stories")
#     browser = ExtendedSelenium()
#     try:
#         url = "https://apnews.com/"
#         browser.open_site(url)
#         browser.close_popup_if_present()
#         browser.click_search_button()
#         browser.type_and_submit_search_query(search_phrase)
#         browser.click_and_select_category(news_category)
#         browser.select_sort_by_newest()
#         browser.extract_news_data_and_store()
#         work_item.release_input_work_item(State.DONE)
#     except Exception as e:
#         work_item.release_input_work_item(State.FAILED)
#     finally:
#         browser.quit_driver()

def the_process():
    browser = ExtendedSelenium()
    work_item = WorkItems()
    try:
        # Reserve the input work item and set it as active
        if not work_item.get_input_work_item():
            logging.error("No input work item found. Exiting process.")
            return

        # Ensure there's an active work item
        if not work_item.current:
            logging.error("No active work item. Exiting process.")
            return

        # Perform the browser operations
        browser.open_chrome_browser(url="https://apnews.com", headless=True)
        browser.screenshot(filename="output/screenshot_example.png")

        # Add the screenshot file to the work item
        work_item.add_work_item_file(path="output/screenshot_example.png")
        work_item.save_work_item()

        # Mark the work item as completed
        work_item.release_input_work_item(State.DONE)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if work_item.current:
            work_item.release_input_work_item(State.FAILED)
    finally:
        browser.close_all_browsers()

if __name__ == "__main__":
    the_process()