import os
from dotenv import load_dotenv
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class EmbeddingGenerator:
    def __init__(self):
        """Initialize the embedding generator with OpenAI API key."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def get_embedding(self, text):
        """Generate an embedding for the given text using OpenAI API."""
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid text for embedding: {text}")
            return None
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding for text '{text[:20]}...': \n\n{str(e)}")
            return None