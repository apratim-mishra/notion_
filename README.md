# 🔍 Notion Semantic Search with RAG

A powerful semantic search system for Notion pages using RAG (Retrieval Augmented Generation) and vector search. This system allows you to search through your Notion content using natural language and get AI-generated responses based on your documents.

## ✨ Features

- 🔍 **Semantic Search**: Find relevant content using meaning, not just keywords
- 🤖 **RAG Integration**: Get AI-generated answers with GPT-4.1 mini based on your Notion content
- 🛠️ **Intelligent Tools**: Web search, content analysis, and fact-checking tools for enhanced answers
- 📚 **Smart Chunking**: Advanced document splitting with overlap for better context preservation
- 🔄 **Real-time Updates**: Index new Notion content as you add it
- 🌐 **REST API**: Easy-to-use endpoints for search and RAG queries
- 📊 **Vector Storage**: Efficient storage and retrieval using Qdrant with cosine similarity
- 🔐 **Environment Management**: Secure API key handling with python-dotenv
- 📈 **Evaluation Suite**: Comprehensive eval framework using OpenAI Evals for quality assessment
- 🔍 **Duplicate Removal**: Advanced deduplication for cleaner search results
- 📊 **Relevance Scoring**: Multi-tier relevance categorization (high/medium/low)

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** (recommended) or 3.10+
- Notion API key ([Get one here](https://developers.notion.com/))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Qdrant (runs locally by default)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/apratim-mishra/notion_.git
cd notion_
```

2. **Create and activate virtual environment:**
```bash
# Using Python 3.11 (recommended)
python3.11 -m venv notion_py311_env
source notion_py311_env/bin/activate  # On Windows: notion_py311_env\Scripts\activate

# Or using Python 3.10
python3.10 -m venv notion_py310_env
source notion_py310_env/bin/activate
```

3. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Set up environment variables in `.env`:**
```env
# Required
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_database_id_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for cloud Qdrant)
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_cloud_api_key

# Optional (for enhanced search tools)
SERPER_API_KEY=your_serper_api_key  # For web search functionality
```

## 📖 Usage

### 1. Index Your Notion Content
```bash
python main.py --index
```
This will:
- Fetch all pages from your Notion database
- Split content into optimized chunks (500 chars with 50 char overlap)
- Generate embeddings using OpenAI's `text-embedding-3-small`
- Store in Qdrant vector database with metadata

### 2. Search Your Content

**Simple semantic search:**
```bash
python main.py --search "machine learning algorithms"
```

**RAG query with AI-generated answer:**
```bash
python main.py --rag "explain the difference between supervised and unsupervised learning"
```

**RAG with tool assistance:**
```bash
python main.py --rag-tools "what are the latest trends in AI development?"
```

### 3. Start the API Server
```bash
python api.py
```

**API Endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Simple search
curl http://localhost:8000/search/machine%20learning

# RAG query
curl http://localhost:8000/rag/explain%20neural%20networks

# RAG with tools
curl http://localhost:8000/rag-tools/latest%20AI%20developments
```

## 🏗️ Project Structure

```
notion_/
├── main.py                 # Main CLI interface and orchestration
├── notion_connector.py     # Notion API integration
├── embeddings.py          # OpenAI embeddings generation
├── vector_store.py        # Qdrant vector database operations
├── search.py              # Semantic search with relevance scoring
├── rag.py                 # RAG processing with GPT-4.1 mini
├── tools.py               # Enhanced query tools (web search, analysis)
├── api.py                 # Flask REST API
├── github_logging.py      # Logging configuration
├── monitoring.py          # System monitoring utilities
├── evals/                 # Evaluation framework
│   ├── rag_quality_eval.py
│   ├── search_relevance_eval.py
│   ├── embedding_quality_eval.py
│   ├── model_comparison_eval.py
│   └── run_all_evals.py
└── requirements.txt       # Python dependencies
```

## 🧪 Evaluation Suite

Run comprehensive evaluations using OpenAI Evals framework:

```bash
# Run all evaluations
python evals/run_all_evals.py

# Run individual evaluations
python evals/rag_quality_eval.py      # Test answer quality
python evals/search_relevance_eval.py # Test search relevance
python evals/embedding_quality_eval.py # Test embedding similarity
python evals/model_comparison_eval.py  # Compare different models
```

## ⚙️ Configuration

### Search Parameters
- **Similarity threshold**: 0.4 (minimum relevance score)
- **High quality threshold**: 0.7 (high relevance score)
- **Max results**: 50 (before filtering)
- **Chunk size**: 500 characters with 50 character overlap
- **Embedding model**: `text-embedding-3-small` (1536 dimensions)

### RAG Parameters
- **Model**: `gpt-4.1-mini` for optimal balance of quality, speed, and cost
- **Context window**: ~800K tokens utilized efficiently
- **Max output**: 4,000 tokens
- **Retrieved chunks**: 5-15 (adaptive based on relevance)
- **Temperature**: 0.1 for consistent, factual responses

## 🛠️ Tools Integration

The system includes three powerful tools for enhanced query answering:

1. **Web Search Tool**: Real-time web search for current information
2. **Content Analysis Tool**: Deep analysis of retrieved content patterns
3. **Fact Checking Tool**: Verification of claims and statements

## 🔧 Troubleshooting

### Common Issues

**Python Version Issues:**
```bash
# If you get version conflicts, use Python 3.11
brew install python@3.11
python3.11 -m venv notion_py311_env
```

**Empty Search Results:**
- Check similarity threshold in `search.py` (lower from 0.7 to 0.4)
- Verify indexing completed successfully
- Ensure Qdrant storage directory exists

**RAG Not Working:**
- Verify OpenAI API key has sufficient credits
- Check model availability (`gpt-4.1-mini`)
- Ensure proper chunk retrieval

**API Connection Issues:**
- Verify Flask server is running on port 8000
- Check all dependencies are installed
- Ensure `.env` file is properly configured

### Performance Optimization

**For large Notion databases (>100 pages):**
- Increase chunk overlap for better context
- Use batch processing for embeddings
- Consider using Qdrant cloud for better performance

**For better search quality:**
- Fine-tune similarity thresholds
- Add more diverse training queries to evaluations
- Monitor relevance scores and adjust accordingly

## 📊 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NOTION_API_KEY` | Your Notion integration token | ✅ | - |
| `NOTION_DATABASE_ID` | ID of your Notion database | ✅ | - |
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ | - |
| `QDRANT_URL` | Qdrant cloud URL | ❌ | `http://localhost:6333` |
| `QDRANT_API_KEY` | Qdrant cloud API key | ❌ | - |
| `SERPER_API_KEY` | Serper API for web search | ❌ | - |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Follow clean code principles and add tests
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Notion API](https://developers.notion.com/) for content access
- [OpenAI](https://openai.com/) for embeddings and language models
- [Qdrant](https://qdrant.tech/) for vector search capabilities
- [OpenAI Evals](https://github.com/openai/evals) for evaluation framework

---

**Built with ❤️ for better knowledge discovery**
