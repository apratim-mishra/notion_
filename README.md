# Notion LLM Search

A local search system for Notion pages using LLMs and vector search, with basic MLOps practices for personal projects.

## Features
- Fetch content from Notion databases
- Generate embeddings using OpenAI's models
- Store and search embeddings using Qdrant
- Simple CLI for indexing and searching

## Setup

### Prerequisites
- Python 3.8 or higher
- Qdrant running locally (see installation instructions below)
- Notion API key
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/notion-llm-search.git
   cd notion-llm-search
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy the `.env.example` file to `.env`
   - Fill in your API keys and database ID

### Setting up Qdrant

Install Qdrant using Docker:
```
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

### Setting up Notion Integration

1. Visit [Notion's My Integrations page](https://www.notion.so/my-integrations)
2. Click "New Integration" and name it (e.g., "Local LLM Search")
3. Select your workspace and submit to get an API key
4. Copy the API key to your `.env` file
5. Share the integration with your Notion pages:
   - Open the page or database
   - Click "Share" in the top-right corner
   - Click "Invite"
   - Select your integration and grant at least read access
6. Get your database ID from the URL (e.g., https://www.notion.so/your-workspace/YOUR_DATABASE_ID)
   - Copy the database ID to your `.env` file

## Usage

### Indexing Notion Content

```
python main.py --index
```

### Searching

```
python main.py --search "your search query"
```

Limit the number of results:
```
python main.py --search "your search query" --limit 10
```

## MLOps Features

This project includes:
- Version control with Git
- CI/CD with GitHub Actions
- Logging for monitoring
- Clean architecture for maintainability

## License

MIT