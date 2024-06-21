import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
        
        # Find all text content in the article
        text_content = ' '.join([p.text.strip() for p in soup.find_all('p')])
        
        # Find all links to images in the article
        image_links = [img['src'] for img in soup.find_all('img')]
        
        # Append the text content and image links to the article_data list
        article_data.append({'text_content': text_content, 'image_links': image_links})
    
    return article_data
