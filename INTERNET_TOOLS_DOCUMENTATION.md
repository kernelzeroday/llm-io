# Internet Tools Documentation

## Overview
This directory contains 5 powerful internet tools that give LLM agents the ability to search the web, fetch content, analyze data, generate test data, and perform cryptographic operations. All functions are designed to work seamlessly with LLM's function calling system.

## 🔍 Function 1: DuckDuckGo Search (`ddg_search.py`)

### Functions:
- `ddg_search(query, num_results=10)` - Real web search using DuckDuckGo HTML
- `search_news_ddg(query="news today")` - Specialized news search
- `curl_get(url, headers=None)` - Curl-like HTTP requests
- `fetch_page_content(url)` - Extract readable content from any webpage
- `deep_fetch_url(url, extract_links=True, max_content_length=50000)` - **NEW** Advanced URL fetching with comprehensive analysis
- `research_topic(query, num_sources=5, deep_fetch=True)` - **NEW** Multi-source research with deep analysis

### Key Features:
- **Real search results** from DuckDuckGo HTML interface
- **No API key required** - uses public search interface
- **Curl-like functionality** with custom headers
- **Content extraction** with title, description, and clean text
- **Gzip decompression** support
- **Error handling** for failed requests
- **🆕 Deep content analysis** - metadata, links, media, structured data
- **🆕 Multi-source research** - automatic relevance scoring and summarization
- **🆕 Link extraction** - categorized internal/external links
- **🆕 Media detection** - images, videos, audio files
- **🆕 Content quality metrics** - readability, structure analysis

### Usage Examples:
```bash
# Search for current news
llm --functions test_functions/ddg_search.py --td 'latest technology news' -s 'use ddg_search'

# Get news specifically
llm --functions test_functions/ddg_search.py --td 'AI developments' -s 'use search_news_ddg'

# Fetch specific webpage content
llm --functions test_functions/ddg_search.py --td 'Get content from https://www.bbc.com/news' -s 'use fetch_page_content'

# Deep analysis of any URL
llm --functions test_functions/ddg_search.py --td 'Analyze https://example.com with links and metadata' -s 'use deep_fetch_url'

# Comprehensive research on any topic
llm --functions test_functions/ddg_search.py --td 'Research AI developments in 2025' -s 'use research_topic'
```

### Sample Output:
```json
{
  "query": "news today",
  "total_results": 15,
  "results": [
    {
      "title": "Breaking News, Latest News and Videos | CNN",
      "url": "https://www.cnn.com/",
      "snippet": "",
      "position": 1
    }
  ],
  "search_engine": "DuckDuckGo HTML",
  "status": "success"
}
```

### 🔬 Deep Research Sample Output:
```json
{
  "url": "https://example.com/article",
  "metadata": {
    "title": "AI Trends 2025",
    "description": "Latest developments in artificial intelligence",
    "og_title": "AI Trends 2025 - Complete Guide"
  },
  "main_content": {
    "word_count": 2847,
    "estimated_reading_time_minutes": 14.2,
    "summary": "Artificial intelligence continues to evolve..."
  },
  "content_analysis": {
    "avg_words_per_sentence": 18.5,
    "question_count": 12,
    "number_count": 45
  },
  "total_links": 67,
  "media_info": {
    "images": 8,
    "videos": 2
  }
}
```

## 📰 Function 2: News Search (`news_search.py`)

### Functions:
- `search_news(query, source="all")` - Search major news websites
- `fetch_article(url)` - Extract full article content
- `get_trending_topics()` - Get trending topics from Google Trends

### Key Features:
- **Multi-source news search** (BBC, Reuters, CNN)
- **Headline extraction** with relevance scoring
- **Article content extraction** with summaries
- **Trending topics** from Google Trends RSS
- **Query filtering** for relevant results
- **Error recovery** for failed sources

### Usage Examples:
```bash
# Search specific news source
llm --functions test_functions/news_search.py --td 'technology news from BBC' -s 'use search_news with source=bbc'

# Get trending topics
llm --functions test_functions/news_search.py --td 'what is trending today' -s 'use get_trending_topics'
```

## 🌐 Function 3: Web Tools (`web_tools.py`)

