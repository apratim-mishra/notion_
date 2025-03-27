import unittest
from unittest.mock import patch, MagicMock
from search import NotionSearch

class TestNotionSearch(unittest.TestCase):
    @patch('search.OpenAI')
    @patch('search.QdrantClient')
    def test_search_initialization(self, mock_qdrant, mock_openai):
        # Setup mocks
        mock_openai.return_value = MagicMock()
        mock_qdrant.return_value = MagicMock()
        
        # Test initialization
        search = NotionSearch()
        self.assertEqual(search.collection_name, "notion_chunks")
        self.assertEqual(search.embedding_model, "text-embedding-3-small")

if __name__ == '__main__':
    unittest.main() 