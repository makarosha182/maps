from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import os
import anthropic

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sivas Tourism Advisor",
    description="AI-powered advisor service for Sivas, Turkey tourism information",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    pass

# Initialize Claude client
claude_client = None
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global claude_client
    try:
        if CLAUDE_API_KEY:
            claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            logger.info("Claude client initialized successfully!")
        else:
            logger.warning("CLAUDE_API_KEY not found")
    except Exception as e:
        logger.error(f"Failed to initialize Claude client: {e}")

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "en"

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Dict]
    context_used: bool

class SuggestionsResponse(BaseModel):
    suggestions: List[str]

def get_sample_suggestions():
    """Get sample questions"""
    return [
        "What are the main attractions in Sivas?",
        "Tell me about Sivas history",
        "What is the best time to visit Sivas?",
        "What are traditional foods in Sivas?",
        "How to get to Sivas?"
    ]

def get_claude_response(query: str) -> str:
    """Get response from Claude"""
    if not claude_client:
        return "Sorry, the AI service is not available at the moment."
    
    try:
        system_prompt = """You are an expert tourism consultant and local guide for the city of Sivas, Turkey.
Your goal is to provide helpful, informative, and friendly answers about Sivas to tourists and visitors. You should:

- Answer questions naturally and comprehensively about Sivas
- Include historical, cultural, and practical information
- Provide specific details when possible (names, locations, recommendations)
- Be enthusiastic and welcoming about Sivas tourism
- If you don't know specific current information, be honest about it

Topics you can discuss include:
- Tourist attractions and landmarks
- Historical sites and museums
- Local cuisine and restaurants
- Cultural events and festivals
- Transportation and accommodation
- Shopping and local crafts
- Weather and best times to visit
- Local customs and traditions
- Government and demographics
- Geography and nature

Always respond in a helpful, friendly, and informative manner."""

        message = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        
        return message.content[0].text
        
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return f"Sorry, I encountered an error while processing your question. Please try again later."

# API Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with chat interface"""
    suggestions = get_sample_suggestions()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "suggestions": suggestions
    })

@app.post("/api/ask", response_model=QueryResponse)
async def ask_question(query_request: QueryRequest):
    """Ask a question about Sivas"""
    if not query_request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        response = get_claude_response(query_request.query)
        
        return QueryResponse(
            query=query_request.query,
            response=response,
            sources=[],  # No sources in simple version
            context_used=False
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/suggestions", response_model=SuggestionsResponse)
async def get_suggestions():
    """Get sample questions"""
    suggestions = get_sample_suggestions()
    return SuggestionsResponse(suggestions=suggestions)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "claude_available": claude_client is not None
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
