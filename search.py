from openai import OpenAI
from qdrant_client import QdrantClient
import os
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class NotionSearch:
    def __init__(self):
        """Initialize the search client."""
        # Initialize OpenAI client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Create httpx client without proxies
        http_client = httpx.Client()
        
        # Create OpenAI client with custom http client
        self.openai_client = OpenAI(
            api_key=self.openai_api_key,
            http_client=http_client
        )
        
        # Update to the newer embedding model to match what you're using in embeddings.py
        self.embedding_model = "text-embedding-3-small"
        
        # Check if QDRANT_URL is provided in environment variables
        qdrant_url = os.getenv("QDRANT_URL")
        
        if qdrant_url:
            # Use cloud-hosted Qdrant
            api_key = os.getenv("QDRANT_API_KEY")
            if not api_key:
                raise ValueError("Qdrant API key not found in environment variables")
            
            self.qdrant_client = QdrantClient(url=qdrant_url, api_key=api_key)
            logger.info(f"Connected to cloud Qdrant at {qdrant_url}")
        else:
            # Use local Qdrant
            self.qdrant_client = QdrantClient(path="./qdrant_storage")
            logger.info("Connected to local Qdrant storage")
        
        self.collection_name = "notion_chunks"
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate an embedding for the search query.
        
        Args:
            query (str): The search query.
            
        Returns:
            List[float]: The embedding vector.
        """
        response = self.openai_client.embeddings.create(
            input=query,
            model=self.embedding_model
        )
        
        return response.data[0].embedding
    
    def search(self, query: str, limit: int = 10, group_by_page: bool = True, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Search for Notion chunks similar to the query."""
        query_embedding = self.generate_query_embedding(query)
        
        # Use old format for Qdrant 1.6.0
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,  # Simple vector, not named
            limit=limit
        )
        
        # Process the results
        if not group_by_page:
            # Return individual chunks
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "title": result.payload.get("title", "Untitled"),
                    "page_id": result.payload.get("page_id", ""),
                    "chunk_idx": result.payload.get("chunk_idx", 0),
                    "total_chunks": result.payload.get("total_chunks", 1),
                    "content": result.payload.get("chunk", ""),
                    "score": result.score
                })
            
            logger.info(f"Found {len(formatted_results)} chunks for query: {query}")
            return formatted_results
        
        else:
            # Group chunks by page and take the best chunk from each page
            pages = defaultdict(list)
            
            for result in search_results:
                page_id = result.payload.get("page_id", "")
                pages[page_id].append({
                    "title": result.payload.get("title", "Untitled"),
                    "page_id": page_id,
                    "chunk_idx": result.payload.get("chunk_idx", 0),
                    "total_chunks": result.payload.get("total_chunks", 1),
                    "content": result.payload.get("chunk", ""),
                    "score": result.score
                })
            
            # Take the top chunks from each page
            top_results = []
            
            # Sort pages by their highest scoring chunk
            sorted_pages = sorted(
                pages.items(), 
                key=lambda x: max(chunk["score"] for chunk in x[1]), 
                reverse=True
            )
            
            # Take the top pages
            for page_id, chunks in sorted_pages[:max_pages]:
                # Sort chunks within this page by score
                sorted_chunks = sorted(chunks, key=lambda x: x["score"], reverse=True)
                
                # Add relevant excerpts from each chunk
                for chunk in sorted_chunks[:3]:  # Take up to 3 best chunks per page
                    excerpt = self.create_relevant_excerpt(chunk["content"], query)
                    chunk["excerpt"] = excerpt
                    top_results.append(chunk)
            
            logger.info(f"Found {len(top_results)} relevant chunks from {len(pages)} pages for query: {query}")
            return top_results
    
    def create_relevant_excerpt(self, content: str, query: str, max_length: int = 300) -> str:
        """Create a relevant excerpt from content based on the query.
        
        Args:
            content (str): The full content text.
            query (str): The search query.
            max_length (int, optional): Maximum length of the excerpt. Defaults to 300.
            
        Returns:
            str: The relevant excerpt.
        """
        if not content:
            return ""
        
        # Simple implementation: find a paragraph containing query keywords
        paragraphs = content.split("\n")
        
        # Try to find paragraphs that contain query terms
        query_terms = query.lower().split()
        
        for paragraph in paragraphs:
            if any(term in paragraph.lower() for term in query_terms):
                if len(paragraph) <= max_length:
                    return paragraph
                
                # Find the position of the first matching term
                positions = []
                for term in query_terms:
                    pos = paragraph.lower().find(term)
                    if pos != -1:
                        positions.append(pos)
                
                if positions:
                    # Center the excerpt around the first match
                    center = min(positions)
                    start = max(0, center - (max_length // 2))
                    end = min(len(paragraph), start + max_length)
                    
                    # Adjust start to avoid cutting words
                    if start > 0:
                        while start > 0 and paragraph[start] != ' ':
                            start -= 1
                        start += 1  # Skip the space
                    
                    # Adjust end to avoid cutting words
                    if end < len(paragraph):
                        while end < len(paragraph) and paragraph[end] != ' ':
                            end += 1
                    
                    excerpt = paragraph[start:end]
                    if start > 0:
                        excerpt = "..." + excerpt
                    if end < len(paragraph):
                        excerpt = excerpt + "..."
                    
                    return excerpt
        
        # If no paragraphs contain query terms, return the beginning of the content
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + "..."