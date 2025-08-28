from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import asyncio
from claude_service import SivasAdvisorService
from config import API_HOST, API_PORT

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

# Mount static files (we'll create this directory)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Directory doesn't exist yet, will be created
    pass

# Initialize the advisor service
advisor_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global advisor_service
    try:
        logger.info("Initializing Sivas Advisor Service...")
        advisor_service = SivasAdvisorService()
        logger.info("Service initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize advisor service: {e}")
        raise

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    language: Optional[str] = "ru"

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Dict]
    context_used: bool

class SuggestionsResponse(BaseModel):
    suggestions: List[str]

# API Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with chat interface"""
    suggestions = advisor_service.get_suggestions() if advisor_service else []
    return templates.TemplateResponse("index.html", {
        "request": request,
        "suggestions": suggestions
    })

@app.post("/api/ask", response_model=QueryResponse)
async def ask_question(query_request: QueryRequest):
    """Ask a question about Sivas"""
    if not advisor_service:
        raise HTTPException(status_code=503, detail="Advisor service not available")
    
    if not query_request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Get advice from the service
        result = advisor_service.get_advice(query_request.query)
        
        return QueryResponse(
            query=result['query'],
            response=result['response'],
            sources=result['sources'],
            context_used=result['context_used']
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/suggestions", response_model=SuggestionsResponse)
async def get_suggestions():
    """Get sample questions"""
    if not advisor_service:
        raise HTTPException(status_code=503, detail="Advisor service not available")
    
    suggestions = advisor_service.get_suggestions()
    return SuggestionsResponse(suggestions=suggestions)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service_available": advisor_service is not None
    }

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle internal server errors"""
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
