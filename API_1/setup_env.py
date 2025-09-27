#!/usr/bin/env python3
"""
Setup script to verify OpenAI environment configuration.
"""

import os
from dotenv import load_dotenv

def check_openai_setup():
    """Check if OpenAI environment is properly configured."""
    
    print("🔧 OpenAI Environment Setup Check")
    print("=" * 40)
    
    # Load .env file
    load_dotenv()
    
    # Check required environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    use_openai = os.getenv("USE_OPENAI_EMBEDDINGS", "true")
    embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    print(f"📂 Loading .env file from: {os.path.abspath('.env')}")
    print(f"🗝️  OPENAI_API_KEY: {'✅ Set' if openai_api_key else '❌ Missing'}")
    print(f"🤖 USE_OPENAI_EMBEDDINGS: {use_openai}")
    print(f"📊 OPENAI_EMBEDDING_MODEL: {embedding_model}")
    
    if not openai_api_key:
        print("\n❌ OPENAI_API_KEY is missing!")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your-actual-api-key-here")
        return False
    
    if openai_api_key.startswith("sk-"):
        print("✅ API key format looks correct")
    else:
        print("⚠️  API key format seems unusual (should start with 'sk-')")
    
    # Test OpenAI import
    try:
        import openai
        print("✅ OpenAI package is installed")
        
        # Test client initialization
        client = openai.OpenAI(api_key=openai_api_key)
        print("✅ OpenAI client can be initialized")
        
    except ImportError:
        print("❌ OpenAI package not installed")
        print("Run: pip install openai")
        return False
    except Exception as e:
        print(f"⚠️  OpenAI client initialization issue: {e}")
    
    print("\n🎉 Environment setup looks good!")
    print(f"🚀 Ready to run: uvicorn app:app --host 0.0.0.0 --port 8001")
    return True

if __name__ == "__main__":
    check_openai_setup()