### Functions:
- `web_request(url, method="GET", **kwargs)` - HTTP requests with multiple methods
- `fetch_url(url, extract_text=True)` - URL fetching with text extraction
- `check_url_status(url)` - URL accessibility checking

### Key Features:
- **Multiple HTTP methods** (GET, HEAD, POST, parse_url, extract_links, extract_text)
- **Link extraction** from HTML pages
- **Text extraction** with HTML cleaning
- **URL parsing** into components
- **Status checking** with response time
- **Size limits** to prevent memory issues

### Usage Examples:
```bash
# Check if URL is accessible
llm --functions test_functions/web_tools.py --td 'Check if google.com is working' -s 'use web_request with method=check_status'

# Extract all links from a page
llm --functions test_functions/web_tools.py --td 'Get all links from https://news.ycombinator.com' -s 'use web_request with method=extract_links'
```

## 🔧 Function 4: API Tools (`api_tools.py`)

### Functions:
- `api_request(url, operation="get", **kwargs)` - Advanced API interactions
- Supports: GET, POST, PUT, DELETE, json_parse, json_query, headers_analyze, api_test

### Key Features:
- **Full REST API support** with authentication
- **JSON parsing and validation** with structure analysis
- **JSON querying** using dot notation paths
- **Header analysis** including security headers
- **API endpoint testing** with health checks
- **Bearer token and API key authentication**

### Usage Examples:
```bash
# Test API endpoints
llm --functions test_functions/api_tools.py --td 'Test if httpbin.org API is working' -s 'use api_request with operation=api_test'

# Parse JSON data
llm --functions test_functions/api_tools.py --td 'Parse this JSON: {"users":[{"name":"Alice","age":30}]}' -s 'use api_request with operation=json_parse'
```

### Sample JSON Query:
```json
{
  "query_path": "users.0.name",
  "result": "Alice",
  "result_type": "str",
  "success": true
}
```

## 📊 Function 5: Data Generator (`data_generator.py`)

### Functions:
- `generate_data(data_type, count=10, **kwargs)` - Generate various test data types

### Supported Data Types:
- **users** - Random user profiles with emails, ages, cities
- **products** - E-commerce product data with prices, ratings
- **transactions** - Financial transaction records
- **logs** - System log entries with levels and timestamps
- **emails** - Random email addresses
- **passwords** - Secure random passwords

### Key Features:
- **Realistic test data** with proper relationships
- **Configurable count** and parameters
- **Timestamp generation** with random dates
- **Multiple data formats** (JSON structured output)
- **Error handling** for invalid data types

### Usage Examples:
```bash
# Generate test users
llm --functions test_functions/data_generator.py --td 'Generate 5 test users' -s 'use generate_data with data_type=users and count=5'

# Generate transaction data
llm --functions test_functions/data_generator.py --td 'Create sample transaction records' -s 'use generate_data with data_type=transactions'
```

### Sample Output:
```json
{
  "data_type": "users",
  "count": 3,
  "data": [
    {
      "id": 1,
      "first_name": "Alice",
      "last_name": "Smith",
      "email": "alice.smith@gmail.com",
      "age": 28,
      "city": "New York"
    }
  ]
}
```

## 🔐 Function 6: Crypto Utils (`crypto_utils.py`)

### Functions:
- `crypto_utils(operation, data, **kwargs)` - Cryptographic operations

### Supported Operations:
- **hash** - Generate MD5, SHA1, SHA256, SHA512 hashes
- **encode** - Base64 encoding
- **decode** - Base64 decoding
- **generate_key** - Random key generation (hex, url_safe, alphanumeric, password)
- **password_hash** - Secure password hashing with salt
- **verify_hash** - Hash verification (simple and salted)

### Key Features:
- **Multiple hash algorithms** with length information
- **Secure key generation** using secrets module
- **Salt-based password hashing** for security
- **Hash verification** supporting both simple and salted hashes
- **Entropy calculation** for generated keys

### Usage Examples:
```bash
# Hash some data
llm --functions test_functions/crypto_utils.py --td 'Hash the text "hello world" using SHA256' -s 'use crypto_utils with operation=hash'

# Generate secure password
llm --functions test_functions/crypto_utils.py --td 'Generate a 16-character secure password' -s 'use crypto_utils with operation=generate_key'
```

