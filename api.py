from flask import Flask, jsonify, request
import os
import sys
from dotenv import load_dotenv
import traceback

try:
    from search import NotionSearch
    from rag import RAGProcessor
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Root route
@app.route("/")
def index():
    return jsonify({
        "status": "ok",
        "message": "Notion Search API is running",
        "endpoints": {
            "health": "/health",
            "search": "/search/<query>",
            "rag": "/rag/<query>"
        }
    })

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# Search endpoint
@app.route("/search/<query>")
def search(query):
    try:
        limit = request.args.get('limit', default=5, type=int)
        search_client = NotionSearch()
        results = search_client.search(query, limit=limit)
        return jsonify({"results": results})
    except Exception as e:
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(f"Error in search endpoint: {error_details}")
        return jsonify(error_details), 500

# RAG endpoint
@app.route("/rag/<query>")
def rag(query):
    try:
        rag_processor = RAGProcessor()
        result = rag_processor.generate_response(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server on port 8000...")
    app.run(host="0.0.0.0", port=8000, debug=True) 