from ExtendedSelenium import ExtendedSelenium

def the_process():
    browser = ExtendedSelenium()
    try:
        browser.open_site("https://apnews.com/")
        browser.close_popup_if_present()
        browser.click_search_button()
        browser.type_and_submit_search_query("COVID")
        browser.click_and_select_category()
        browser.select_sort_by_newest()
        browser.extract_news_data_and_store()
    finally:
        browser.quit_driver()

if __name__ == "__main__":
    the_process()
