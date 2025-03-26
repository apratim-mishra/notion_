import os
from dotenv import load_dotenv
from notion_client import Client
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class NotionConnector:
    def __init__(self):
        """Initialize the Notion client with API key from environment variables."""
        self.api_key = os.getenv("NOTION_API_KEY")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.api_key:
            raise ValueError("Notion API key not found in environment variables")
        
        if not self.database_id:
            raise ValueError("Notion database ID not found in environment variables")
        
        self.client = Client(auth=self.api_key)
    
    def fetch_database_content(self):
        """Fetch all pages from the specified Notion database."""
        results = []
        has_more = True
        next_cursor = None
        
        while has_more:
            query_params = {"database_id": self.database_id}
            if next_cursor:
                query_params["start_cursor"] = next_cursor
            
            try:
                response = self.client.databases.query(**query_params)
                results.extend(response["results"])
                has_more = response["has_more"]
                next_cursor = response.get("next_cursor")
                logger.info(f"Fetched {len(response['results'])} pages from Notion")
            except Exception as e:
                logger.error(f"Error fetching Notion data: {e}")
                break
        
        return results
    
    def extract_text_from_pages(self, pages):
        """Extract title text from Notion pages."""
        text_list = []
        for idx, page in enumerate(pages):
            try:
                title = page["properties"]["Name"]["title"][0]["text"]["content"]
                text_list.append((idx, title))
            except (KeyError, IndexError) as e:
                logger.warning(f"Skipping page {idx} due to missing title: {e}")
        return text_list
        