import json
import urllib.request
import urllib.parse
import urllib.error
import re

def search_news(query: str, source: str = "all") -> str:
    """
    Search for current news by fetching content from major news websites.
    
    Args:
        query (str): The search query/topic
        source (str): News source ("bbc", "reuters", "cnn", "all")
        
    Returns:
        str: JSON string with news results
    """
    news_sources = {
        "bbc": {
            "url": "https://www.bbc.com/news",
            "name": "BBC News"
        },
        "reuters": {
            "url": "https://www.reuters.com",
            "name": "Reuters"
        },
        "cnn": {
            "url": "https://www.cnn.com",
            "name": "CNN"
        }
    }
    
    results = []
    sources_to_check = [source] if source != "all" else list(news_sources.keys())
    
    for src in sources_to_check:
        if src not in news_sources:
            continue
            
        try:
            news_data = _fetch_news_from_source(news_sources[src], query)
            if news_data:
                results.extend(news_data)
        except Exception as e:
            results.append({
                "source": news_sources[src]["name"],
                "error": f"Failed to fetch from {src}: {str(e)}"
            })
    
    return json.dumps({
        "query": query,
        "total_results": len([r for r in results if "error" not in r]),
        "sources_checked": sources_to_check,
        "results": results[:10],  # Limit to 10 results
        "status": "success"
    }, indent=2)

def _fetch_news_from_source(source_info, query):
    """Fetch news content from a specific source"""
    try:
        req = urllib.request.Request(source_info["url"])
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read(1024 * 512).decode('utf-8', errors='ignore')  # 512KB limit
            
            # Extract headlines and links
            headlines = _extract_headlines(content, source_info["name"])
            
            # Filter headlines based on query if provided
            if query and query.lower() != "all":
                query_words = query.lower().split()
                filtered_headlines = []
                for headline in headlines:
                    headline_text = headline.get("title", "").lower()
                    if any(word in headline_text for word in query_words):
                        headline["relevance"] = "high"
                        filtered_headlines.append(headline)
                    elif any(word in headline.get("summary", "").lower() for word in query_words):
                        headline["relevance"] = "medium"
                        filtered_headlines.append(headline)
                
                return filtered_headlines[:5] if filtered_headlines else headlines[:3]
            
            return headlines[:5]
            
    except Exception as e:
        return [{"source": source_info["name"], "error": str(e)}]

def _extract_headlines(content, source_name):
    """Extract headlines from HTML content"""
    headlines = []
    
    # Common patterns for headlines
    patterns = [
        r'<h[1-3][^>]*>([^<]+)</h[1-3]>',  # h1, h2, h3 tags
        r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>',  # links that might be headlines
        r'<title>([^<]+)</title>',  # page title
    ]
    
    # Extract title first
    title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
    if title_match:
        headlines.append({
            "title": title_match.group(1).strip(),
            "source": source_name,
            "type": "page_title",
            "url": "",
            "summary": f"Main page of {source_name}"
        })
    
    # Extract headlines
    headline_pattern = r'<h[1-3][^>]*>([^<]+)</h[1-3]>'
    headline_matches = re.findall(headline_pattern, content, re.IGNORECASE)
    
    for i, headline in enumerate(headline_matches[:8]):
        clean_headline = re.sub(r'<[^>]+>', '', headline).strip()
        if len(clean_headline) > 10 and not any(skip in clean_headline.lower() for skip in ['menu', 'search', 'login', 'subscribe']):
            headlines.append({
                "title": clean_headline,
                "source": source_name,
                "type": "headline",
                "url": "",
                "summary": f"Headline from {source_name}"
            })
    
    # Extract some article links
    link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
    link_matches = re.findall(link_pattern, content, re.IGNORECASE)
    
    for url, link_text in link_matches[:5]:
        clean_text = re.sub(r'<[^>]+>', '', link_text).strip()
        if (len(clean_text) > 20 and 
            not any(skip in clean_text.lower() for skip in ['menu', 'search', 'login', 'subscribe', 'more', 'read']) and
            ('news' in url.lower() or 'article' in url.lower() or len(clean_text) > 30)):
            headlines.append({
                "title": clean_text,
                "source": source_name,
                "type": "article_link",
                "url": url if url.startswith('http') else f"https://{source_name.lower().replace(' ', '')}.com{url}",
                "summary": f"Article link from {source_name}"
            })
    
    return headlines

def fetch_article(url: str) -> str:
    """
    Fetch and extract the main content from a news article URL.
    
    Args:
        url (str): The article URL to fetch
        
    Returns:
        str: JSON string with article content
    """
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read(1024 * 1024).decode('utf-8', errors='ignore')  # 1MB limit
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "No title found"
            
            # Extract meta description
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
            description = desc_match.group(1) if desc_match else ""
            
            # Remove script, style, nav, footer elements
            clean_content = re.sub(r'<(script|style|nav|footer|header)[^>]*>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Extract main content (look for article, main, or content divs)
            main_content_patterns = [
                r'<article[^>]*>(.*?)</article>',
                r'<main[^>]*>(.*?)</main>',
                r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>'
            ]
            
            main_content = ""
            for pattern in main_content_patterns:
                match = re.search(pattern, clean_content, re.DOTALL | re.IGNORECASE)
                if match:
                    main_content = match.group(1)
                    break
            
            if not main_content:
                # Fallback: get content from body
                body_match = re.search(r'<body[^>]*>(.*?)</body>', clean_content, re.DOTALL | re.IGNORECASE)
                main_content = body_match.group(1) if body_match else clean_content
            
            # Remove all HTML tags
            text_content = re.sub(r'<[^>]+>', '', main_content)
            
            # Clean up whitespace
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Extract first few paragraphs as summary
            sentences = text_content.split('. ')
            summary = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else text_content
            
            return json.dumps({
                "url": url,
                "title": title,
                "description": description,
                "summary": summary[:500] + "..." if len(summary) > 500 else summary,
                "full_text": text_content[:2000] + "..." if len(text_content) > 2000 else text_content,
                "word_count": len(text_content.split()),
                "status": "success"
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "url": url,
            "error": f"Failed to fetch article: {str(e)}",
            "status": "error"
        })

def get_trending_topics() -> str:
    """
    Get trending topics by checking multiple news sources.
    
    Returns:
        str: JSON string with trending topics
    """
    try:
        # Check Google Trends (simple approach)
        trending_url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        
        req = urllib.request.Request(trending_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
            # Extract trending topics from RSS
            topics = []
            title_pattern = r'<title><!\[CDATA\[(.*?)\]\]></title>'
            matches = re.findall(title_pattern, content)
            
            for i, topic in enumerate(matches[1:11]):  # Skip first (feed title), get next 10
                topics.append({
                    "rank": i + 1,
                    "topic": topic.strip(),
                    "source": "Google Trends",
                    "category": "trending"
                })
            
            return json.dumps({
                "trending_topics": topics,
                "total_topics": len(topics),
                "source": "Google Trends US",
                "status": "success"
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Failed to fetch trending topics: {str(e)}",
            "status": "error"
        }) 