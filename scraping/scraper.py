import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def scrape_links():
    '''Scrape links from the Canada.ca website based on specific keywords.'''

    keywords = [
        'international student', 'work permit', 'study permit', 
        'post-graduation work permit', 'PGWP', 'study visa', 
        'work visa', 'permanent residency', 'PR', 'express entry', 
        'family sponsorship', 'spousal sponsorship', 'parental sponsorship', 
        'super visa', 'visitor visa', 'temporary resident visa', 'TRV'
    ]

    domain = 'https://www.canada.ca'  # Domain name
    urls = [
        '/en/immigration-refugees-citizenship/news/notices.html',
        '/en/immigration-refugees-citizenship/news.html',
    ]

    links = set()  # Use a set to avoid duplicate links
    for url in urls:
        response = requests.get(urljoin(domain, url))
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links
        for link in soup.find_all('a'):
            text = link.text.lower()
            href = link.get('href')
            full_url = urljoin(domain, href)
            # Check if any of the keywords are present in the link text or URL
            if any(keyword.lower() in text or keyword.lower().replace(" ", "_") in href.lower() for keyword in keywords):
                links.add(full_url)
    
    return list(links)  # Convert back to list

def scrape_article_content(links):
    '''Scrape the content of the articles based on the provided links.'''

    article_data = []
    for link in links:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the date of the article
        date = soup.find('time')
        if date:
            date = date.text.strip()
        
        # Find all text content in the article
        text_content = ' '.join([p.text.strip() for p in soup.find_all('p')])

        # Append the text content and date to the article_data list
        article_data.append({'date': date, 'text_content': text_content})

    return article_data

def monthly_report(current_date=None):
    '''Generate a monthly report based on the latest articles from the Canada.ca website.'''

    latest_articles = []

    # Use current_date if provided, otherwise use the current date
    if current_date is None:
        current_date = datetime.now()

    # Scrape articles
    scraped_links = scrape_links()

    # Scrape article content
    article_content = scrape_article_content(scraped_links)

    if len(article_content) != 0:
        article_date = datetime.strptime(article_content[0]['date'][0], '%B %d, %Y')
        # Checking if the article was released in the same month and year as the current date
        if article_date.month == current_date.month and article_date.year == current_date.year:
            latest_articles.append(article_content[0]['text_content'])
        else:
            return False
    else:
        return 'No articles found for the given keywords.'
    
    return latest_articles

# Example usage
if __name__ == "__main__":
    report = monthly_report()
    print(report)