## 📝 Function 7: Text Analysis (`text_analysis.py`)

### Functions:
- `analyze_text(text)` - Comprehensive text analysis

### Analysis Features:
- **Basic statistics** - character, word, sentence, paragraph counts
- **Reading level** - Flesch readability score and level
- **Lexical diversity** - unique word ratio
- **Most common words** - frequency analysis
- **Complexity metrics** - average word/sentence length
- **Text quality indicators** - comprehensive scoring

### Usage Examples:
```bash
# Analyze article text
llm --functions test_functions/text_analysis.py --td 'Analyze the readability of this text: "The quick brown fox..."' -s 'use analyze_text'
```

### Sample Output:
```json
{
  "basic_stats": {
    "characters": 156,
    "words": 28,
    "sentences": 3,
    "unique_words": 25
  },
  "complexity": {
    "lexical_diversity": 0.893,
    "flesch_score": 72.3,
    "reading_level": "Fairly Easy"
  }
}
```

## 🚀 Testing All Functions

### Quick Test Script:
```bash
# Test all functions
python3 test_ddg_search.py
python3 test_news_functions.py

# Test individual functions
python3 -c "
import sys; sys.path.append('test_functions')
from ddg_search import ddg_search
print(ddg_search('AI news'))
"
```

### Integration with LLM:
```bash
# Use with IO Intelligence models (if API key set)
llm -m llama-3.3-70b --functions test_functions/ddg_search.py --td 'Search for latest AI developments'

# Use with any model that supports tools
llm --functions test_functions/crypto_utils.py --td 'Generate a secure API key'
```

## 🔧 Technical Details

### Error Handling:
- All functions return JSON with error information
- Timeout protection (10-15 seconds)
- Size limits to prevent memory issues
- Graceful degradation for failed requests

### Security Features:
- User-Agent rotation to avoid blocking
- Request size limits
- Secure random generation
- Input validation and sanitization

### Performance:
- Efficient regex patterns for content extraction
- Streaming support where applicable
- Memory-conscious content handling
- Connection pooling for multiple requests

## 📋 Function Summary

| Function | Purpose | Key Features | Use Cases |
|----------|---------|--------------|-----------|
| `ddg_search` | Web search | Real results, no API key | Current news, research |
| `news_search` | News aggregation | Multi-source, filtering | Breaking news, trends |
| `web_tools` | Web utilities | HTTP methods, parsing | Site analysis, monitoring |
| `api_tools` | API interaction | REST support, auth | API testing, integration |
| `data_generator` | Test data | Multiple types, realistic | Development, testing |
| `crypto_utils` | Cryptography | Hashing, keys, encoding | Security, authentication |
| `text_analysis` | Text metrics | Readability, complexity | Content analysis, SEO |

## 🎯 Best Practices

1. **Always handle errors** - Check for "error" field in responses
2. **Respect rate limits** - Don't make too many requests rapidly
3. **Use appropriate timeouts** - Default 10-15 seconds is usually sufficient
4. **Validate inputs** - Ensure URLs are properly formatted
5. **Check content size** - Large responses are truncated for safety
6. **Use specific queries** - More specific searches yield better results

## 🔗 Integration Examples

### News Monitoring Agent:
```python
# Search for news, fetch articles, analyze content
news_results = ddg_search("AI breakthrough 2025")
for result in news_results["results"]:
    article = fetch_page_content(result["url"])
    analysis = analyze_text(article["text_content"])
    print(f"Readability: {analysis['complexity']['reading_level']}")
```

### API Testing Agent:
```python
# Test API, analyze responses, generate test data
api_status = api_request("https://api.example.com", "api_test")
test_users = generate_data("users", count=5)
# Use test data for API testing
```

### Security Analysis Agent:
```python
# Analyze website security, check headers, hash content
headers = api_request("https://example.com", "headers_analyze")
content_hash = crypto_utils("hash", page_content, algorithm="sha256")
```

These tools provide comprehensive internet access capabilities for LLM agents, enabling them to gather current information, analyze content, and perform various web-related tasks autonomously. 