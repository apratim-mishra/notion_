from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name="notion_content", host="localhost", port=6333):
        """Initialize the vector store with Qdrant."""
        self.collection_name = collection_name
        self.dimension = 1536  # Dimension of text-embedding-ada-002
        
        try:
            self.client = QdrantClient(host=host, port=port)
            logger.info(f"Connected to Qdrant at {host}:{port}")
        except Exception as e:
            logger.error(f"Error connecting to Qdrant: {e}")
            raise
        
        # Create collection if it doesn't exist
        self._create_collection_if_not_exists()
    
    def _create_collection_if_not_exists(self):
        """Create the collection in Qdrant if it doesn't already exist."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.dimension,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created collection {self.collection_name}")
            except Exception as e:
                logger.error(f"Error creating collection: {e}")
                raise
    
    def index_documents(self, documents):
        """Index documents (id, embedding, payload) into Qdrant."""
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=documents
            )
            logger.info(f"Indexed {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
    
    def search(self, query_vector, limit=5):
        """Search for similar documents using a query vector."""
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            logger.info(f"Found {len(search_result)} search results")
            return search_result
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []