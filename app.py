from flask import Flask, jsonify
from scraping.scraper import monthly_report

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to CanScrape!'

@app.route('/scrape')
def scrape():
    return jsonify(monthly_report())


if __name__ == '__main__':
    app.run(debug=True)