import logging

logger = logging.getLogger(__name__)

class NotionSearch:
    def __init__(self, notion_connector, embedding_generator, vector_store):
        """Initialize the search system with components."""
        self.notion_connector = notion_connector
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
    
    def index_notion_content(self):
        """Fetch, process, and index Notion content."""
        # Fetch pages from Notion
        pages = self.notion_connector.fetch_database_content()
        logger.info(f"Fetched {len(pages)} pages from Notion")
        
        # Extract text from pages
        text_list = self.notion_connector.extract_text_from_pages(pages)
        logger.info(f"Extracted text from {len(text_list)} pages")
        
        # Generate embeddings and prepare documents for indexing
        documents = []
        for idx, content in text_list:
            embedding = self.embedding_generator.get_embedding(content)
            if embedding:
                documents.append({
                    "id": idx,
                    "vector": embedding,
                    "payload": {"content": content}
                })
        
        # Index documents if any
        if documents:
            self.vector_store.index_documents(documents)
            logger.info(f"Indexed {len(documents)} documents in the vector store")
        else:
            logger.warning("No documents to index")
    
    def search_notion_content(self, query, limit=5):
        """Search for Notion content similar to the query."""
        # Generate embedding for the query
        query_embedding = self.embedding_generator.get_embedding(query)
        
        if not query_embedding:
            logger.warning(f"Could not generate embedding for query: {query}")
            return []
        
        # Search using the query embedding
        search_results = self.vector_store.search(query_embedding, limit=limit)
        
        # Format the results
        formatted_results = []
        for hit in search_results:
            formatted_results.append({
                "content": hit.payload["content"],
                "score": hit.score
            })
        
        return formatted_results