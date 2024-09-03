from dotenv import load_dotenv
from RPA.Robocorp.WorkItems import WorkItems, State
from ExtendedSelenium import ExtendedSelenium
import logging
# Load environment variables from .env file
load_dotenv()

def the_process():
    work_item = WorkItems()
    browser = ExtendedSelenium(work_item=work_item)
    try:
        # Reserve the input work item and set it as active
        if not work_item.get_input_work_item():
            logging.error("No input work item found. Exiting process.")
            return
        # Ensure there's an active work item
        if not work_item.current:
            logging.error("No active work item. Exiting process.")
            return
        # Get variables from work item
        search_phrase = work_item.get_work_item_variable("search_phrase", "COVID")
        news_category = work_item.get_work_item_variable("news_category", "Stories")
        # Perform the browser operations
        browser.open_site(url="https://apnews.com/")
        browser.accept_cookies()  # Accept the cookies if present
        browser.click_search_button()
        browser.type_and_submit_search_query(search_phrase)
        browser.click_and_select_category(news_category)
        browser.select_sort_by_newest()
        browser.extract_news_data_and_store()
        # Save a screenshot as proof of successful operations
        final_path="step_5_final_screenshot.png"
        browser.screenshot(filename=final_path)
        work_item.add_work_item_file(path=final_path)
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
