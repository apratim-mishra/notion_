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

def create_rag_quality_dataset():
    """Create evaluation dataset with ground truth Q&A pairs from your Notion content."""
    # Based on your actual ML content
    return [
        {
            "query": "What are the main machine learning algorithms discussed?",
            "expected_topics": ["neural networks", "decision trees", "clustering", "recommendation systems"],
            "expected_sources": ["ML design", "ml_design_video"]
        },
        {
            "query": "How does Instagram use machine learning for notifications?",
            "expected_topics": ["notification management", "causal inference", "click-through rate"],
            "expected_sources": ["ml_design_video", "ML design"]
        },
        {
            "query": "What is content moderation in machine learning?",
            "expected_topics": ["LLMs", "content moderation", "deep learning workflows"],
            "expected_sources": ["ML design", "ml_design_video"]
        },
        {
            "query": "How do recommendation systems work?",
            "expected_topics": ["ranking models", "personalized ads", "recommendation algorithms"],
            "expected_sources": ["ML design", "ml_design_video"]
        }
    ]

rag_grader_prompt = """
You are an expert evaluator of RAG (Retrieval-Augmented Generation) systems.
Evaluate the quality of the generated answer based on:

1. **Factual Accuracy (40%)**: Is the information correct based on the provided sources?
2. **Completeness (25%)**: Does it address all aspects of the question?
3. **Source Utilization (20%)**: How well does it use the retrieved sources?
4. **Clarity (15%)**: Is the answer well-structured and understandable?

Return a JSON object with your evaluation:
{
  "accuracy_score": float,
  "completeness_score": float, 
  "source_utilization_score": float,
  "clarity_score": float,
  "overall_score": float,
  "reasoning": "detailed explanation"
}

Score range: 1-7 (7 = excellent, 1 = poor)
"""

def run_rag_quality_eval():
    """Run RAG quality evaluation."""
    try:
        print("🤖 Creating RAG Quality Evaluation...")
        
        # Create eval
        rag_eval = client.evals.create(
            name="Notion RAG Quality Evaluation",
            data_source_config={
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "expected_topics": {"type": "array"},
                        "expected_sources": {"type": "array"}
                    }
                },
                "include_sample_schema": True
            },
            testing_criteria=[
                {
                    "type": "score_model",
                    "name": "RAG Quality Grader",
                    "model": "o3-mini",
                    "input": [
                        {"role": "system", "content": rag_grader_prompt},
                        {"role": "user", "content": """
Query: {{item.query}}
Expected Topics: {{item.expected_topics}}
Expected Sources: {{item.expected_sources}}

Generated Answer: {{sample.output_json.answer}}
Retrieved Sources: {{sample.output_json.pages}}
Chunks Used: {{sample.output_json.chunks_used}}
Average Relevance: {{sample.output_json.average_relevance}}
                        """}
                    ],
                    "range": [1, 7],
                    "pass_threshold": 5.0
                }
            ]
        )
        
        print(f"✅ RAG eval created: {rag_eval.id}")
        
        # Test different RAG configurations
        configs = [
            {"name": "Standard_RAG", "type": "standard"},
            {"name": "Long_form_RAG", "type": "long"},
            {"name": "Concise_RAG", "type": "concise"}
        ]
        
        run_ids = []
        
        for config in configs:
            print(f"🚀 Creating run for {config['name']}...")
            
            try:
                run = client.evals.runs.create(
                    name=config["name"],
                    eval_id=rag_eval.id,
                    data_source={
                        "type": "completions",
                        "source": {
                            "type": "file_content",
                            "content": [{"item": item} for item in create_rag_quality_dataset()]
                        },
                        "input_messages": {
                            "type": "template", 
                            "template": [
                                {
                                    "type": "message",
                                    "role": "user",
                                    "content": {
                                        "type": "input_text",
                                        "text": "Generate RAG response for: {{item.query}}"
                                    }
                                }
                            ]
                        },
                        "model": "gpt-4.1-mini",
                        "sampling_params": {
                            "temperature": 0.2,
                            "max_completions_tokens": 8192 if config["type"] == "long" else 4096,
                            "response_format": {
                                "type": "json_schema",
                                "json_schema": {
                                    "name": "rag_response",
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "answer": {"type": "string"},
                                            "pages": {"type": "array"},
                                            "chunks_used": {"type": "integer"},
                                            "average_relevance": {"type": "number"}
                                        },
                                        "required": ["answer", "pages", "chunks_used"],
                                        "additionalProperties": False
                                    }
                                }
                            }
                        }
                    }
                )
                run_ids.append(run.id)
                print(f"✅ Created run: {run.id}")
                
            except Exception as e:
                print(f"❌ Error creating run for {config['name']}: {e}")
        
        return rag_eval.id, run_ids
        
    except Exception as e:
        print(f"Error creating RAG quality eval: {e}")
        return None, []

if __name__ == "__main__":
    print("🔬 Running RAG Quality Evaluation...")
    eval_id, run_ids = run_rag_quality_eval()
    if eval_id:
        print(f"✅ RAG quality eval created: {eval_id}")
        print(f"📊 Created {len(run_ids)} runs")
    else:
        print("❌ Failed to create RAG quality eval") 