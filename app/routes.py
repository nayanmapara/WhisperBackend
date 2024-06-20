from app import app
from flask import jsonify
from scraping.scraper import scrape_articles, scrape_article_content

@app.route('/scrape')
def scrape():
    # Scrape articles
    scraped_links = scrape_articles()

    # Scrape article content
    article_content = scrape_article_content(scraped_links)

    return jsonify(article_content)
