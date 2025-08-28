import chromadb
from chromadb.config import Settings
import json
import os
from typing import List, Dict, Optional
import logging
from sentence_transformers import SentenceTransformer
import re
from config import VECTOR_DB_DIR, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, SCRAPED_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SivasVectorStore:
    def __init__(self):
        self.db_path = VECTOR_DB_DIR
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="sivas_content",
            metadata={"description": "Sivas tourism website content"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,!?;:\-\(\)]+', '', text)
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks"""
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                last_period = text.rfind('.', max(start, end - 100), end)
                last_exclamation = text.rfind('!', max(start, end - 100), end)
                last_question = text.rfind('?', max(start, end - 100), end)
                
                sentence_end = max(last_period, last_exclamation, last_question)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def extract_document_chunks(self, page_data: Dict) -> List[Dict]:
        """Extract and chunk content from a page"""
        chunks = []
        url = page_data.get('url', '')
        title = page_data.get('title', '')
        description = page_data.get('description', '')
        content = page_data.get('content', '')
        headings = page_data.get('headings', [])
        
        # Combine title and description as main metadata
        main_text = f"{title}\n{description}\n{content}"
        main_text = self.clean_text(main_text)
        
        # Create chunks from main content
        text_chunks = self.chunk_text(main_text)
        
        for i, chunk in enumerate(text_chunks):
            if chunk.strip():
                chunk_data = {
                    'id': f"{url}#chunk_{i}",
                    'text': chunk,
                    'metadata': {
                        'url': url,
                        'title': title,
                        'description': description,
                        'chunk_index': i,
                        'page_type': self.classify_page_type(url, title),
                        'headings': ', '.join([h['text'] for h in headings[:3]]) if headings else ''  # Top 3 headings as string
                    }
                }
                chunks.append(chunk_data)
        
        # Create separate chunks for headings if they're substantial
        for i, heading in enumerate(headings):
            heading_text = self.clean_text(heading.get('text', ''))
            if len(heading_text) > 50:  # Only chunk substantial headings
                chunk_data = {
                    'id': f"{url}#heading_{i}",
                    'text': heading_text,
                    'metadata': {
                        'url': url,
                        'title': title,
                        'heading_level': heading.get('level', 'h1'),
                        'chunk_type': 'heading',
                        'page_type': self.classify_page_type(url, title)
                    }
                }
                chunks.append(chunk_data)
        
        return chunks
    
    def classify_page_type(self, url: str, title: str) -> str:
        """Classify page type based on URL and title"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if any(keyword in url_lower or keyword in title_lower for keyword in ['hotel', 'accommodation', 'stay']):
            return 'accommodation'
        elif any(keyword in url_lower or keyword in title_lower for keyword in ['restaurant', 'food', 'taste', 'cuisine']):
            return 'food'
        elif any(keyword in url_lower or keyword in title_lower for keyword in ['museum', 'historical', 'heritage', 'see']):
            return 'historical'
        elif any(keyword in url_lower or keyword in title_lower for keyword in ['activity', 'tour', 'touch', 'experience']):
            return 'activity'
        elif any(keyword in url_lower or keyword in title_lower for keyword in ['nature', 'park', 'outdoor', 'smell']):
            return 'nature'
        elif any(keyword in url_lower or keyword in title_lower for keyword in ['culture', 'music', 'festival', 'listen']):
            return 'culture'
        elif any(keyword in url_lower or keyword in title_lower for keyword in ['route', 'itinerary', 'travel']):
            return 'route'
        else:
            return 'general'
    
    def add_documents(self, documents: List[Dict]):
        """Add documents to the vector store"""
        all_chunks = []
        
        for doc in documents:
            if 'error' in doc:
                logger.warning(f"Skipping document with error: {doc['url']}")
                continue
            
            # Adapt our parsed data structure to the expected format
            chunks = self.extract_chunks_from_parsed_data(doc)
            all_chunks.extend(chunks)
        
        if not all_chunks:
            logger.warning("No chunks to add to vector store")
            return
        
        # Prepare data for ChromaDB
        ids = [chunk['id'] for chunk in all_chunks]
        documents = [chunk['text'] for chunk in all_chunks]
        metadatas = [chunk['metadata'] for chunk in all_chunks]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} chunks...")
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        logger.info("Adding documents to vector store...")
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        logger.info(f"Added {len(all_chunks)} chunks to vector store")
    
    def extract_chunks_from_parsed_data(self, page_data: Dict) -> List[Dict]:
        """Extract chunks from our parsed HTML data structure"""
        chunks = []
        url = page_data.get('url', '')
        title = page_data.get('title', '')
        content = page_data.get('content', '')
        headers = page_data.get('headers', [])
        category = page_data.get('category', 'general')
        
        # Combine title and content
        main_text = f"{title}\n{content}"
        main_text = self.clean_text(main_text)
        
        # Create chunks from main content
        text_chunks = self.chunk_text(main_text)
        
        for i, chunk in enumerate(text_chunks):
            if chunk.strip():
                chunk_data = {
                    'id': f"{page_data.get('filename', url)}#chunk_{i}",
                    'text': chunk,
                    'metadata': {
                        'url': url,
                        'title': title,
                        'category': category,
                        'chunk_index': i,
                        'filename': page_data.get('filename', ''),
                        'headers': ', '.join(headers[:3]) if headers else '',  # Convert list to string
                        'word_count': len(chunk.split())
                    }
                }
                chunks.append(chunk_data)
        
        return chunks
    
    def search(self, query: str, n_results: int = 10, page_type: Optional[str] = None) -> List[Dict]:
        """Search for relevant content"""
        # Build where clause for filtering
        where_clause = {}
        if page_type:
            where_clause['page_type'] = page_type
        
        # Perform search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                result = {
                    'id': results['ids'][0][i],
                    'text': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if results['distances'] else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            'total_chunks': count,
            'collection_name': self.collection.name
        }
    
    def load_from_scraped_data(self, filename: str = 'sivas_content.json'):
        """Load and index scraped data"""
        filepath = os.path.join(SCRAPED_DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            logger.error(f"Scraped data file not found: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        
        logger.info(f"Loading {len(scraped_data)} documents into vector store...")
        self.add_documents(scraped_data)

def main():
    """Initialize vector store with scraped data"""
    vector_store = SivasVectorStore()
    
    # Load scraped data
    vector_store.load_from_scraped_data()
    
    # Print stats
    stats = vector_store.get_collection_stats()
    logger.info(f"Vector store stats: {stats}")
    
    # Test search
    test_query = "What are the best restaurants in Sivas?"
    results = vector_store.search(test_query, n_results=3)
    
    logger.info(f"Test search results for '{test_query}':")
    for result in results:
        logger.info(f"- {result['metadata']['title']}: {result['text'][:100]}...")

if __name__ == "__main__":
    main()
