import anthropic
from typing import List, Dict, Optional
import logging
from vector_store import SivasVectorStore
from config import CLAUDE_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SivasAdvisorService:
    def __init__(self):
        self.claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        self.vector_store = SivasVectorStore()
        
        # System prompt for the Sivas advisor
        self.system_prompt = """You are an expert tourism consultant and local guide for the city of Sivas, Turkey.

        Your goal is to provide helpful, informative, and friendly answers about Sivas to tourists and visitors. You should:

        - Answer questions naturally and comprehensively about Sivas
        - Include historical, cultural, and practical information
        - Provide specific details when possible (names, locations, recommendations)
        - Be conversational and welcoming
        - Help visitors plan their trips and understand the city
        - Share interesting facts and local insights
        - Give practical travel advice

        Topics you can discuss include:
        - Attractions and landmarks
        - History and culture
        - Local cuisine and restaurants
        - Hotels and accommodation
        - Transportation and getting around
        - Events and festivals
        - Shopping and crafts
        - Local government and officials
        - Demographics and statistics
        - Nearby areas and day trips

        Always be helpful and informative, drawing from your knowledge about Sivas to give the best possible answer."""
    
    def search_relevant_content(self, query: str, n_results: int = 8) -> List[Dict]:
        """Search for relevant content using vector store"""
        try:
            # Detect query type to help with filtering
            query_lower = query.lower()
            page_type = None
            
            if any(keyword in query_lower for keyword in ['restaurant', 'food', 'cuisine', 'eat', 'taste', 'dining']):
                page_type = 'food'
            elif any(keyword in query_lower for keyword in ['hotel', 'accommodation', 'stay', 'lodging', 'where to sleep']):
                page_type = 'accommodation'
            elif any(keyword in query_lower for keyword in ['museum', 'history', 'attraction', 'see', 'visit', 'historic']):
                page_type = 'historical'
            elif any(keyword in query_lower for keyword in ['activity', 'activities', 'entertainment', 'things to do', 'what to do']):
                page_type = 'activity'
            elif any(keyword in query_lower for keyword in ['nature', 'park', 'landscape', 'outdoor', 'natural']):
                page_type = 'nature'
            elif any(keyword in query_lower for keyword in ['culture', 'music', 'festival', 'tradition', 'cultural']):
                page_type = 'culture'
            elif any(keyword in query_lower for keyword in ['route', 'travel', 'how to get', 'transportation', 'itinerary']):
                page_type = 'route'
            
            results = self.vector_store.search(query, n_results=n_results, page_type=page_type)
            return results
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    def format_context(self, search_results: List[Dict]) -> str:
        """Format search results into context for Claude"""
        if not search_results:
            return "Context information about Sivas not found."
        
        context_parts = []
        seen_urls = set()
        
        for result in search_results:
            metadata = result.get('metadata', {})
            url = metadata.get('url', '')
            
            # Avoid duplicate content from same URL
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            title = metadata.get('title', 'Untitled')
            page_type = metadata.get('page_type', 'general')
            text = result.get('text', '')
            
            context_part = f"""
=== {title} ({page_type}) ===
URL: {url}
Content: {text}
"""
            context_parts.append(context_part.strip())
        
        return "\n\n".join(context_parts)
    
    def generate_response(self, user_query: str, context: str) -> str:
        """Generate response using Claude API"""
        try:
            prompt = f"""Here's some context about Sivas from tourism materials:
{context}

Question: {user_query}

Please provide a helpful and informative answer about Sivas. You can use the context above if relevant, but feel free to draw from your general knowledge about Sivas to give a comprehensive answer. Be friendly and practical for tourists."""

            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.7,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, an error occurred while processing your request: {e}"
    
    def get_advice(self, user_query: str) -> Dict:
        """Main method to get advice about Sivas"""
        # Search for relevant content
        search_results = self.search_relevant_content(user_query)
        
        # Format context
        context = self.format_context(search_results)
        
        # Generate response
        response = self.generate_response(user_query, context)
        
        return {
            'query': user_query,
            'response': response,
            'sources': [],  # No sources shown to user
            'context_used': len(search_results) > 0
        }
    
    def get_suggestions(self) -> List[str]:
        """Get sample questions users can ask"""
        return [
            "What are the main attractions worth visiting in Sivas?",
            "Where can I try the best traditional cuisine in Sivas?",
            "What crafts and souvenirs can I buy in Sivas?",
            "Tell me about the history and architecture of Sivas",
            "What natural places can I visit around Sivas?",
            "Where to stay in Sivas? What accommodation options are available?",
            "What traditional festivals and events take place in Sivas?",
            "What's the best way to get to Sivas?",
            "What interesting things can I do in Sivas in 48 hours?",
            "Tell me about the culture and traditions of Sivas"
        ]

def main():
    """Test the advisor service"""
    advisor = SivasAdvisorService()
    
    # Test questions
    test_queries = [
        "What can I see in Sivas?",
        "What traditional dishes should I try?",
        "Tell me about the history of the city"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Question: {query}")
        print(f"{'='*50}")
        
        result = advisor.get_advice(query)
        print(f"Answer: {result['response']}")
        
        if result['sources']:
            print(f"\nSources:")
            for source in result['sources']:
                print(f"- {source['title']} ({source['page_type']})")

if __name__ == "__main__":
    main()
