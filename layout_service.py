import logging
from typing import List, Dict, Optional, Set
import json
import re

logger = logging.getLogger(__name__)

class GenerativeLayoutService:
    """Service for generating dynamic layouts with Claude-controlled image placement"""
    
    def __init__(self, image_service):
        self.image_service = image_service
        self.used_image_urls: Set[str] = set()
        
    def create_layout_prompt(self, user_query: str) -> str:
        """Create a prompt for Claude to generate structured layout response"""
        
        prompt = f"""You are a tourism expert for Sivas, Turkey. Your task is to create a structured response with BOTH content and layout instructions.

USER QUESTION: {user_query}

RESPOND WITH A JSON structure containing:
1. "content" - your informative answer about Sivas
2. "layout" - array of layout elements

LAYOUT ELEMENT TYPES:
- "text": Regular text content with unique ID
- "image": Image request with search query and placement

EXAMPLE RESPONSE FORMAT:
{{
  "content": "Here are the famous dishes of Sivas...",
  "layout": [
    {{
      "type": "text",
      "content": "1. Sivas Köftesi - Traditional meatballs made with bulgur and spices",
      "id": "dish_1"
    }},
    {{
      "type": "image", 
      "search_query": "sivas köftesi turkish meatballs",
      "fallback_query": "turkish köfte meatballs",
      "position": "after",
      "target_id": "dish_1",
      "description": "Traditional Sivas köftesi served on a plate"
    }},
    {{
      "type": "text",
      "content": "2. Madımak - Wild herb specialty unique to Sivas region",
      "id": "dish_2"
    }},
    {{
      "type": "image",
      "search_query": "madımak herb dish sivas turkey",
      "fallback_query": "turkish herb salad greens",
      "position": "after",
      "target_id": "dish_2",
      "description": "Fresh madımak herb dish"
    }}
  ]
}}

RULES:
1. Always provide JSON format
2. Decide if images are needed (not every response needs images)
3. Use specific search queries for Sivas content
4. Provide fallback queries for broader search if Sivas-specific content not found
5. Give each text element a unique ID
6. Images should enhance understanding, not distract

For this query about Sivas, create an appropriate structured response:"""

        return prompt
    
    def parse_claude_layout_response(self, claude_response: str) -> Dict:
        """Parse Claude's JSON layout response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', claude_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                layout_data = json.loads(json_str)
                return layout_data
            else:
                # Fallback: treat as regular text response
                return {
                    "content": claude_response,
                    "layout": [
                        {
                            "type": "text",
                            "content": claude_response,
                            "id": "main_content"
                        }
                    ]
                }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude layout response: {e}")
            # Fallback to simple text layout
            return {
                "content": claude_response,
                "layout": [
                    {
                        "type": "text", 
                        "content": claude_response,
                        "id": "main_content"
                    }
                ]
            }
    
    def find_unique_image(self, search_query: str, fallback_query: str = None) -> Optional[Dict]:
        """Find a unique image that hasn't been used yet"""
        
        # Try primary search query
        logger.info(f"Searching for unique image: '{search_query}'")
        images = self.image_service.search_images([search_query], limit=5)
        
        # Filter out used images
        unique_images = [img for img in images if img.get('url') not in self.used_image_urls]
        
        if unique_images:
            selected_image = unique_images[0]
            self.used_image_urls.add(selected_image['url'])
            logger.info(f"Found unique image with primary query")
            return selected_image
        
        # Try fallback query if no unique images found
        if fallback_query:
            logger.info(f"Primary search exhausted, trying fallback: '{fallback_query}'")
            fallback_images = self.image_service.search_images([fallback_query], limit=5)
            unique_fallback = [img for img in fallback_images if img.get('url') not in self.used_image_urls]
            
            if unique_fallback:
                selected_image = unique_fallback[0]
                self.used_image_urls.add(selected_image['url'])
                logger.info(f"Found unique image with fallback query")
                return selected_image
        
        logger.warning(f"No unique images found for queries: '{search_query}', '{fallback_query}'")
        return None
    
    def process_layout(self, layout_data: Dict) -> Dict:
        """Process the layout by fetching images and building final structure"""
        processed_layout = []
        
        for element in layout_data.get('layout', []):
            if element['type'] == 'text':
                # Text elements pass through unchanged
                processed_layout.append(element)
                
            elif element['type'] == 'image':
                # Process image elements
                search_query = element.get('search_query', '')
                fallback_query = element.get('fallback_query', '')
                
                image_data = self.find_unique_image(search_query, fallback_query)
                
                if image_data:
                    # Add layout positioning info to image
                    image_element = {
                        'type': 'image',
                        'position': element.get('position', 'after'),
                        'target_id': element.get('target_id', ''),
                        'description': element.get('description', ''),
                        'image_data': image_data,
                        'search_query': search_query
                    }
                    processed_layout.append(image_element)
                else:
                    # Skip image if no unique image found
                    logger.warning(f"Skipping image element - no unique image available")
        
        return {
            'content': layout_data.get('content', ''),
            'layout': processed_layout
        }
    
    def reset_used_images(self):
        """Reset the used images set for a new conversation"""
        self.used_image_urls.clear()
        logger.info("Reset used images set")
    
    def generate_response_with_layout(self, user_query: str, claude_client) -> Dict:
        """Main method to generate response with dynamic layout"""
        try:
            # Create layout-aware prompt
            layout_prompt = self.create_layout_prompt(user_query)
            
            # Get structured response from Claude
            message = claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": layout_prompt
                    }
                ]
            )
            
            claude_response = message.content[0].text
            logger.info(f"Claude layout response received: {len(claude_response)} chars")
            
            # Parse the structured response
            layout_data = self.parse_claude_layout_response(claude_response)
            
            # Process layout and fetch images
            processed_response = self.process_layout(layout_data)
            
            logger.info(f"Generated layout with {len(processed_response['layout'])} elements")
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating layout response: {e}")
            return {
                'content': f'Sorry, I encountered an error while preparing your response about Sivas. Please try again.',
                'layout': [
                    {
                        'type': 'text',
                        'content': 'Sorry, I encountered an error while preparing your response about Sivas. Please try again.',
                        'id': 'error_message'
                    }
                ]
            }

# Global instance will be created in main.py
layout_service = None
