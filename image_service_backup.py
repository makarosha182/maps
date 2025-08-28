import requests
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class UnsplashImageService:
    """Service for searching and retrieving images from Unsplash"""
    
    def __init__(self):
        # Using official Unsplash API
        self.base_url = "https://api.unsplash.com"
        self.search_url = "https://api.unsplash.com/search/photos"
        
        # Unsplash API credentials
        self.access_key = "8bopXYR-oZP1zKvbHx86c5CTQkjLkt7eoQarlEyuWdU"
        self.secret_key = "Ji9nwTInIi7vgVuXJt-JzcW2MqkiqQh768VcUPtsnUA"
        
        self.headers = {
            "Authorization": f"Client-ID {self.access_key}",
            "Content-Type": "application/json"
        }
    
    def parse_claude_response(self, response_text: str) -> List[Dict]:
        """Parse Claude response to extract specific items (dishes, places, etc.)"""
        items = []
        
        # Patterns for different list formats
        patterns = [
            r'(\d+)\.\s*([^\n\r]+?)(?:\s*\n|$)',  # "1. Item Name"
            r'[-*]\s*([^\n\r]+?)(?:\s*\n|$)',     # "- Item Name" 
            r'##\s*([^\n\r]+)',                   # "## Item Name"
            r'\*\*([^*\n]+)\*\*',                 # "**Item Name**"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # For numbered lists, take the second group (item name)
                    item_name = match[1].strip() if len(match) > 1 else match[0].strip()
                else:
                    item_name = match.strip()
                
                # Clean up the item name
                item_name = item_name.replace('(', '').replace(')', '')
                item_name = re.sub(r'\s+', ' ', item_name)  # Remove extra spaces
                
                # Basic filtering - keep item names that look like proper nouns
                item_lower = item_name.lower().strip()
                
                # Skip very short items or obvious descriptions
                if (len(item_name) > 3 and 
                    not item_lower.startswith(('the ', 'a ', 'an ', 'this ', 'that ')) and
                    len(item_name.split()) <= 5):  # Not too many words
                    
                    items.append({
                        'name': item_name.strip(),
                        'original': match
                    })
        
        # Remove duplicates and limit to most relevant items
        unique_items = []
        seen_names = set()
        for item in items:
            name_lower = item['name'].lower()
            if name_lower not in seen_names and len(name_lower) > 3:
                unique_items.append(item)
                seen_names.add(name_lower)
                
        return unique_items[:5]  # Limit to 5 most relevant items
    
    def detect_response_category(self, query: str, response_text: str) -> str:
        """Detect what type of content the response is about"""
        query_lower = query.lower()
        response_lower = response_text.lower()
        
        # Food-related keywords
        food_keywords = ['food', 'dish', 'cuisine', 'eat', 'restaurant', 'meal', 'cooking', 'recipe', 'köfte', 'çorba', 'kebab']
        if any(keyword in query_lower or keyword in response_lower for keyword in food_keywords):
            return 'food'
            
        # Architecture/building keywords  
        architecture_keywords = ['mosque', 'medrese', 'castle', 'building', 'architecture', 'monument', 'structure', 'cami', 'kale']
        if any(keyword in query_lower or keyword in response_lower for keyword in architecture_keywords):
            return 'architecture'
            
        # Places/attractions keywords
        places_keywords = ['museum', 'park', 'square', 'market', 'bazaar', 'attraction', 'site', 'place', 'visit']
        if any(keyword in query_lower or keyword in response_lower for keyword in places_keywords):
            return 'places'
            
        # History keywords
        history_keywords = ['history', 'historical', 'ancient', 'empire', 'period', 'century', 'ottoman', 'seljuk']
        if any(keyword in query_lower or keyword in response_lower for keyword in history_keywords):
            return 'history'
            
        return 'general'
        
    def create_specific_search_terms(self, items: List[Dict], category: str) -> List[str]:
        """Create specific search terms based on extracted items and category"""
        search_terms = []
        
        for item in items:
            item_name = item['name']
            
            if category == 'food':
                # For food items, create specific dish searches
                search_terms.extend([
                    f"{item_name} sivas turkey",
                    f"sivas {item_name}",
                    f"{item_name} turkish food"
                ])
            elif category == 'architecture':
                # For architecture, focus on buildings and structures
                search_terms.extend([
                    f"{item_name} sivas turkey",
                    f"sivas {item_name}",
                    f"{item_name} architecture turkey"
                ])
            elif category == 'places':
                # For places and attractions
                search_terms.extend([
                    f"{item_name} sivas turkey",
                    f"sivas {item_name}",
                    f"{item_name} tourist attraction"
                ])
            else:
                # General items
                search_terms.extend([
                    f"sivas {item_name} turkey",
                    f"{item_name} sivas"
                ])
        
        # If we have specific items, limit to their count, otherwise use 3 default
        limit = min(len(items), 3) if items else 3
        return search_terms[:limit * 2]  # 2 search terms per item max
    
    def extract_keywords_for_images(self, response_text: str, query: str) -> List[str]:
        """Extract keywords based on Claude's response content"""
        
        # Parse the response to find specific items
        items = self.parse_claude_response(response_text)
        category = self.detect_response_category(query, response_text)
        
        logger.info(f"Found {len(items)} items in response, category: {category}")
        for item in items:
            logger.info(f"  - {item['name']}")
        
        # If we found specific items, create targeted search terms
        if items:
            keywords = self.create_specific_search_terms(items, category)
        else:
            # Fallback to general search based on query
            query_lower = query.lower()
            if "food" in query_lower or "dish" in query_lower or "cuisine" in query_lower:
                keywords = ["sivas food turkey", "sivas cuisine", "sivas traditional food"]
            elif "castle" in query_lower or "fortress" in query_lower:
                keywords = ["sivas castle turkey", "sivas kale", "sivas fortress"]
            elif "mosque" in query_lower or "cami" in query_lower:
                keywords = ["sivas mosque turkey", "sivas ulu cami"]
            elif "medrese" in query_lower:
                keywords = ["cifte minareli medrese sivas", "sivas medrese turkey"]
            else:
                keywords = ["sivas city turkey", "sivas anatolia", "sivas center turkey"]
        
        # Ensure we have at least basic search terms
        if not keywords:
            keywords = ["sivas turkey"]
            
        return keywords[:3]  # Limit to 3 most relevant keywords
    
    def search_images(self, keywords: List[str], limit: int = 3) -> List[Dict]:
        """Search for images using official Unsplash API"""
        images = []
        
        for keyword in keywords[:limit]:
            try:
                # Search using official Unsplash API
                params = {
                    "query": keyword,
                    "per_page": 1,
                    "orientation": "landscape"
                }
                
                response = requests.get(
                    self.search_url, 
                    headers=self.headers, 
                    params=params, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("results") and len(data["results"]) > 0:
                        photo = data["results"][0]
                        
                        images.append({
                            "url": photo["urls"]["regular"],  # High quality image
                            "thumb_url": photo["urls"]["small"],  # Thumbnail
                            "alt": photo.get("alt_description", f"Image related to {keyword}"),
                            "title": keyword.title(),
                            "source": "Unsplash",
                            "photographer": photo["user"]["name"],
                            "photographer_url": photo["user"]["links"]["html"]
                        })
                        logger.info(f"Found image for keyword: {keyword}")
                    else:
                        logger.warning(f"No images found for keyword: {keyword}")
                else:
                    logger.error(f"Unsplash API error for '{keyword}': {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error searching image for '{keyword}': {e}")
                continue
                
        # If no images found, try a general Sivas search
        if not images:
            try:
                params = {
                    "query": "sivas turkey",
                    "per_page": 1,
                    "orientation": "landscape"
                }
                
                response = requests.get(
                    self.search_url, 
                    headers=self.headers, 
                    params=params, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results") and len(data["results"]) > 0:
                        photo = data["results"][0]
                        images.append({
                            "url": photo["urls"]["regular"],
                            "thumb_url": photo["urls"]["small"],
                            "alt": photo.get("alt_description", "Sivas, Turkey"),
                            "title": "Sivas City",
                            "source": "Unsplash",
                            "photographer": photo["user"]["name"],
                            "photographer_url": photo["user"]["links"]["html"]
                        })
            except Exception as e:
                logger.error(f"Error getting default Sivas image: {e}")
            
        return images
    
    def get_images_for_response(self, query: str, claude_response: str) -> List[Dict]:
        """Get relevant images for a Claude response with smart parsing"""
        try:
            # Parse response to find specific items
            items = self.parse_claude_response(claude_response)
            category = self.detect_response_category(query, claude_response)
            
            logger.info(f"Smart image search - Category: {category}, Items found: {len(items)}")
            
            # Extract targeted keywords
            keywords = self.extract_keywords_for_images(claude_response, query)
            logger.info(f"Search keywords: {keywords}")
            
            # Search for images with appropriate limit
            # If we found specific items, try to get one image per item (up to 3)
            image_limit = min(len(items), 3) if items else 3
            images = self.search_images(keywords, limit=image_limit)
            
            # Add context information to images
            for i, image in enumerate(images):
                if items and i < len(items):
                    image['related_item'] = items[i]['name']
                    image['category'] = category
                    # Update title to be more specific
                    image['title'] = items[i]['name']
                else:
                    image['category'] = category
            
            logger.info(f"Found {len(images)} contextual images")
            return images
            
        except Exception as e:
            logger.error(f"Error getting images: {e}")
            return []

# Global instance
image_service = UnsplashImageService()
