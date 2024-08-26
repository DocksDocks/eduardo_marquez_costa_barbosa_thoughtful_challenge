from RPA.Browser.Selenium import Selenium

browser = Selenium()

try:
    browser.open_available_browser("https://www.apnews.com/")
finally:
    browser.close_all_browsers()
