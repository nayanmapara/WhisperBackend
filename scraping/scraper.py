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
        '/en/news/advanced-news-search/news-results.html?typ=newsreleases&dprtmnt=departmentofcitizenshipandimmigration',
    ]

    links = [] 
    for url in urls:
        response = requests.get(urljoin(domain, url))
        soup = BeautifulSoup(response.content, 'html.parser')
        print(url)
        
        # Find all links
        for link in soup.find_all('a'):
            text = link.text.lower()
            href = link.get('href') # Get the URL
            full_url = urljoin(domain, href) # Get the full URL

            # Check if any of the keywords are present in the link text or URL
            if any(keyword.lower() in text or keyword.lower().replace(" ", "_") in href.lower() for keyword in keywords):
                data = scrape_article_content(full_url) # Scrape the article content
                if data:
                    links.append(data) # Append the data to the list of links
                else:
                    break

    return links

def scrape_article_content(link):
    '''Scrape the content of the articles based on the provided links.'''

    response = requests.get(link) # Get the article content
    soup = BeautifulSoup(response.content, 'html.parser') # Parse the HTML content

    # Find the date of the article
    date = soup.find('time')
    if date:
        date = date.text.strip()
    
    # Find all text content in the article
    text_content = ' '.join([p.text.strip() for p in soup.find_all('p')])

    if date_checker(date) == True:
        return {'date': date, 'url': link, 'text_content': text_content} # Return the date and text content
    else:
        return False

def date_checker(date):
    '''Check if the article was released in the same month and year as the current date.'''

    current_date = datetime.now()
    # current_date = datetime(2024, 5, 10) # For testing purposes 
    article_date = datetime.strptime(date, '%Y-%m-%d') # Convert the date string to a datetime object

    if article_date.month == current_date.month and article_date.year == current_date.year:
        return True # Return True if the article was released in the same month and year
    else:
        return False # Return False if the article was not released in the same month and year

if __name__ == "__main__":
    links = scrape_links()
    print(links)