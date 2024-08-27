# tasks.py

from news_scraper import NewsScraper
from RPA.Robocorp.WorkItems import WorkItems
import logging

logging.basicConfig(level=logging.INFO)

def process_news():
    logging.info("Starting news scraping process")
    work_items = WorkItems()
    work_items.get_input_work_item()

    search_phrase = work_items.get_work_item_variable("search_phrase")
    category = work_items.get_work_item_variable("category")
    months = int(work_items.get_work_item_variable("months", 0))

    scraper = NewsScraper()
    try:
        articles = scraper.search_news(search_phrase, category)
        filtered_articles = scraper.filter_articles_by_date(articles, months)
        articles_data = [scraper.extract_article_info(article) for article in filtered_articles]

        scraper.save_to_excel(articles_data, search_phrase)
        logging.info("Completed news scraping process")

        work_items.complete_work_item()
    finally:
        scraper.close()

if __name__ == "__main__":
    process_news()
