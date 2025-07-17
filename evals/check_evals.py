#!/usr/bin/env python3
"""
Check and validate all eval files before running.
"""

import os
import sys
import importlib.util
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_file(filepath):
    """Check if a Python file can be imported successfully."""
    try:
        spec = importlib.util.spec_from_file_location("module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    """Check all eval files."""
    print("🔍 Checking Eval Files")
    print("=" * 40)
    
    # Check environment first
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ Environment loaded - API key found")
    else:
        print("❌ OPENAI_API_KEY not found in environment")
        print("💡 Make sure your .env file contains OPENAI_API_KEY")
    
    eval_files = [
        "test_simple.py",
        "rag_quality_eval.py",
        "search_relevance_eval.py", 
        "embedding_quality_eval.py",
        "model_comparison_eval.py",
        "run_all_evals.py"
    ]
    
    # Add parent directory to path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    results = {}
    
    print(f"\nChecking {len(eval_files)} eval files:")
    print("-" * 40)
    
    for filename in eval_files:
        filepath = os.path.join("evals", filename)
        if os.path.exists(filepath):
            success, error = check_file(filepath)
            results[filename] = (success, error)
            status = "✅" if success else "❌"
            print(f"{status} {filename}")
            if error:
                print(f"   Error: {error[:100]}...")
        else:
            results[filename] = (False, "File not found")
            print(f"❌ {filename} - File not found")
    
    print("\n" + "=" * 40)
    
    success_count = sum(1 for success, _ in results.values() if success)
    total_count = len(results)
    
    print(f"📊 Summary: {success_count}/{total_count} files passed checks")
    
    if success_count == total_count:
        print("🎉 All eval files are ready to run!")
        print("\nNext steps:")
        print("  python evals/run_all_evals.py")
    else:
        print("🔧 Some files need fixing before running evals")
        
        # Show failed files
        failed = [name for name, (success, _) in results.items() if not success]
        print(f"\nFailed files: {', '.join(failed)}")

if __name__ == "__main__":
    main()