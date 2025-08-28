import requests
import logging
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class UnsplashImageService:
    """Service for searching and retrieving images from Unsplash"""
    
    def __init__(self):
        # Using Unsplash Source API (no API key required for basic usage)
        self.base_url = "https://source.unsplash.com"
        self.search_url = "https://api.unsplash.com/search/photos"
        
        # Unsplash API key (optional, for better quota and features)
        # For now using source.unsplash.com which doesn't require API key
        self.api_key = None
        
    def extract_keywords_for_images(self, text: str, query: str) -> List[str]:
        """Extract relevant keywords for image search from Claude's response and user query"""
        
        # Common Sivas-related terms
        sivas_terms = [
            "sivas", "turkey", "turkish", "anatolia", "historical", "ancient",
            "castle", "fortress", "museum", "mosque", "architecture", "traditional"
        ]
        
        # Extract keywords from query and response
        keywords = []
        
        # Add Sivas as base term
        keywords.append("sivas turkey")
        
        # Extract specific terms from query
        query_lower = query.lower()
        if "castle" in query_lower or "fortress" in query_lower or "kale" in query_lower:
            keywords.append("sivas castle turkey")
            keywords.append("turkish fortress")
        
        if "food" in query_lower or "cuisine" in query_lower or "eat" in query_lower:
            keywords.append("turkish food")
            keywords.append("traditional turkish cuisine")
            
        if "mosque" in query_lower or "cami" in query_lower or "religion" in query_lower:
            keywords.append("sivas mosque turkey")
            keywords.append("turkish mosque")
            
        if "museum" in query_lower or "history" in query_lower:
            keywords.append("sivas museum turkey")
            keywords.append("turkish historical site")
            
        if "architecture" in query_lower or "building" in query_lower:
            keywords.append("sivas architecture turkey")
            keywords.append("turkish traditional architecture")
            
        # If no specific terms found, use general terms
        if len(keywords) == 1:  # Only "sivas turkey"
            keywords.extend([
                "sivas city turkey",
                "central anatolia turkey",
                "turkish city"
            ])
            
        return keywords[:3]  # Limit to 3 most relevant keywords
    
    def search_images(self, keywords: List[str], limit: int = 3) -> List[Dict]:
        """Search for images using Unsplash Source API"""
        images = []
        
        for i, keyword in enumerate(keywords[:limit]):
            try:
                # Using Unsplash Source API for direct image URLs
                # Format: https://source.unsplash.com/800x600/?keyword
                clean_keyword = keyword.replace(" ", ",")
                image_url = f"{self.base_url}/800x600/?{clean_keyword}"
                
                # Verify image exists by making a HEAD request
                response = requests.head(image_url, timeout=5)
                if response.status_code == 200:
                    images.append({
                        "url": image_url,
                        "alt": f"Image related to {keyword}",
                        "title": keyword.title(),
                        "source": "Unsplash"
                    })
                    logger.info(f"Found image for keyword: {keyword}")
                else:
                    logger.warning(f"Image not found for keyword: {keyword}")
                    
            except Exception as e:
                logger.error(f"Error searching image for '{keyword}': {e}")
                continue
                
        # If no images found, add a default Sivas image
        if not images:
            default_url = f"{self.base_url}/800x600/?sivas,turkey,city"
            images.append({
                "url": default_url,
                "alt": "Sivas, Turkey",
                "title": "Sivas City",
                "source": "Unsplash"
            })
            
        return images
    
    def get_images_for_response(self, query: str, claude_response: str) -> List[Dict]:
        """Get relevant images for a Claude response"""
        try:
            keywords = self.extract_keywords_for_images(claude_response, query)
            logger.info(f"Extracted keywords for images: {keywords}")
            
            images = self.search_images(keywords)
            logger.info(f"Found {len(images)} images")
            
            return images
            
        except Exception as e:
            logger.error(f"Error getting images: {e}")
            return []

# Global instance
image_service = UnsplashImageService()
