from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging
import uuid
import tempfile

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class VectorStore:
    def __init__(self):
        """Initialize the vector store client."""
        # Check if QDRANT_URL is provided in environment variables
        qdrant_url = os.getenv("QDRANT_URL")
        
        if qdrant_url:
            # Use cloud-hosted Qdrant
            api_key = os.getenv("QDRANT_API_KEY")
            if not api_key:
                raise ValueError("Qdrant API key not found in environment variables")
            
            self.client = QdrantClient(url=qdrant_url, api_key=api_key)
            logger.info(f"Connected to cloud Qdrant at {qdrant_url}")
        else:
            # Use local Qdrant - with tmpdir for GitHub Actions compatibility
            temp_dir = tempfile.gettempdir()
            storage_path = os.path.join(temp_dir, "qdrant_storage")
            os.makedirs(storage_path, exist_ok=True)
            
            self.client = QdrantClient(path=storage_path)
            logger.info(f"Connected to local Qdrant storage at {storage_path}")
        
        self.collection_name = "notion_chunks"
        self.vector_size = 1536  # Size of text-embedding-3-small embeddings
    
    def create_collection(self):
        """Create the vector collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            # Use the OLD format for Qdrant 1.6.0
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
        else:
            logger.info(f"Collection {self.collection_name} already exists")
    
    def store_embeddings(self, documents: List[Dict[str, Any]]):
        """Store document embeddings in the vector store."""
        # First recreate collection to clear existing data
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted existing collection: {self.collection_name}")
        except Exception as e:
            logger.warning(f"Error deleting collection (may not exist yet): {str(e)}")
        
        self.create_collection()
        
        # Prepare points for the vector store
        points = []
        for doc in documents:
            # Convert document ID to a valid UUID
            uuid_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"notion-chunk-{doc['id']}"))
            
            # Use the OLD format for Qdrant 1.6.0
            point = models.PointStruct(
                id=uuid_id,
                vector=doc["embedding"],  # Use unnamed vector format
                payload={
                    "chunk_id": doc["id"],
                    "page_idx": doc["page_idx"],
                    "page_id": doc["page_id"],
                    "title": doc["title"],
                    "chunk_idx": doc["chunk_idx"],
                    "chunk": doc["chunk"],
                    "total_chunks": doc["total_chunks"]
                }
            )
            
            points.append(point)
        
        # Store points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
                wait=True
            )
            logger.info(f"Stored batch of {len(batch)} document chunks")