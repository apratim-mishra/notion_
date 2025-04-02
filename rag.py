from typing import List, Dict, Any
import logging
from openai import OpenAI
import os
import httpx
from dotenv import load_dotenv
from search import NotionSearch
import time
import random

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

class RAGProcessor:
    def __init__(self):
        """Initialize the RAG processor."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        http_client = httpx.Client()
        self.client = OpenAI(
            api_key=self.openai_api_key,
            http_client=http_client
        )

        self.search_client = NotionSearch()
        self.model = "gpt-3.5-turbo"  # Changed from gpt-4o-mini which appears to be a typo
        self.max_tokens = 4096  # Adjust based on your model
    
    def retrieve_documents(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks based on the query.
        
        Args:
            query (str): The user's query
            limit (int): Number of chunks to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of retrieved document chunks
        """
        # Get chunks with group_by_page=False to retrieve individual chunks
        return self.search_client.search(query, limit=limit, group_by_page=False)
    
    def construct_prompt(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """Construct a prompt for the language model using retrieved chunks.
        
        Args:
            query (str): The user's query
            chunks (List[Dict[str, Any]]): List of retrieved document chunks
            
        Returns:
            str: The constructed prompt
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            # Combine title and content for better context
            content = f"Title: {chunk['title']} (Chunk {chunk['chunk_idx'] + 1}/{chunk['total_chunks']})\nContent: {chunk['content']}"
            context_parts.append(f"{i}. {content}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""Using the provided context, answer the following question comprehensively.

Context:
{context}

Question: {query}

Answer:
"""
        return prompt
    
    def with_retry(self, operation, max_retries=3, *args, **kwargs):
        """Execute an operation with retry logic."""
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.random()
                    logger.warning(f"RAG operation failed, retrying in {wait_time:.2f}s: {str(e)}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All RAG operation attempts failed: {str(e)}")
                    raise

    def generate_response(self, query: str) -> Dict[str, Any]:
        """Generate a comprehensive response to the query using RAG.
        
        Args:
            query (str): The user's query
            
        Returns:
            Dict[str, Any]: A dictionary containing the generated response and retrieved chunks
        """
        try:
            # Retrieve relevant document chunks
            chunks = self.retrieve_documents(query)
            
            # Construct prompt
            prompt = self.construct_prompt(query, chunks)
            
            # Generate response using OpenAI API
            response = self.with_retry(
                self.client.chat.completions.create,
                3,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable assistant that provides comprehensive answers based on the given context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Group chunks by page for display in results
            pages = {}
            for chunk in chunks:
                page_id = chunk["page_id"]
                if page_id not in pages:
                    pages[page_id] = {
                        "title": chunk["title"],
                        "page_id": page_id,
                        "chunks": [],
                        "score": 0  # Will store the highest chunk score
                    }
                
                pages[page_id]["chunks"].append({
                    "chunk_idx": chunk["chunk_idx"],
                    "excerpt": self.search_client.create_relevant_excerpt(chunk["content"], query),
                    "score": chunk["score"]
                })
                
                # Update page score to highest chunk score
                pages[page_id]["score"] = max(pages[page_id]["score"], chunk["score"])
            
            # Convert to list and sort by score
            page_list = sorted(pages.values(), key=lambda x: x["score"], reverse=True)
            
            return {
                "answer": answer,
                "pages": page_list
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            return {
                "answer": f"Error generating response: {str(e)}",
                "pages": []
            } 