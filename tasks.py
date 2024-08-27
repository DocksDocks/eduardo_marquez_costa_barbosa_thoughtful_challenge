from ExtendedSelenium import ExtendedSelenium

def capture_screenshot():
    browser = ExtendedSelenium()
    try:
        browser.open_site("https://apnews.com/")
        browser.close_popup_if_present()  # Close the popup if it appears
        browser.click_search_button()  # Click the search button after closing the popup
        browser.capture_page_screenshot("output/final_page_screenshot.png")
    finally:
        browser.quit_driver()

if __name__ == "__main__":
    capture_screenshot()
