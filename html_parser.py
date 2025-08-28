#!/usr/bin/env python3
"""
HTML Parser for Local Sivas Website Files
Extracts content from downloaded HTML files and converts to structured data
"""

import os
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from pathlib import Path
import logging
from config import SCRAPED_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalSivasHTMLParser:
    def __init__(self, html_directory="sivas_site/sivas_site"):
        self.html_directory = html_directory
        self.parsed_data = []
        self.base_url = "https://sivas.goturkiye.com"
        
        # Ensure output directory exists
        os.makedirs(SCRAPED_DATA_DIR, exist_ok=True)
    
    def clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove HTML entities
        text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
        return text.strip()
    
    def extract_page_content(self, html_file_path):
        """Extract content from a single HTML file"""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract basic metadata
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ""
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '') if meta_desc else ""
            
            # Determine URL from filename
            filename = os.path.basename(html_file_path)
            if filename == 'index.html':
                url = self.base_url + "/"
                page_name = "homepage"
            else:
                page_name = filename.replace('.html', '')
                url = f"{self.base_url}/{page_name}"
                if page_name == "10-vibes":
                    url = f"{self.base_url}/10-vibes-for-sivas-like-locals"
                elif page_name == "48-hours":
                    url = f"{self.base_url}/48-hours"
            
            # Extract headings
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                heading_text = self.clean_text(h.get_text())
                if heading_text and len(heading_text) > 2:
                    headings.append({
                        'level': h.name,
                        'text': heading_text
                    })
            
            # Extract main content - look for content containers
            main_content = ""
            content_selectors = [
                '.container-reading-narrow',
                '.page-detail-header',
                'main',
                '.content',
                '.main-content',
                'article',
                '.page-content',
                '#content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style", "nav", "footer", "header"]):
                        script.decompose()
                    
                    content_text = content_elem.get_text(separator='\n', strip=True)
                    main_content += content_text + "\n"
            
            # If no main content found, extract from body
            if not main_content.strip():
                body = soup.find('body')
                if body:
                    # Remove unwanted elements
                    for element in body(["script", "style", "nav", "footer", "header", "noscript"]):
                        element.decompose()
                    
                    # Remove cookie consent and tracking elements
                    for element in body.find_all(['div', 'span'], id=re.compile(r'onetrust|gtag|clarity')):
                        element.decompose()
                    
                    main_content = body.get_text(separator='\n', strip=True)
            
            main_content = self.clean_text(main_content)
            
            # Extract images with alt text
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src and not src.startswith('data:'):
                    # Convert relative URLs to absolute
                    if src.startswith('./'):
                        src = src[2:]
                    if not src.startswith('http'):
                        src = urljoin(url, src)
                    
                    images.append({
                        'src': src,
                        'alt': self.clean_text(alt)
                    })
            
            # Extract navigation links
            links = []
            nav_links = soup.find_all('a', href=True)
            for link in nav_links:
                href = link.get('href')
                text = self.clean_text(link.get_text())
                
                if href and text and not href.startswith('#') and not href.startswith('javascript:'):
                    # Convert to absolute URL
                    if href.startswith('./'):
                        href = href[2:]
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    links.append({
                        'url': href,
                        'text': text
                    })
            
            return {
                'url': url,
                'page_name': page_name,
                'title': title,
                'description': description,
                'headings': headings,
                'content': main_content,
                'images': images[:10],  # Limit images
                'links': links[:20],   # Limit links
                'scraped_at': time.time(),
                'source': 'local_html'
            }
            
        except Exception as e:
            logger.error(f"Error parsing {html_file_path}: {e}")
            return None
    
    def parse_all_files(self):
        """Parse all HTML files in the directory"""
        html_files = []
        
        # Find all HTML files
        if os.path.exists(self.html_directory):
            for file in os.listdir(self.html_directory):
                if file.endswith('.html'):
                    html_files.append(os.path.join(self.html_directory, file))
        
        logger.info(f"Found {len(html_files)} HTML files to parse")
        
        for html_file in html_files:
            logger.info(f"Parsing: {html_file}")
            page_data = self.extract_page_content(html_file)
            
            if page_data:
                self.parsed_data.append(page_data)
                logger.info(f"Successfully parsed: {page_data['page_name']}")
            else:
                logger.warning(f"Failed to parse: {html_file}")
        
        return self.parsed_data
    
    def save_data(self, filename='sivas_content.json'):
        """Save parsed data to JSON file"""
        filepath = os.path.join(SCRAPED_DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.parsed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.parsed_data)} pages to {filepath}")
        
        # Also save a summary
        summary_file = os.path.join(SCRAPED_DATA_DIR, 'parsing_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Sivas Website Content Parsing Summary\n")
            f.write(f"=" * 40 + "\n\n")
            f.write(f"Total pages parsed: {len(self.parsed_data)}\n")
            f.write(f"Parsing date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Pages:\n")
            for page in self.parsed_data:
                f.write(f"- {page['page_name']}: {page['title']}\n")
                f.write(f"  Content length: {len(page['content'])} chars\n")
                f.write(f"  Headings: {len(page['headings'])}\n")
                f.write(f"  Images: {len(page['images'])}\n\n")
    
    def get_page_types(self):
        """Classify pages by type for better organization"""
        page_types = {}
        
        for page in self.parsed_data:
            page_name = page['page_name']
            title = page['title'].lower()
            content = page['content'].lower()
            
            if page_name == 'homepage' or 'homepage' in title:
                page_type = 'general'
            elif page_name == 'see' or 'достопримечательност' in content or 'historical' in content:
                page_type = 'historical'
            elif page_name == 'taste' or 'food' in content or 'cuisine' in content or 'restaurant' in content:
                page_type = 'food'
            elif page_name == 'touch' or 'handicraft' in content or 'carpet' in content or 'craft' in content:
                page_type = 'activity'
            elif page_name == 'smell' or 'nature' in content or 'natural' in content:
                page_type = 'nature'
            elif page_name == 'listen' or 'music' in content or 'culture' in content:
                page_type = 'culture'
            elif page_name == 'routes' or 'route' in content or 'travel' in content:
                page_type = 'route'
            elif '48-hours' in page_name or '10-vibes' in page_name:
                page_type = 'guide'
            else:
                page_type = 'general'
            
            page_types[page_name] = page_type
            page['page_type'] = page_type
        
        return page_types

def main():
    """Main function to parse HTML files"""
    parser = LocalSivasHTMLParser()
    
    logger.info("Starting HTML parsing...")
    
    # Parse all files
    parsed_data = parser.parse_all_files()
    
    if not parsed_data:
        logger.error("No data was parsed. Check the HTML directory path.")
        return
    
    # Classify page types
    page_types = parser.get_page_types()
    logger.info(f"Page types: {page_types}")
    
    # Save data
    parser.save_data()
    
    logger.info("HTML parsing completed successfully!")
    
    # Print summary
    print("\n" + "=" * 50)
    print("PARSING SUMMARY")
    print("=" * 50)
    
    for page in parsed_data:
        print(f"\n📄 {page['page_name'].upper()}")
        print(f"   Title: {page['title']}")
        print(f"   Type: {page.get('page_type', 'unknown')}")
        print(f"   Content: {len(page['content'])} characters")
        print(f"   URL: {page['url']}")

if __name__ == "__main__":
    main()
