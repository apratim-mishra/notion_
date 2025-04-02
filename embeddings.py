import os
from dotenv import load_dotenv
import logging
from openai import OpenAI
from typing import List, Dict, Any
import httpx
import time
import random

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class EmbeddingGenerator:
    def __init__(self):
        """Initialize the embedding generator with OpenAI API key."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        http_client = httpx.Client(timeout=60.0)  # Increased timeout
        self.client = OpenAI(
            api_key=self.api_key,
            http_client=http_client
        )
        self.model = "text-embedding-3-small"
    
    def generate_embedding_with_retry(self, text: str, max_retries=3):
        """Generate embedding with retry logic."""
        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    input=text,
                    model=self.model
                )
                return response.data[0].embedding
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.random()  # Exponential backoff with jitter
                    logger.warning(f"Embedding generation failed, retrying in {wait_time:.2f}s: {str(e)}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All embedding generation attempts failed: {str(e)}")
                    raise
    
    def generate_embeddings(self, chunks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for text chunks using OpenAI API.
        
        Args:
            chunks_data (List[Dict[str, Any]]): List of dictionaries containing chunk data.
            
        Returns:
            List[Dict[str, Any]]: List of documents with embeddings.
        """
        documents = []
        
        for chunk_data in chunks_data:
            try:
                # Combine title and chunk for embedding
                title = chunk_data["title"]
                chunk = chunk_data["chunk"]
                
                # Weight the title more heavily
                text_to_embed = f"{title} {title}\n\n{chunk}"
                
                embedding = self.generate_embedding_with_retry(text_to_embed)
                
                # Copy chunk_data and add embedding
                doc_with_embedding = chunk_data.copy()
                doc_with_embedding["embedding"] = embedding
                
                documents.append(doc_with_embedding)
                
                logger.info(f"Generated embedding for chunk {chunk_data['id']}: {title} (chunk {chunk_data['chunk_idx'] + 1}/{chunk_data['total_chunks']})")
            except Exception as e:
                logger.error(f"Error generating embedding for chunk {chunk_data['id']}: {str(e)}")
        
        return documents