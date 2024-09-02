# tasks.py
import logging
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
    work_item = WorkItems()
    work_item.get_input_work_item()
    browser = ExtendedSelenium()
    try:
        url = "https://apnews.com/"
        browser.open_site(url)
        browser.capture_page_screenshot(
            "output/screenshots/test_open_page.png")
        work_item.release_input_work_item(State.DONE)
    except Exception as e:
        logging.error(f"Failed during minimal test: {e}")
        work_item.release_input_work_item(State.FAILED)
    finally:
        browser.quit_driver()


if __name__ == "__main__":
    the_process()
