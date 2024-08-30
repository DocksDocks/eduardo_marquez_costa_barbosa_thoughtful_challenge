from ExtendedSelenium import ExtendedSelenium

def the_process():
    browser = ExtendedSelenium()
    try:
        browser.open_site("https://apnews.com/")
        browser.close_popup_if_present()  # Close the popup if it appears
        browser.click_search_button()  # Click the search button after closing the popup
        browser.type_and_submit_search_query("COVID")  # Type "COVID" into the search input
        browser.click_and_select_category()  # Click and select the "Stories" category
        browser.select_sort_by_newest()  # Sort by Newest
        browser.extract_news_data_and_store()  # Extract news data and store in Excel
    finally:
        browser.quit_driver()

if __name__ == "__main__":
    the_process()
