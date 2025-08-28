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
        
    def extract_keywords_for_images(self, text: str, query: str) -> List[str]:
        """Extract relevant keywords for image search - ONLY Sivas related"""
        
        # Always start with Sivas as base
        keywords = []
        
        # Extract specific terms from query
        query_lower = query.lower()
        
        if "castle" in query_lower or "fortress" in query_lower or "kale" in query_lower:
            keywords.extend([
                "sivas castle turkey",
                "sivas kale",
                "sivas fortress"
            ])
        elif "food" in query_lower or "cuisine" in query_lower or "eat" in query_lower:
            keywords.extend([
                "sivas food turkey",
                "sivas cuisine",
                "sivas traditional food"
            ])
        elif "mosque" in query_lower or "cami" in query_lower or "religion" in query_lower:
            keywords.extend([
                "sivas mosque turkey",
                "sivas ulu cami",
                "sivas buruciye medrese"
            ])
        elif "museum" in query_lower or "history" in query_lower:
            keywords.extend([
                "sivas museum turkey",
                "sivas archaeological museum",
                "sivas history"
            ])
        elif "architecture" in query_lower or "building" in query_lower:
            keywords.extend([
                "sivas architecture turkey",
                "sivas buildings",
                "sivas historical architecture"
            ])
        elif "medrese" in query_lower or "madrasa" in query_lower:
            keywords.extend([
                "sivas medrese turkey",
                "cifte minareli medrese sivas",
                "sivas twin minaret"
            ])
        else:
            # General Sivas terms
            keywords.extend([
                "sivas city turkey",
                "sivas turkey center",
                "sivas anatolia"
            ])
            
        # Ensure we always have at least basic Sivas search
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
