from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from scraping.scraper import scrape_links

app = Flask(__name__)

# Initialize Flask-Limiter with Redis
limiter = Limiter(
    get_remote_address,
    app=app
)

@app.route('/')
def index():
    return 'Welcome to CanScrape!'

@app.route('/scrape')
# @limiter.limit("10 per month")
def scrape():
    return jsonify(scrape_links())


if __name__ == '__main__':
    app.run(debug=True)