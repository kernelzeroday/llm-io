import json
import urllib.request
import urllib.parse
import urllib.error
import re

def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for current information using DuckDuckGo Instant Answer API.
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return (default: 5)
        
    Returns:
        str: JSON string with search results
    """
    try:
        # Use DuckDuckGo Instant Answer API (no API key required)
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'LLM-Agent/1.0 (Web Search)')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            data = json.loads(content)
            
            results = []
            
            # Get instant answer if available
            if data.get('Answer'):
                results.append({
                    "type": "instant_answer",
                    "title": "Instant Answer",
                    "content": data['Answer'],
                    "source": data.get('AnswerType', 'DuckDuckGo')
                })
            
            # Get abstract if available
            if data.get('Abstract'):
                results.append({
                    "type": "abstract",
                    "title": data.get('Heading', 'Abstract'),
                    "content": data['Abstract'],
                    "source": data.get('AbstractSource', 'Unknown'),
                    "url": data.get('AbstractURL', '')
                })
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        "type": "related_topic",
                        "title": topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else "Related",
                        "content": topic.get('Text', ''),
                        "url": topic.get('FirstURL', '')
                    })
            
            # Get definition if available
            if data.get('Definition'):
                results.append({
                    "type": "definition",
                    "title": "Definition",
                    "content": data['Definition'],
                    "source": data.get('DefinitionSource', 'Unknown'),
                    "url": data.get('DefinitionURL', '')
                })
            
            return json.dumps({
                "query": query,
                "total_results": len(results),
                "results": results[:num_results],
                "search_engine": "DuckDuckGo",
                "status": "success"
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "query": query,
            "error": f"Search failed: {str(e)}",
            "status": "error"
        })

def fetch_url(url: str, extract_text: bool = True) -> str:
    """
    Fetch content from a URL and optionally extract clean text.
    
    Args:
        url (str): The URL to fetch
        extract_text (bool): Whether to extract clean text from HTML
        
    Returns:
        str: JSON string with URL content
    """
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'LLM-Agent/1.0 (URL Fetcher)')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            content_type = response.headers.get('Content-Type', 'unknown')
            content = response.read(1024 * 1024).decode('utf-8', errors='ignore')  # 1MB limit
            
            result = {
                "url": url,
                "status_code": status_code,
                "content_type": content_type,
                "content_length": len(content),
                "raw_content": content[:2000] + "..." if len(content) > 2000 else content
            }
            
            if extract_text and 'html' in content_type.lower():
                # Extract title
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else "No title"
                
                # Remove script and style elements
                clean_content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
                clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL | re.IGNORECASE)
                
                # Remove HTML tags
                clean_content = re.sub(r'<[^>]+>', '', clean_content)
                
                # Clean up whitespace
                clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                
                result.update({
                    "title": title,
                    "text_content": clean_content[:3000] + "..." if len(clean_content) > 3000 else clean_content,
                    "word_count": len(clean_content.split()),
                    "extracted": True
                })
            
            return json.dumps(result, indent=2)
            
    except Exception as e:
        return json.dumps({
            "url": url,
            "error": f"Failed to fetch: {str(e)}",
            "status": "error"
        })

def check_url_status(url: str) -> str:
    """
    Check if a URL is accessible and get basic information.
    
    Args:
        url (str): The URL to check
        
    Returns:
        str: JSON string with URL status
    """
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'LLM-Agent/1.0 (Status Checker)')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.dumps({
                "url": url,
                "status": "accessible",
                "status_code": response.getcode(),
                "content_type": response.headers.get('Content-Type', 'unknown'),
                "server": response.headers.get('Server', 'unknown'),
                "final_url": response.geturl(),
                "redirected": response.geturl() != url
            }, indent=2)
            
    except urllib.error.HTTPError as e:
        return json.dumps({
            "url": url,
            "status": "error",
            "status_code": e.code,
            "error": f"HTTP {e.code}: {e.reason}"
        })
    except Exception as e:
        return json.dumps({
            "url": url,
            "status": "unreachable",
            "error": str(e)
        }) 