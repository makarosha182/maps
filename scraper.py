import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin, urlparse
import time
import json
import os
from typing import Set, List, Dict, Optional
import logging
from config import BASE_URL, SCRAPED_DATA_DIR, MAX_PAGES, DELAY_BETWEEN_REQUESTS, REQUEST_TIMEOUT

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SivasWebScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.scraped_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Setup Selenium for dynamic content
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Create data directory
        os.makedirs(SCRAPED_DATA_DIR, exist_ok=True)
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to the target domain"""
        parsed = urlparse(url)
        target_domain = urlparse(self.base_url).netloc
        return parsed.netloc == target_domain
    
    def get_page_content_selenium(self, url: str) -> Optional[BeautifulSoup]:
        """Get page content using Selenium for dynamic content"""
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for dynamic content to load
            
            # Scroll to bottom to load any lazy content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            html_content = self.driver.page_source
            return BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logger.error(f"Error loading page with Selenium {url}: {e}")
            return None
    
    def get_page_content_requests(self, url: str) -> Optional[BeautifulSoup]:
        """Get page content using requests"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error loading page with requests {url}: {e}")
            return None
    
    def extract_page_data(self, url: str, soup: BeautifulSoup) -> Dict:
        """Extract structured data from a page"""
        try:
            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ""
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            # Extract headings
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                headings.append({
                    'level': h.name,
                    'text': h.get_text().strip()
                })
            
            # Extract main content
            content_selectors = [
                'main', '.content', '.main-content', 
                '.post-content', '.entry-content', 'article',
                '.page-content', '#content'
            ]
            
            main_content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    main_content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # If no main content found, extract from body
            if not main_content:
                body = soup.find('body')
                if body:
                    # Remove script and style elements
                    for script in body(["script", "style", "nav", "footer", "header"]):
                        script.decompose()
                    main_content = body.get_text(separator='\n', strip=True)
            
            # Extract images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src:
                    images.append({
                        'src': urljoin(url, src),
                        'alt': alt
                    })
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                if href and text:
                    full_url = urljoin(url, href)
                    links.append({
                        'url': full_url,
                        'text': text
                    })
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'headings': headings,
                'content': main_content,
                'images': images,
                'links': links,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {e}")
            return {'url': url, 'error': str(e)}
    
    def find_all_links(self, soup: BeautifulSoup, current_url: str) -> Set[str]:
        """Find all internal links on a page"""
        links = set()
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(current_url, href)
                if self.is_valid_url(full_url):
                    # Clean URL (remove fragments and query params for deduplication)
                    clean_url = full_url.split('#')[0].split('?')[0]
                    links.add(clean_url)
        return links
    
    def scrape_page(self, url: str) -> Optional[Dict]:
        """Scrape a single page"""
        if url in self.scraped_urls or len(self.scraped_urls) >= MAX_PAGES:
            return None
        
        logger.info(f"Scraping: {url}")
        self.scraped_urls.add(url)
        
        # Try Selenium first for dynamic content
        soup = self.get_page_content_selenium(url)
        if not soup:
            # Fallback to requests
            soup = self.get_page_content_requests(url)
        
        if not soup:
            return None
        
        # Extract page data
        page_data = self.extract_page_data(url, soup)
        
        # Find new links to scrape
        new_links = self.find_all_links(soup, url)
        page_data['found_links'] = list(new_links)
        
        time.sleep(DELAY_BETWEEN_REQUESTS)
        return page_data
    
    def scrape_website(self, start_url: Optional[str] = None) -> List[Dict]:
        """Scrape the entire website"""
        if not start_url:
            start_url = self.base_url
        
        urls_to_scrape = [start_url]
        
        while urls_to_scrape and len(self.scraped_data) < MAX_PAGES:
            current_url = urls_to_scrape.pop(0)
            
            if current_url in self.scraped_urls:
                continue
            
            page_data = self.scrape_page(current_url)
            if page_data:
                self.scraped_data.append(page_data)
                
                # Add new links to scrape queue
                if 'found_links' in page_data:
                    for link in page_data['found_links']:
                        if link not in self.scraped_urls and link not in urls_to_scrape:
                            urls_to_scrape.append(link)
        
        return self.scraped_data
    
    def save_data(self, filename: str = 'sivas_content.json'):
        """Save scraped data to file"""
        filepath = os.path.join(SCRAPED_DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.scraped_data)} pages to {filepath}")
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    scraper = SivasWebScraper()
    try:
        logger.info("Starting website scraping...")
        scraped_data = scraper.scrape_website()
        
        logger.info(f"Scraped {len(scraped_data)} pages")
        scraper.save_data()
        
        # Save URLs list for reference
        urls_file = os.path.join(SCRAPED_DATA_DIR, 'scraped_urls.txt')
        with open(urls_file, 'w', encoding='utf-8') as f:
            for url in scraper.scraped_urls:
                f.write(f"{url}\n")
        
        logger.info("Scraping completed successfully!")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
