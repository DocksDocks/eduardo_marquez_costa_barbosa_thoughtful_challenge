import logging
from dotenv import load_dotenv
from RPA.Robocorp.WorkItems import WorkItems, State
from ExtendedSelenium import ExtendedSelenium

load_dotenv()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def the_process():
    """
    Main function to perform the web automation process.

    This function retrieves input work items, uses a custom Selenium browser to perform
    web interactions such as searching for a term on a news website, selecting a category,
    sorting results, and extracting data. It also handles exceptions and ensures that the
    browser is properly closed after execution. The work item is marked as 'DONE' upon
    successful completion or 'FAILED' in case of errors.

    Raises:
        Exception: If an error occurs during the process, it is logged, and the work item is
                   marked as 'FAILED'.
    """
    work_item = WorkItems()
    browser = ExtendedSelenium(work_item=work_item)
    try:
        if not work_item.get_input_work_item() or not work_item.current:
            logging.error(
                "No valid input work item or no active work item. Exiting process.")
            return
        search_phrase = work_item.get_work_item_variable(
            "search_phrase", "COVID")
        news_category = work_item.get_work_item_variable(
            "news_category", "Stories")
        browser.open_site(url="https://apnews.com/")
        browser.accept_cookies()  # Accept the cookies if present
        browser.click_search_button()
        browser.type_and_submit_search_query(search_phrase)
        browser.click_and_select_category(news_category)
        browser.select_sort_by_newest()
        browser.extract_news_data_and_store()
        browser.save_screenshot_to_work_item(
            filename="output/step_5_final_screenshot.png")
        work_item.release_input_work_item(State.DONE)
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        if work_item.current:
            work_item.release_input_work_item(State.FAILED)
    finally:
        browser.close_all_browsers()


if __name__ == "__main__":
    the_process()
