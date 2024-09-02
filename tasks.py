from dotenv import load_dotenv
from RPA.Robocorp.WorkItems import WorkItems, State
from ExtendedSelenium import ExtendedSelenium

# Load environment variables from .env file
load_dotenv()

def the_process():
    work_item = WorkItems()
    work_item.get_input_work_item()

    # Retrieve variables from the work item
    search_phrase = work_item.get_work_item_variable("search_phrase", "COVID")
    news_category = work_item.get_work_item_variable("news_category", "Stories")

    browser = ExtendedSelenium()
    try:
        # Perform the browser automation tasks
        browser.open_site("https://apnews.com/")
        browser.close_popup_if_present()
        browser.click_search_button()
        browser.type_and_submit_search_query(search_phrase)
        browser.click_and_select_category(news_category)
        browser.select_sort_by_newest()
        browser.extract_news_data_and_store()

        # If successful, release the work item with DONE state
        work_item.release_input_work_item(State.DONE)
    except Exception as e:
        # If an error occurs, release the work item with FAILED state
        work_item.release_input_work_item(State.FAILED)
        raise e  # Re-raise the exception to handle it outside the function if needed
    finally:
        browser.quit_driver()

if __name__ == "__main__":
    the_process()
