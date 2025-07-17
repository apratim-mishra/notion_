#!/usr/bin/env python3
"""
Comprehensive evaluation suite for Notion Semantic Search system.
Run with: python evals/run_all_evals.py
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import eval modules
try:
    from evals.rag_quality_eval import run_rag_quality_eval
    from evals.search_relevance_eval import run_search_relevance_eval
    from evals.embedding_quality_eval import run_embedding_quality_eval
    from evals.model_comparison_eval import run_model_comparison_eval
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI()

def poll_and_save_results(eval_id: str, run_ids: List[str], eval_name: str):
    """Poll for completion and save results."""
    if not run_ids:
        print(f"⚠️  No runs to poll for {eval_name}")
        return
    
    print(f"🔄 Polling {eval_name} evaluation...")
    
    while True:
        runs = [client.evals.runs.retrieve(rid, eval_id=eval_id) for rid in run_ids]
        
        for run in runs:
            print(f"  {run.id}: {run.status} - {run.result_counts}")
            
        if all(run.status in {"completed", "failed"} for run in runs):
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create results directory
            results_dir = "evals/results"
            os.makedirs(results_dir, exist_ok=True)
            
            for run in runs:
                try:
                    output = client.evals.runs.output_items.list(
                        run_id=run.id, eval_id=eval_id
                    )
                    
                    filename = f"{results_dir}/{eval_name}_{run.name}_{timestamp}.json"
                    
                    with open(filename, "w") as f:
                        f.write(output.model_dump_json(indent=2))
                        
                    print(f"✅ Saved results to {filename}")
                except Exception as e:
                    print(f"❌ Error saving results for {run.id}: {e}")
            break
            
        time.sleep(10)

def main():
    """Run comprehensive evaluation suite."""
    print("🚀 Starting Notion Semantic Search Evaluation Suite")
    print("=" * 60)
    
    # Check environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Please set your API key in .env file.")
        return
    
    print(f"✅ Environment loaded - API key found")
    
    # List of evaluations to run
    evaluations = [
        ("RAG_Quality", run_rag_quality_eval),
        ("Search_Relevance", run_search_relevance_eval), 
        ("Embedding_Quality", run_embedding_quality_eval),
        ("Model_Comparison", run_model_comparison_eval)
    ]
    
    print(f"📊 Found {len(evaluations)} evaluation suites to run:")
    for i, (name, _) in enumerate(evaluations, 1):
        print(f"  {i}. {name.replace('_', ' ')}")
    
    print("\n" + "=" * 60)
    
    # Run evaluations
    for eval_name, eval_func in evaluations:
        print(f"\n🔬 Running {eval_name.replace('_', ' ')} evaluation...")
        try:
            result = eval_func()
            if isinstance(result, tuple) and len(result) == 2:
                eval_id, run_ids = result
                if eval_id:
                    poll_and_save_results(eval_id, run_ids, eval_name.lower())
                else:
                    print(f"❌ Failed to create {eval_name} evaluation")
            else:
                print(f"✅ {eval_name} completed (no polling needed)")
        except Exception as e:
            print(f"❌ Error in {eval_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Evaluation suite completed!")
    print("📁 Results saved in ./evals/results/ directory")

if __name__ == "__main__":
    main() 