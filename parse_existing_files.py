#!/usr/bin/env python3
"""
Simple parser for existing HTML files from Sivas website
Converts HTML to structured JSON for the AI advisor
"""

import os
import json
from bs4 import BeautifulSoup
import re
from pathlib import Path

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def extract_content_from_html(file_path):
    """Extract meaningful content from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='iso-8859-1') as f:
            html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Extract title
    title = ""
    title_tag = soup.find('title')
    if title_tag:
        title = clean_text(title_tag.get_text())
    
    # Extract main content - try different selectors
    content_selectors = [
        'main',
        '.content',
        '#content', 
        '.main-content',
        'article',
        '.container'
    ]
    
    main_content = ""
    for selector in content_selectors:
        content_div = soup.select_one(selector)
        if content_div:
            main_content = clean_text(content_div.get_text())
            break
    
    # If no main content found, get body text
    if not main_content:
        body = soup.find('body')
        if body:
            main_content = clean_text(body.get_text())
    
    # Extract headers
    headers = []
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        header_text = clean_text(header.get_text())
        if header_text:
            headers.append(header_text)
    
    # Extract paragraphs
    paragraphs = []
    for p in soup.find_all('p'):
        p_text = clean_text(p.get_text())
        if p_text and len(p_text) > 10:  # Only meaningful paragraphs
            paragraphs.append(p_text)
    
    return {
        'title': title,
        'headers': headers,
        'paragraphs': paragraphs,
        'content': main_content
    }

def categorize_page(filename):
    """Categorize page based on filename"""
    categories = {
        'index': 'overview',
        'see': 'attractions', 
        'taste': 'food',
        'touch': 'activities',
        'smell': 'culture',
        'listen': 'culture',
        '48-hours': 'itinerary',
        '10-vibes': 'experiences',
        'about-sivas': 'general',
        'routes': 'travel'
    }
    
    for key, category in categories.items():
        if key in filename.lower():
            return category
    
    return 'general'

def main():
    html_dir = "sivas_site/sivas_site"
    output_dir = "scraped_data"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    parsed_data = []
    
    # Process all HTML files
    for filename in os.listdir(html_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(html_dir, filename)
            print(f"📄 Обрабатываю {filename}...")
            
            content = extract_content_from_html(file_path)
            
            page_data = {
                'url': f"https://sivas.goturkiye.com/{filename}",
                'filename': filename,
                'title': content['title'],
                'category': categorize_page(filename),
                'headers': content['headers'],
                'paragraphs': content['paragraphs'],
                'content': content['content'],
                'word_count': len(content['content'].split()) if content['content'] else 0
            }
            
            parsed_data.append(page_data)
            print(f"   ✅ Извлечено {page_data['word_count']} слов")
    
    # Save to JSON
    output_file = os.path.join(output_dir, "sivas_content.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Обработано {len(parsed_data)} страниц")
    print(f"📊 Данные сохранены в {output_file}")
    
    # Print summary
    total_words = sum(page['word_count'] for page in parsed_data)
    categories = {}
    for page in parsed_data:
        cat = page['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📈 Статистика:")
    print(f"   Всего слов: {total_words}")
    print(f"   Категории: {categories}")

if __name__ == "__main__":
    main()
