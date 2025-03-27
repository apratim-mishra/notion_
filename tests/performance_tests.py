import time
import unittest
from embeddings import EmbeddingGenerator
from search import NotionSearch
from vector_store import VectorStore
from rag import RAGProcessor

class PerformanceTests(unittest.TestCase):
    def test_embedding_generation_performance(self):
        """Test that embedding generation meets latency requirements."""
        embedding_generator = EmbeddingGenerator()
        
        test_text = "This is a test document for embedding generation performance."
        
        # Warm-up
        _ = embedding_generator.generate_embeddings([
            {"id": "test-0", "title": "Test", "chunk": test_text}
        ])
        
        # Actual test
        start_time = time.time()
        _ = embedding_generator.generate_embeddings([
            {"id": "test-1", "title": "Test", "chunk": test_text}
        ])
        end_time = time.time()
        
        latency = end_time - start_time
        
        # Ensure latency is below threshold (adjust based on your requirements)
        self.assertLess(latency, 2.0, f"Embedding generation took {latency:.2f}s, which exceeds the threshold")
    
    def test_search_performance(self):
        """Test that search meets latency requirements."""
        # This test requires a working Qdrant instance with data
        # You might want to mock this in CI or have a test database
        search_client = NotionSearch()
        
        # Warm-up
        _ = search_client.search("warm up query")
        
        # Actual test
        start_time = time.time()
        results = search_client.search("test query for performance")
        end_time = time.time()
        
        latency = end_time - start_time
        
        # Ensure latency is below threshold
        self.assertLess(latency, 1.0, f"Search took {latency:.2f}s, which exceeds the threshold")

if __name__ == '__main__':
    unittest.main() 