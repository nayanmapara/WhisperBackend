import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def scrape_links():
    keywords = ['international student', 'work permit', 'study permit', 'post-graduation work permit', 'PGWP', 'study visa', 'work visa', 'permanent residency', 'PR', 'express entry', 'family sponsorship', 'spousal sponsorship', 'parental sponsorship', 'super visa', 'visitor visa', 'temporary resident visa', 'TRV']
    domain = 'https://www.canada.ca'  # Domain name
    urls = [
        '/en/immigration-refugees-citizenship/news/notices.html',
        '/en/immigration-refugees-citizenship/news.html',
    ]
    links = []
    for url in urls:
        response = requests.get(urljoin(domain, url))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links
        for link in soup.find_all('a'):
            text = link.text.lower()
            # Check if any of the keywords are present in the link text
            if any(keyword in text for keyword in keywords):
                links.append(urljoin(domain, link.get('href')))
    
    return links

def scrape_article_content(links):
    article_data = []
    for link in links:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the dates of the articles
        dates = [date.text for date in soup.find_all('time')]
        
        # Find all text content in the article
        text_content = ' '.join([p.text.strip() for p in soup.find_all('p')])

        # Append the text content and image links to the article_data list
        article_data.append({'date': dates, 'text_content': text_content})

    return article_data

def monthly_report():
    latest_articles = []

    # Scrape articles
    scraped_links = scrape_links()

    # Scrape article content
    article_content = scrape_article_content(scraped_links)

    if len(article_content) != 0:
        # if article_content[0]['date'][0] == datetime.date():
        # print(datetime.strptime(article_content[0]['date'][0], '%Y-%m-%d'))
        # print(type(datetime.strptime(article_content[0]['date'][0], '%Y-%m-%d')))
        # print(datetime.now().date())

        # Checking if the article was released in the same month and year as the current date
        if datetime.strptime(article_content[0]['date'][0], '%Y-%m-%d').month == datetime.now().month and datetime.strptime(article_content[0]['date'][0], '%Y-%m-%d').year == datetime.now().year:
            # print(f"Article date: {article_content[0]['date'][0]}")
            latest_articles.append(article_content[0]['text_content'])

        else:
            # print(f"Article date: {article_content[0]['date'][0]}")
            # print('Monthly report is not up to date.')
            return False
    else:
        return 'No articles found for the given keywords.'
    
    return article_content