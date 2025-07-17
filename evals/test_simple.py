#!/usr/bin/env python3
"""
Simple test to verify eval system works.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_functionality():
    """Test basic functionality without running full evals."""
    print("🧪 Testing Basic Eval Functionality")
    print("=" * 40)
    
    # Test 1: Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API key found (starts with: {api_key[:8]}...)")
    else:
        print("❌ OpenAI API key not found")
        print("💡 Make sure OPENAI_API_KEY is set in your .env file")
        return False
    
    # Test 2: Try importing main
    try:
        from main import NotionSemanticSearch
        print("✅ Main module import successful")
    except ImportError as e:
        print(f"❌ Main module import failed: {e}")
        return False
    
    # Test 3: Try initializing app
    try:
        app = NotionSemanticSearch()
        print("✅ NotionSemanticSearch initialization successful")
    except Exception as e:
        print(f"❌ App initialization failed: {e}")
        return False
    
    # Test 4: Try OpenAI client
    try:
        from openai import OpenAI
        client = OpenAI()
        print("✅ OpenAI client creation successful")
    except Exception as e:
        print(f"❌ OpenAI client failed: {e}")
        return False
    
    print("\n🎉 All basic tests passed!")
    print("Your system is ready for evaluation.")
    return True

if __name__ == "__main__":
    test_basic_functionality()