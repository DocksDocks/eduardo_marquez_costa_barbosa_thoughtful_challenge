# news_scraper.py

from CustomSelenium import CustomSelenium
from RPA.Tables import Table
import os
import re
from datetime import datetime, timedelta

class NewsScraper:
    def __init__(self):
        self.browser = CustomSelenium()
        self.browser.set_webdriver()

    def search_news(self, search_phrase, category=None):
        self.browser.open_url("https://www.apnews.com/")

        # Locate the search field and enter the search phrase
        self.browser.driver.find_element_by_css_selector('input[type="search"]').send_keys(search_phrase)
        self.browser.driver.find_element_by_css_selector('input[type="search"]').send_keys(u'\ue007')  # Press Enter key

        # Optionally, select a news category/section
        if category:
            self.browser.driver.find_element_by_link_text(category).click()

        # Fetch the latest news
        articles = self.browser.driver.find_elements_by_css_selector('.FeedCard')  # Adjust the selector based on the site structure

        return articles

    def extract_article_info(self, article):
        title = article.find_element_by_css_selector('h1, h2').text  # Adjust selectors as needed
        date = article.find_element_by_css_selector('time').text
        description = article.find_element_by_css_selector('p').text
        img_url = article.find_element_by_css_selector('img').get_attribute('src')

        # Determine if the title or description contains any amount of money
        money_regex = r'\$\d[\d,]*(\.\d+)?|\d+\s*(dollars?|USD)'
        contains_money = bool(re.search(money_regex, title + description))

        return {
            "title": title,
            "date": date,
            "description": description,
            "img_url": img_url,
            "contains_money": contains_money
        }

    def save_to_excel(self, articles_data, search_phrase):
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        excel_path = os.path.join(output_dir, f"{search_phrase}_news.xlsx")

        table = Table(columns=["Title", "Date", "Description", "Image Filename", "Contains Money"])

        for data in articles_data:
            table.add_row([
                data["title"],
                data["date"],
                data["description"],
                data["img_url"].split('/')[-1],
                str(data["contains_money"])
            ])

        table.save_to_file(excel_path)

    def filter_articles_by_date(self, articles, months):
        filtered_articles = []
        current_date = datetime.now()
        time_threshold = current_date - timedelta(days=months * 30)

        for article in articles:
            date_text = article.find_element_by_css_selector('time').text
            article_date = datetime.strptime(date_text, "%Y-%m-%d")

            if article_date >= time_threshold:
                filtered_articles.append(article)

        return filtered_articles

    def close(self):
        self.browser.driver_quit()
