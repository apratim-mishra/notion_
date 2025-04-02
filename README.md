# Notion Search with RAG

A powerful semantic search system for Notion pages using RAG (Retrieval Augmented Generation) and vector search. This system allows you to search through your Notion content using natural language and get AI-generated responses based on your documents.

## Features

- 🔍 **Semantic Search**: Find relevant content using meaning, not just keywords
- 🤖 **RAG Integration**: Get AI-generated answers based on your Notion content
- 📚 **Chunk Management**: Smart document splitting for better context preservation
- 🔄 **Real-time Updates**: Index new Notion content as you add it
- 🌐 **REST API**: Easy-to-use endpoints for search and RAG queries
- 📊 **Vector Storage**: Efficient storage and retrieval using Qdrant
- 🔐 **Environment Management**: Secure API key handling

## Prerequisites

- Python 3.10 or higher
- Notion API key
- OpenAI API key
- Qdrant (local or cloud)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/apratim-mishra/notion_.git
cd notion_
```

2. Create a virtual environment:
```bash
python -m venv notion_py310_env
source notion_py310_env/bin/activate  # On Windows: notion_py310_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:
```env
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_database_id
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url  # Optional for cloud Qdrant
QDRANT_API_KEY=your_qdrant_api_key  # Optional for cloud Qdrant
```

## Usage

### 1. Index Your Notion Content
```bash
python main.py --index
```

### 2. Start the API Server
```bash
python api.py
```

### 3. Search Your Content

Using the API:
```bash
# Simple search
curl http://localhost:8000/search/your-query

# RAG query
curl http://localhost:8000/rag/your-question
```

Using the CLI:
```bash
# Simple search
python main.py --search "what is machine learning"

# RAG query
python main.py --rag "explain machine learning concepts"
```

## API Endpoints

- `GET /`: API information and available endpoints
- `GET /health`: Health check endpoint
- `GET /search/<query>`: Search endpoint for finding relevant content
- `GET /rag/<query>`: RAG endpoint for AI-generated answers

## Project Structure

## MLOps Features

This project includes:
- Version control with Git
- CI/CD with GitHub Actions
- Logging for monitoring
- Clean architecture for maintainability

## License

MIT

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NOTION_API_KEY` | Your Notion integration token | Yes |
| `NOTION_DATABASE_ID` | ID of your Notion database | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `QDRANT_URL` | Qdrant cloud URL | No |
| `QDRANT_API_KEY` | Qdrant cloud API key | No |

## Package Versions

## Troubleshooting

### Common Issues

1. **Indexing Errors**: 
   - Ensure your Notion API key has proper access
   - Check your database ID is correct
   - Verify OpenAI API key has sufficient credits

2. **Search Returns Empty**: 
   - Verify indexing completed successfully
   - Check qdrant_storage directory exists
   - Ensure vectors were properly stored

3. **RAG Not Working**: 
   - Check OpenAI API key and rate limits
   - Verify embeddings were generated correctly
   - Ensure proper Python version (3.10 recommended)

4. **API Connection Issues**:
   - Verify Flask server is running
   - Check port 8000 is available
   - Ensure all dependencies are installed

### Version Compatibility

- Python: 3.10 recommended
- Qdrant client: 1.6.0
- OpenAI: 1.3.7
- Flask: 2.3.3

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request



# Container runtime data
qdrant_storage/
notion_storage/
vector_storage/
