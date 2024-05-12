import requests
from bs4 import BeautifulSoup
import csv
import os

def fetch_and_parse(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def save_to_csv(filename, data):
    directory = os.path.dirname(filename)
    if directory:
        os.makedirs(directory, exist_ok=True)  # Ensure the directory exists
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Description', 'Link'])  # Writing headers
        for item in data:
            writer.writerow([item['title'], item['description'], item['link']])

def extract_dawn_links_and_articles(soup):
    links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href']]
    articles = []
    for article in soup.find_all('article'):
        title = article.find('h2').get_text(strip=True) if article.find('h2') else ''
        description = article.find('p').get_text(strip=True) if article.find('p') else ''
        articles.append({'title': title, 'description': description, 'link': article.find('a')['href']})
    return links, articles

def extract_bbc_links_and_articles(soup):
    links = [a['href'] for a in soup.find_all('a', href=True) if 'http' in a['href']]
    articles = []
    for div in soup.find_all('div', class_='gs-c-promo'):
        title = div.find('h3').get_text(strip=True) if div.find('h3') else ''
        description = div.find('p').get_text(strip=True) if div.find('p') else ''
        link = div.find('a')['href']
        articles.append({'title': title, 'description': description, 'link': link})
    return links, articles

def extract_and_save_data(url, soup, extractor):
    base_dir = "scraped_data"
    if soup:
        links, articles = extractor(soup)
        links_filename = os.path.join(base_dir, f"{url.replace('https://', '').replace('www.', '').replace('/', '_')}_links.csv")
        articles_filename = os.path.join(base_dir, f"{url.replace('https://', '').replace('www.', '').replace('/', '_')}_articles.csv")
        save_to_csv(links_filename, [{'title': '', 'description': '', 'link': link} for link in links])
        save_to_csv(articles_filename, articles)

def main():
    urls = {
        'https://www.dawn.com/': extract_dawn_links_and_articles,
        'https://www.bbc.com/': extract_bbc_links_and_articles,
    }
    
    for url, extractor in urls.items():
        print(f"Scraping {url}")
        soup = fetch_and_parse(url)
        extract_and_save_data(url, soup, extractor)

if __name__ == "__main__":
    main()
