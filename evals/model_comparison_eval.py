#!/usr/bin/env python3
"""
Simple test to verify eval system works.
"""

import os
import sys
import json
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import NotionSemanticSearch
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

client = OpenAI()

def create_model_comparison_dataset():
    """Create dataset for comparing different models based on your content."""
    return [
        {
            "query": "How does machine learning work in Instagram's recommendation systems?",
            "complexity": "high",
            "expected_length": "comprehensive"
        },
        {
            "query": "What are neural networks?",
            "complexity": "medium", 
            "expected_length": "concise"
        },
        {
            "query": "Explain content moderation using ML",
            "complexity": "medium",
            "expected_length": "detailed"
        },
        {
            "query": "What is causal inference in notifications?",
            "complexity": "high",
            "expected_length": "comprehensive"
        }
    ]

model_comparison_grader = """
You are evaluating the quality of AI-generated responses for different language models.

Evaluate the response based on:
1. **Accuracy (30%)**: Is the information factually correct?
2. **Completeness (25%)**: Does it address all aspects of the question?
3. **Clarity (25%)**: Is it well-structured and understandable?
4. **Efficiency (20%)**: Is the response appropriately concise/detailed for the question?

Return JSON with scores 1-7:
{
  "accuracy_score": float,
  "completeness_score": float,
  "clarity_score": float,
  "efficiency_score": float,
  "overall_score": float,
  "reasoning": "detailed explanation"
}
"""

def run_model_comparison_eval():
    """Compare different models for RAG generation."""
    try:
        print("🤖 Creating Model Comparison Evaluation...")
        
        model_comparison_eval = client.evals.create(
            name="RAG Model Comparison",
            data_source_config={
                "type": "custom",
                "item_schema": {
                    "type": "object", 
                    "properties": {
                        "query": {"type": "string"},
                        "complexity": {"type": "string"},
                        "expected_length": {"type": "string"}
                    }
                },
                "include_sample_schema": True  # THIS WAS MISSING!
            },
            testing_criteria=[
                {
                    "type": "score_model",
                    "name": "Response Quality Grader",
                    "model": "o3-mini",
                    "input": [
                        {"role": "system", "content": model_comparison_grader},
                        {"role": "user", "content": """
Query: {{item.query}}
Complexity: {{item.complexity}}
Expected Length: {{item.expected_length}}

Response to evaluate: {{sample.output_text}}
                        """}
                    ],
                    "range": [1, 7],
                    "pass_threshold": 5.0
                }
            ]
        )
        
        print(f"✅ Model comparison eval created: {model_comparison_eval.id}")
        
        models_to_test = ["gpt-4.1", "gpt-4.1-mini", "gpt-4o-mini"]
        run_ids = []
        
        for model in models_to_test:
            try:
                print(f"🚀 Creating run for {model}...")
                
                run = client.evals.runs.create(
                    name=f"RAG_with_{model.replace('.', '_').replace('-', '_')}",
                    eval_id=model_comparison_eval.id,
                    data_source={
                        "type": "completions",
                        "source": {
                            "type": "file_content",
                            "content": [{"item": item} for item in create_model_comparison_dataset()]
                        },
                        "input_messages": {
                            "type": "template",
                            "template": [
                                {
                                    "type": "message",
                                    "role": "user", 
                                    "content": {
                                        "type": "input_text",
                                        "text": "Answer this question using RAG: {{item.query}}"
                                    }
                                }
                            ]
                        },
                        "model": model,
                        "sampling_params": {
                            "temperature": 0.2,
                            "max_completions_tokens": 4096
                        }
                    }
                )
                run_ids.append(run.id)
                print(f"✅ Created run for {model}: {run.id}")
                
            except Exception as e:
                print(f"❌ Error creating run for {model}: {e}")
        
        return model_comparison_eval.id, run_ids
        
    except Exception as e:
        print(f"Error creating model comparison eval: {e}")
        return None, []

if __name__ == "__main__":
    print("🤖 Running Model Comparison Evaluation...")
    eval_id, run_ids = run_model_comparison_eval()
    if eval_id:
        print(f"✅ Model comparison eval created: {eval_id}")
        print(f"📊 Created {len(run_ids)} runs")
    else:
        print("❌ Failed to create model comparison eval") 