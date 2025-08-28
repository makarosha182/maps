#!/usr/bin/env python3
"""
Simple demo server without Claude API
Uses only vector search for demonstration
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import logging
from vector_store import SivasVectorStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sivas Tourism Advisor Demo",
    description="Demo version using vector search only",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    logger.warning("Static files directory not found")

# Global vector store instance
vector_store = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Dict]
    context_used: bool

@app.on_event("startup")
async def startup_event():
    global vector_store
    logger.info("Initializing Vector Store...")
    vector_store = SivasVectorStore()
    logger.info("Vector Store initialized successfully!")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/ask", response_model=QueryResponse)
async def ask_question(query_request: QueryRequest):
    try:
        query = query_request.query
        logger.info(f"Processing query: {query}")
        
        # Search for relevant content
        search_results = vector_store.search(query, n_results=5)
        
        if not search_results:
            response = f"""
🤖 **Sivas Database Search**

Unfortunately, I couldn't find relevant information for your query: "{query}"

Try rephrasing your question or ask about:
• Sivas attractions
• Traditional cuisine
• Historical sites
• Tourist activities
• Cultural features
            """.strip()
            
            return QueryResponse(
                query=query,
                response=response,
                sources=[],
                context_used=False
            )
        
        # Format response from search results
        response_parts = [f"🏛️ **Found Information about Sivas:**\n"]
        
        sources = []
        for i, result in enumerate(search_results[:3], 1):
            metadata = result.get('metadata', {})
            title = metadata.get('title', 'Untitled')
            category = metadata.get('category', 'general')
            text = result.get('text', '')
            url = metadata.get('url', '')
            
            # Clean up text
            if len(text) > 300:
                text = text[:300] + "..."
            
            response_parts.append(f"**{i}. {title}** ({category})")
            response_parts.append(f"{text}\n")
            
            sources.append({
                'title': title,
                'url': url,
                'category': category
            })
        
        response_parts.append("---")
        response_parts.append("💡 *These are vector search results from Sivas website content*")
        response_parts.append("🔧 *For complete answers, a valid Claude API key is needed*")
        
        response = "\n\n".join(response_parts)
        
        return QueryResponse(
            query=query,
            response=response,
            sources=[],  # No sources shown
            context_used=True
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suggestions")
async def get_suggestions():
    return {
        "suggestions": [
            "What are the main attractions in Sivas?",
            "What to see in Sivas in 48 hours?",
            "Tell me about the history of Sivas",
            "What activities are available for tourists?",
            "What local cuisine should I try?",
            "What museums are there in Sivas?",
            "Where can I listen to traditional music?",
            "What crafts are popular in Sivas?"
        ]
    }

@app.get("/api/stats")
async def get_stats():
    stats = vector_store.get_collection_stats()
    return {
        "total_chunks": stats['total_chunks'],
        "collection_name": stats['collection_name'],
        "status": "Vector search active - Claude API disabled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
