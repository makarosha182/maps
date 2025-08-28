import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY environment variable is required")

# Website Configuration
BASE_URL = "https://sivas.goturkiye.com"
SCRAPED_DATA_DIR = "scraped_data"
VECTOR_DB_DIR = "vector_db"

# Scraping Configuration
MAX_PAGES = 100
DELAY_BETWEEN_REQUESTS = 1.0
REQUEST_TIMEOUT = 30

# Vector Database Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# API Configuration
API_HOST = "localhost"
API_PORT = 8000
