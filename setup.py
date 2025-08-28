#!/usr/bin/env python3
"""
Setup script for Sivas Tourism Advisor
This script handles the complete setup process
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"\n{'='*50}")
    print(f"📋 {description if description else command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_environment():
    """Set up the Python environment and install dependencies"""
    print("🔧 Setting up Python environment...")
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("📦 Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            return False
        
        print("🔗 Please activate the virtual environment and run setup again:")
        print("   source venv/bin/activate  # On Linux/Mac")
        print("   venv\\Scripts\\activate     # On Windows")
        print("   python setup.py")
        return False
    
    # Install dependencies
    print("📦 Installing Python dependencies...")
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def setup_environment_file():
    """Create .env file from example"""
    env_file = Path(".env")
    example_file = Path("env_example.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if example_file.exists():
        print("📝 Creating .env file from example...")
        with open(example_file, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("⚠️  Please edit .env file and add your Claude API key!")
        return True
    
    print("❌ env_example.txt not found")
    return False

def run_scraper():
    """Run the web scraper"""
    print("🕷️  Running web scraper...")
    return run_command("python scraper.py", "Scraping Sivas tourism website")

def setup_vector_store():
    """Initialize the vector store"""
    print("🗃️  Setting up vector database...")
    return run_command("python vector_store.py", "Creating vector database")

def test_service():
    """Test the Claude service"""
    print("🤖 Testing Claude API service...")
    return run_command("python claude_service.py", "Testing Claude integration")

def main():
    """Main setup process"""
    print("🏛️  Sivas Tourism Advisor - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Failed to set up environment")
        sys.exit(1)
    
    # Setup environment file
    if not setup_environment_file():
        print("❌ Failed to set up environment file")
        sys.exit(1)
    
    # Check if Claude API key is set
    try:
        from dotenv import load_dotenv
        load_dotenv()
        claude_key = os.getenv("CLAUDE_API_KEY")
        if not claude_key or claude_key == "your_claude_api_key_here":
            print("⚠️  Please set your Claude API key in .env file before proceeding!")
            print("   Edit .env and set CLAUDE_API_KEY=your_actual_api_key")
            print("   Then run: python setup.py --skip-env")
            sys.exit(1)
    except ImportError:
        print("⚠️  Dependencies not installed properly")
        sys.exit(1)
    
    # Run scraper
    print("\n🚀 Starting data collection and setup...")
    if "--skip-scraping" not in sys.argv:
        if not run_scraper():
            print("❌ Scraping failed - you can run 'python scraper.py' manually later")
        
        # Setup vector store
        if not setup_vector_store():
            print("❌ Vector store setup failed")
            sys.exit(1)
    
    # Test service
    if not test_service():
        print("❌ Service test failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("\n📋 Next steps:")
    print("1. Start the service: python main.py")
    print("2. Open browser: http://localhost:8000")
    print("3. Ask questions about Sivas tourism!")
    print("\n🔧 Available commands:")
    print("   python scraper.py      - Re-run web scraping")
    print("   python vector_store.py - Rebuild vector database")
    print("   python claude_service.py - Test Claude service")
    print("   python main.py         - Start web service")

if __name__ == "__main__":
    # Handle command line arguments
    if "--skip-env" in sys.argv:
        # Skip environment setup, useful for subsequent runs
        run_scraper()
        setup_vector_store()
        test_service()
    else:
        main()
