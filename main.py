import os
from dotenv import load_dotenv
import argparse
from notion_connector import NotionConnector
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from search import NotionSearch
from monitoring import setup_logging

# Setup logging
logger = setup_logging()

def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Notion LLM Search")
    parser.add_argument("--index", action="store_true", help="Index Notion content")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Number of search results to return")
    args = parser.parse_args()
    
    # Initialize components
    try:
        notion_connector = NotionConnector()
        embedding_generator = EmbeddingGenerator()
        vector_store = VectorStore()
        notion_search = NotionSearch(notion_connector, embedding_generator, vector_store)
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        return
    
    # Handle commands
    if args.index:
        logger.info("Indexing Notion content...")
        notion_search.index_notion_content()
        logger.info("Indexing complete")
    
    if args.search:
        logger.info(f"Searching for: {args.search}")
        results = notion_search.search_notion_content(args.search, limit=args.limit)
        
        if results:
            print(f"\nFound {len(results)} results for '{args.search}':")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result['content']} (Score: {result['score']:.4f})")
        else:
            print(f"\nNo results found for '{args.search}'")
    
    # If no arguments, show help
    if not args.index and not args.search:
        parser.print_help()

if __name__ == "__main__":
    main()