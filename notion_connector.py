import os
from typing import List, Tuple, Optional, Dict, Any
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError
import logging
import re
import time
import random

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class NotionConnector:
    def __init__(self) -> None:
        """Initialize the Notion client with API key from environment variables.
        
        Raises:
            ValueError: If NOTION_API_KEY or NOTION_DATABASE_ID environment variables are not set.
        """
        self.api_key = os.getenv("NOTION_API_KEY")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.api_key:
            raise ValueError("Notion API key not found in environment variables")
        
        if not self.database_id:
            raise ValueError("Notion database ID not found in environment variables")
        
        self.client = Client(auth=self.api_key)
    
    def with_retry(self, operation, max_retries=3, *args, **kwargs):
        """Execute an operation with retry logic."""
        for attempt in range(max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.random()  # Exponential backoff with jitter
                    logger.warning(f"Operation failed, retrying in {wait_time:.2f}s: {str(e)}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All operation attempts failed: {str(e)}")
                    raise
    
    def fetch_database_content(self) -> List[dict]:
        """Fetch all pages from the specified Notion database.
        
        Returns:
            List[dict]: List of pages from the Notion database.
            
        Raises:
            APIResponseError: If there's an error communicating with the Notion API.
        """
        results = []
        has_more = True
        next_cursor = None
        
        while has_more:
            query_params = {"database_id": self.database_id}
            if next_cursor:
                query_params["start_cursor"] = next_cursor
            
            try:
                response = self.with_retry(self.client.databases.query, 3, **query_params)
                results.extend(response["results"])
                has_more = response["has_more"]
                next_cursor = response.get("next_cursor")
                logger.info(f"Fetched {len(response['results'])} pages from Notion")
            except APIResponseError as e:
                logger.error(f"Error fetching Notion data: {str(e)}")
                raise
        
        return results
    
    def fetch_page_content(self, page_id: str) -> List[Dict[str, Any]]:
        """Fetch all blocks (content) from a Notion page.
        
        Args:
            page_id (str): The ID of the Notion page.
            
        Returns:
            List[Dict[str, Any]]: List of blocks from the Notion page.
            
        Raises:
            APIResponseError: If there's an error communicating with the Notion API.
        """
        try:
            all_blocks = []
            has_more = True
            next_cursor = None
            
            while has_more:
                query_params = {}
                if next_cursor:
                    query_params["start_cursor"] = next_cursor
                
                response = self.with_retry(self.client.blocks.children.list, 3, page_id, **query_params)
                all_blocks.extend(response["results"])
                has_more = response["has_more"]
                next_cursor = response.get("next_cursor")
                
            logger.info(f"Fetched {len(all_blocks)} blocks from page {page_id}")
            return all_blocks
            
        except APIResponseError as e:
            logger.error(f"Error fetching page content for {page_id}: {str(e)}")
            return []
    
    def extract_text_from_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        """Extract text content from Notion blocks.
        
        Args:
            blocks (List[Dict[str, Any]]): List of Notion blocks.
            
        Returns:
            str: Concatenated text content from all blocks.
        """
        content = []
        
        for block in blocks:
            block_type = block.get("type")
            
            if block_type == "paragraph":
                try:
                    text_items = block.get("paragraph", {}).get("rich_text", [])
                    if text_items:
                        for text_item in text_items:
                            content.append(text_item.get("plain_text", ""))
                except Exception as e:
                    logger.warning(f"Error extracting paragraph text: {str(e)}")
                    
            elif block_type == "heading_1":
                try:
                    text_items = block.get("heading_1", {}).get("rich_text", [])
                    if text_items:
                        heading_text = " ".join([item.get("plain_text", "") for item in text_items])
                        content.append(f"# {heading_text}")
                except Exception as e:
                    logger.warning(f"Error extracting heading_1 text: {str(e)}")
                    
            elif block_type == "heading_2":
                try:
                    text_items = block.get("heading_2", {}).get("rich_text", [])
                    if text_items:
                        heading_text = " ".join([item.get("plain_text", "") for item in text_items])
                        content.append(f"## {heading_text}")
                except Exception as e:
                    logger.warning(f"Error extracting heading_2 text: {str(e)}")
                    
            elif block_type == "heading_3":
                try:
                    text_items = block.get("heading_3", {}).get("rich_text", [])
                    if text_items:
                        heading_text = " ".join([item.get("plain_text", "") for item in text_items])
                        content.append(f"### {heading_text}")
                except Exception as e:
                    logger.warning(f"Error extracting heading_3 text: {str(e)}")
                    
            elif block_type == "bulleted_list_item" or block_type == "numbered_list_item":
                try:
                    text_items = block.get(block_type, {}).get("rich_text", [])
                    if text_items:
                        item_text = " ".join([item.get("plain_text", "") for item in text_items])
                        content.append(f"• {item_text}")
                except Exception as e:
                    logger.warning(f"Error extracting list item text: {str(e)}")
                    
            # Add more block types as needed
            
        return "\n".join(content)
    
    def split_into_chunks(self, text: str, chunk_size: int = 2048, overlap: int = 128) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text (str): Text to split.
            chunk_size (int): Maximum size of each chunk.
            overlap (int): Overlap between chunks.
            
        Returns:
            List[str]: List of text chunks.
        """
        if not text:
            return []
            
        # Split by paragraphs to maintain semantic meaning
        paragraphs = text.split("\n")
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            # Skip empty paragraphs
            if not paragraph.strip():
                continue
                
            paragraph_size = len(paragraph)
            
            # If adding this paragraph would exceed chunk size, finalize the current chunk
            if current_size + paragraph_size > chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                
                # Keep some of the last paragraphs for overlap
                overlap_size = 0
                overlap_paragraphs = []
                
                for p in reversed(current_chunk):
                    if overlap_size + len(p) <= overlap:
                        overlap_paragraphs.insert(0, p)
                        overlap_size += len(p)
                    else:
                        break
                
                current_chunk = overlap_paragraphs
                current_size = overlap_size
            
            # Add the paragraph to the current chunk
            current_chunk.append(paragraph)
            current_size += paragraph_size
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        
        return chunks
    
    def extract_text_from_pages(self, pages: List[dict]) -> List[Dict[str, Any]]:
        """Extract title and content text from Notion pages and split into chunks.
        
        Args:
            pages (List[dict]): List of Notion pages.
            
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing page info and content chunks.
        """
        chunks_data = []
        
        for idx, page in enumerate(pages):
            try:
                # Extract title
                title = page["properties"]["Name"]["title"][0]["text"]["content"]
                page_id = page["id"]
                
                # Fetch and extract content
                blocks = self.fetch_page_content(page_id)
                content = self.extract_text_from_blocks(blocks)
                
                # Split content into chunks
                content_chunks = self.split_into_chunks(content)
                
                # Add each chunk as a separate item, but with reference to the original page
                for chunk_idx, chunk in enumerate(content_chunks):
                    chunk_data = {
                        "id": f"{idx}-{chunk_idx}",
                        "page_idx": idx,
                        "page_id": page_id,
                        "title": title,
                        "chunk_idx": chunk_idx,
                        "chunk": chunk,
                        "total_chunks": len(content_chunks)
                    }
                    chunks_data.append(chunk_data)
                
                logger.info(f"Processed page {idx}: {title} into {len(content_chunks)} chunks")
            except (KeyError, IndexError) as e:
                logger.warning(f"Skipping page {idx} due to missing title: {str(e)}")
        
        return chunks_data