import os
import logging
from notion_connector import NotionConnector
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from search import NotionSearch
from rag import RAGProcessor
from github_logging import setup_github_logging

# Setup logging
setup_github_logging()
logger = logging.getLogger(__name__)

def index_notion_content():
    """Fetch Notion content, generate embeddings, and store them in the vector store."""
    try:
        logger.info("Starting Notion content indexing")
        
        # Fetch content from Notion
        logger.info("Connecting to Notion")
        notion = NotionConnector()
        
        logger.info("Fetching database content")
        pages = notion.fetch_database_content()
        logger.info(f"Fetched {len(pages)} pages from Notion database")
        
        # Extract text from pages and split into chunks
        logger.info("Extracting text from pages and splitting into chunks")
        chunks_data = notion.extract_text_from_pages(pages)
        logger.info(f"Created {len(chunks_data)} chunks from {len(pages)} pages")
        
        # Generate embeddings
        logger.info("Generating embeddings for chunks")
        embedding_generator = EmbeddingGenerator()
        documents = embedding_generator.generate_embeddings(chunks_data)
        logger.info(f"Generated embeddings for {len(documents)} chunks")
        
        # Store embeddings in vector database
        logger.info("Storing embeddings in vector database")
        vector_store = VectorStore()
        vector_store.store_embeddings(documents)
        logger.info("Embeddings stored successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error indexing Notion content: {str(e)}")
        return False

def search_notion(query: str, limit: int = 5, group_by_page: bool = True):
    """Search for Notion content similar to the query.
    
    Args:
        query (str): The search query.
        limit (int, optional): Maximum number of results to return. Defaults to 5.
        group_by_page (bool, optional): Whether to group results by page. Defaults to True.
    
    Returns:
        List[Dict[str, Any]]: List of search results.
    """
    try:
        search_client = NotionSearch()
        results = search_client.search(query, limit=limit, group_by_page=group_by_page)
        return results
    except Exception as e:
        logger.error(f"Error searching Notion: {str(e)}")
        return []

def generate_rag_answer(query: str):
    """Generate a comprehensive answer using RAG.
    
    Args:
        query (str): The user's query.
    
    Returns:
        Dict[str, Any]: The generated answer and supporting documents.
    """
    try:
        rag_processor = RAGProcessor()
        result = rag_processor.generate_response(query)
        return result
    except Exception as e:
        logger.error(f"Error generating RAG answer: {str(e)}")
        return {"answer": f"Error: {str(e)}", "pages": []}

def display_search_results(results, query):
    """Display search results in a formatted way.
    
    Args:
        results: The search results to display.
        query: The original search query.
    """
    print(f"\nSearch results for '{query}':\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']} (Score: {result['score']:.2f})")
        print(f"   Chunk {result.get('chunk_idx', 0) + 1}/{result.get('total_chunks', 1)}")
        print(f"   {result.get('excerpt', '')}")
        print()

def display_rag_results(rag_result, query):
    """Display RAG results in a formatted way.
    
    Args:
        rag_result: The RAG result to display.
        query: The original query.
    """
    print(f"\nComprehensive answer for '{query}':\n")
    print(rag_result["answer"])
    print("\nBased on these sources:")
    
    # Display source pages
    for i, page in enumerate(rag_result.get("pages", []), 1):
        print(f"{i}. {page['title']} (Score: {page['score']:.2f})")
        # If available, show the top chunk from each page
        if page.get("chunks"):
            top_chunk = page["chunks"][0]
            print(f"   Chunk {top_chunk.get('chunk_idx', 0) + 1}")
            print(f"   {top_chunk.get('excerpt', '')}")
        print()

def test_query(query="what are best ranking models"):
    """Run a test query and display results.
    
    Args:
        query (str, optional): The test query. Defaults to "what are best ranking models".
    """
    print(f"Running test query: '{query}'")
    
    # 1. Display search results
    print("\n--- SEARCH RESULTS ---")
    results = search_notion(query, limit=5)
    display_search_results(results, query)
    
    # 2. Display RAG results
    print("\n--- RAG RESULTS ---")
    rag_result = generate_rag_answer(query)
    display_rag_results(rag_result, query)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Notion semantic search tool")
    parser.add_argument("--index", action="store_true", help="Index Notion content")
    parser.add_argument("--search", type=str, help="Search Notion content")
    parser.add_argument("--rag", type=str, help="Generate a comprehensive answer using RAG")
    parser.add_argument("--test", action="store_true", help="Run a test query")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of search results")
    parser.add_argument("--no-group", action="store_true", help="Don't group search results by page")
    parser.add_argument("--github", action="store_true", help="Run in GitHub Actions mode")
    
    args = parser.parse_args()
    
    if args.github:
        # GitHub Actions specific run
        try:
            success = index_notion_content()
            if not success:
                sys.exit(1)  # Exit with error code if indexing failed
        except Exception as e:
            logger.error(f"Fatal error in GitHub Actions mode: {str(e)}")
            sys.exit(1)
            
    if args.index:
        index_notion_content()
    
    if args.search:
        group_by_page = not args.no_group
        results = search_notion(args.search, args.limit, group_by_page)
        display_search_results(results, args.search)
    
    if args.rag:
        rag_result = generate_rag_answer(args.rag)
        display_rag_results(rag_result, args.rag)
    
    if args.test:
        test_query()