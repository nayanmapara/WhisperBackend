from flask import Flask, jsonify
from scraping.scraper import scrape_links, scrape_article_content

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to CanScrape!'

@app.route('/scrape')
def scrape():
    # Scrape articles
    scraped_links = scrape_links()

    # Scrape article content
    article_content = scrape_article_content(scraped_links)

    return jsonify(article_content)


if __name__ == '__main__':
    app.run(debug=True)