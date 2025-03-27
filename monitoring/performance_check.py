import json
import time
import datetime
import os
from prometheus_client import Gauge, CollectorRegistry, push_to_gateway
from notion_connector import NotionConnector
from search import NotionSearch
from rag import RAGProcessor

# Configure Prometheus metrics
registry = CollectorRegistry()
search_latency = Gauge('notion_search_latency_seconds', 
                       'Latency of notion search queries', 
                       ['query_type'], registry=registry)
rag_latency = Gauge('notion_rag_latency_seconds', 
                   'Latency of RAG generation', 
                   ['query_type'], registry=registry)
search_score = Gauge('notion_search_score', 
                    'Average relevance score of search results', 
                    ['query_type'], registry=registry)

# Test queries
TEST_QUERIES = [
    {"query": "what are best ranking models", "type": "ranking_models"},
    {"query": "explain neural networks", "type": "neural_networks"},
    {"query": "how does Target AI work", "type": "target_ai"}
]

def run_search_tests():
    """Run tests on the search functionality and collect metrics."""
    search_client = NotionSearch()
    
    for test in TEST_QUERIES:
        query = test["query"]
        query_type = test["type"]
        
        # Measure search latency
        start_time = time.time()
        results = search_client.search(query, limit=5)
        end_time = time.time()
        
        latency = end_time - start_time
        search_latency.labels(query_type=query_type).set(latency)
        
        # Calculate average score
        if results:
            avg_score = sum(result["score"] for result in results) / len(results)
            search_score.labels(query_type=query_type).set(avg_score)
        
        # Save results for analysis
        with open(f"logs/search_results_{query_type}_{datetime.datetime.now().strftime('%Y%m%d')}.json", "w") as f:
            json.dump(results, f)

def run_rag_tests():
    """Run tests on the RAG functionality and collect metrics."""
    rag_processor = RAGProcessor()
    
    for test in TEST_QUERIES:
        query = test["query"]
        query_type = test["type"]
        
        # Measure RAG latency
        start_time = time.time()
        result = rag_processor.generate_response(query)
        end_time = time.time()
        
        latency = end_time - start_time
        rag_latency.labels(query_type=query_type).set(latency)
        
        # Save results for analysis
        with open(f"logs/rag_results_{query_type}_{datetime.datetime.now().strftime('%Y%m%d')}.json", "w") as f:
            json.dump(result, f)

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run tests and collect metrics
    run_search_tests()
    run_rag_tests()
    
    # Push metrics to Prometheus if configured
    prometheus_gateway = os.getenv("PROMETHEUS_GATEWAY")
    if prometheus_gateway:
        push_to_gateway(prometheus_gateway, job='notion_search_monitoring', registry=registry) 