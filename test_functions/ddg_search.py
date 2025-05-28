import json
import urllib.request
import urllib.parse
import urllib.error
import re

def ddg_search(query: str, num_results: int = 10) -> str:
    """
    Search DuckDuckGo HTML directly for real search results.
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return (default: 10)
        
    Returns:
        str: JSON string with search results
    """
    try:
        # Use DuckDuckGo HTML search directly
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        req.add_header('Accept-Language', 'en-US,en;q=0.5')
        req.add_header('Accept-Encoding', 'gzip, deflate')
        req.add_header('DNT', '1')
        req.add_header('Connection', 'keep-alive')
        req.add_header('Upgrade-Insecure-Requests', '1')
        
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read()
            
            # Handle gzip encoding if present
            if response.headers.get('Content-Encoding') == 'gzip':
                import gzip
                content = gzip.decompress(content)
            
            content = content.decode('utf-8', errors='ignore')
            
            # Extract search results
            results = _extract_ddg_results(content)
            
            return json.dumps({
                "query": query,
                "total_results": len(results),
                "results": results[:num_results],
                "search_engine": "DuckDuckGo HTML",
                "status": "success",
                "url_searched": url
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "query": query,
            "error": f"Search failed: {str(e)}",
            "status": "error"
        })

def _extract_ddg_results(content):
    """Extract search results from DuckDuckGo HTML"""
    results = []
    
    # DuckDuckGo result pattern - look for result containers
    # Results are typically in divs with class containing "result"
    result_pattern = r'<div[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</div>\s*</div>'
    result_matches = re.findall(result_pattern, content, re.DOTALL | re.IGNORECASE)
    
    # Alternative pattern for DDG results
    if not result_matches:
        result_pattern = r'<div[^>]*class="[^"]*web-result[^"]*"[^>]*>(.*?)</div>'
        result_matches = re.findall(result_pattern, content, re.DOTALL | re.IGNORECASE)
    
    # Another pattern for DDG
    if not result_matches:
        result_pattern = r'<div[^>]*class="[^"]*links_main[^"]*"[^>]*>(.*?)</div>'
        result_matches = re.findall(result_pattern, content, re.DOTALL | re.IGNORECASE)
    
    # Fallback: look for any div containing links and titles
    if not result_matches:
        # Look for patterns that contain both a link and title
        link_title_pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>[^<]*<[^>]*>([^<]*)</[^>]*>'
        matches = re.findall(link_title_pattern, content, re.IGNORECASE)
        
        for i, (url, title, snippet) in enumerate(matches[:15]):
            if (url.startswith('http') and 
                len(title.strip()) > 5 and 
                'duckduckgo' not in url.lower() and
                not any(skip in title.lower() for skip in ['search', 'menu', 'login', 'privacy'])):
                
                results.append({
                    "title": title.strip(),
                    "url": url,
                    "snippet": snippet.strip()[:200] + "..." if len(snippet.strip()) > 200 else snippet.strip(),
                    "position": i + 1
                })
    
    # Try to extract from the actual DDG HTML structure
    if not results:
        # Look for the specific DDG result structure
        # DDG often uses patterns like: <a class="result__a" href="...">title</a>
        title_url_pattern = r'<a[^>]*class="[^"]*result[^"]*"[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
        title_matches = re.findall(title_url_pattern, content, re.IGNORECASE)
        
        for i, (url, title) in enumerate(title_matches[:15]):
            if (url.startswith('http') and 
                len(title.strip()) > 5 and 
                'duckduckgo' not in url.lower()):
                
                # Try to find snippet for this result
                snippet = ""
                # Look for snippet near this title
                title_escaped = re.escape(title[:20])
                snippet_pattern = f'{title_escaped}.*?<[^>]*class="[^"]*snippet[^"]*"[^>]*>([^<]+)</[^>]*>'
                snippet_match = re.search(snippet_pattern, content, re.DOTALL | re.IGNORECASE)
                if snippet_match:
                    snippet = snippet_match.group(1).strip()
                
                results.append({
                    "title": title.strip(),
                    "url": url,
                    "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet,
                    "position": i + 1
                })
    
    # Final fallback: extract any reasonable looking links
    if not results:
        # Look for any links that might be results
        all_links_pattern = r'<a[^>]*href="(https?://[^"]*)"[^>]*>([^<]+)</a>'
        all_matches = re.findall(all_links_pattern, content, re.IGNORECASE)
        
        seen_domains = set()
        for i, (url, title) in enumerate(all_matches):
            domain = urllib.parse.urlparse(url).netloc.lower()
            
            if (len(title.strip()) > 10 and 
                domain not in seen_domains and
                'duckduckgo' not in domain and
                not any(skip in title.lower() for skip in ['search', 'menu', 'login', 'privacy', 'cookie']) and
                not any(skip in domain for skip in ['duckduckgo', 'google', 'bing'])):
                
                seen_domains.add(domain)
                results.append({
                    "title": title.strip(),
                    "url": url,
                    "snippet": f"Result from {domain}",
                    "position": len(results) + 1
                })
                
                if len(results) >= 10:
                    break
    
    return results

def curl_get(url: str, headers: dict = None) -> str:
    """
    Perform a curl-like GET request to any URL.
    
    Args:
        url (str): The URL to fetch
        headers (dict): Optional headers to send
        
    Returns:
        str: JSON string with response data
    """
    try:
        req = urllib.request.Request(url)
        
        # Default headers (curl-like)
        default_headers = {
            'User-Agent': 'curl/7.68.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # Add custom headers if provided
        if headers:
            default_headers.update(headers)
        
        for key, value in default_headers.items():
            req.add_header(key, value)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            status_code = response.getcode()
            response_headers = dict(response.headers)
            content = response.read()
            
            # Handle gzip encoding
            if response.headers.get('Content-Encoding') == 'gzip':
                import gzip
                content = gzip.decompress(content)
            
            # Try to decode as text
            try:
                content_text = content.decode('utf-8', errors='ignore')
                is_text = True
            except:
                content_text = f"<Binary content, {len(content)} bytes>"
                is_text = False
            
            return json.dumps({
                "url": url,
                "status_code": status_code,
                "headers": response_headers,
                "content_length": len(content),
                "is_text": is_text,
                "content": content_text[:5000] + "..." if len(content_text) > 5000 else content_text,
                "truncated": len(content_text) > 5000,
                "final_url": response.geturl()
            }, indent=2)
            
    except urllib.error.HTTPError as e:
        return json.dumps({
            "url": url,
            "error": f"HTTP {e.code}: {e.reason}",
            "status_code": e.code,
            "headers": dict(e.headers) if e.headers else {}
        })
    except Exception as e:
        return json.dumps({
            "url": url,
            "error": f"Request failed: {str(e)}",
            "status": "error"
        })

def search_news_ddg(query: str = "news today") -> str:
    """
    Search for current news using DuckDuckGo HTML search.
    
    Args:
        query (str): News search query (default: "news today")
        
    Returns:
        str: JSON string with news results
    """
    # Add "news" to the query if not present
    if "news" not in query.lower():
        query = f"{query} news"
    
    return ddg_search(query, num_results=8)

def fetch_page_content(url: str) -> str:
    """
    Fetch and extract readable content from any webpage.
    
    Args:
        url (str): The URL to fetch
        
    Returns:
        str: JSON string with page content
    """
    try:
        # First get the raw content
        curl_result = json.loads(curl_get(url))
        
        if "error" in curl_result:
            return json.dumps(curl_result)
        
        content = curl_result.get("content", "")
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "No title"
        
        # Extract meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        description = desc_match.group(1) if desc_match else ""
        
        # Remove script, style, nav, footer elements
        clean_content = re.sub(r'<(script|style|nav|footer|header|aside)[^>]*>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text_content = re.sub(r'<[^>]+>', '', clean_content)
        
        # Clean up whitespace
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Extract first paragraph as summary
        paragraphs = [p.strip() for p in text_content.split('\n') if len(p.strip()) > 50]
        summary = paragraphs[0] if paragraphs else text_content[:300]
        
        return json.dumps({
            "url": url,
            "title": title,
            "description": description,
            "summary": summary[:500] + "..." if len(summary) > 500 else summary,
            "text_content": text_content[:3000] + "..." if len(text_content) > 3000 else text_content,
            "word_count": len(text_content.split()),
            "status": "success"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "url": url,
            "error": f"Failed to fetch content: {str(e)}",
            "status": "error"
        })

def deep_fetch_url(url: str, extract_links: bool = True, follow_redirects: bool = True, max_content_length: int = 50000) -> str:
    """
    Advanced URL fetching with deep content extraction for research.
    
    Args:
        url (str): The URL to fetch
        extract_links (bool): Whether to extract all links from the page
        follow_redirects (bool): Whether to follow redirects
        max_content_length (int): Maximum content length to extract
        
    Returns:
        str: JSON string with comprehensive page analysis
    """
    try:
        # Enhanced headers for better compatibility
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Get raw content with enhanced headers
        curl_result = json.loads(curl_get(url, headers))
        
        if "error" in curl_result:
            return json.dumps(curl_result)
        
        content = curl_result.get("content", "")
        response_headers = curl_result.get("headers", {})
        
        # Extract comprehensive metadata
        metadata = _extract_comprehensive_metadata(content)
        
        # Extract main content with multiple strategies
        main_content = _extract_main_content(content, max_content_length)
        
        # Extract all links if requested
        links = []
        if extract_links:
            links = _extract_all_links(content, url)
        
        # Extract structured data (JSON-LD, microdata)
        structured_data = _extract_structured_data(content)
        
        # Analyze content structure
        content_analysis = _analyze_content_structure(main_content)
        
        # Extract images and media
        media_info = _extract_media_info(content, url)
        
        return json.dumps({
            "url": url,
            "final_url": curl_result.get("final_url", url),
            "status_code": curl_result.get("status_code"),
            "content_type": response_headers.get("Content-Type", ""),
            "content_length": curl_result.get("content_length", 0),
            "metadata": metadata,
            "main_content": main_content,
            "content_analysis": content_analysis,
            "links": links[:50] if links else [],  # Limit to 50 links
            "total_links": len(links),
            "structured_data": structured_data,
            "media_info": media_info,
            "extraction_timestamp": str(hash(url) % 1000000),
            "status": "success"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "url": url,
            "error": f"Deep fetch failed: {str(e)}",
            "status": "error"
        })

def _extract_comprehensive_metadata(content):
    """Extract comprehensive metadata from HTML content"""
    metadata = {}
    
    # Title
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
    metadata['title'] = title_match.group(1).strip() if title_match else ""
    
    # Meta tags
    meta_patterns = {
        'description': r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
        'keywords': r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']',
        'author': r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']+)["\']',
        'robots': r'<meta[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']+)["\']',
        'viewport': r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\']([^"\']+)["\']',
        'charset': r'<meta[^>]*charset=["\']?([^"\'>\s]+)',
    }
    
    for key, pattern in meta_patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        metadata[key] = match.group(1) if match else ""
    
    # Open Graph tags
    og_patterns = {
        'og_title': r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']',
        'og_description': r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']',
        'og_image': r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
        'og_url': r'<meta[^>]*property=["\']og:url["\'][^>]*content=["\']([^"\']+)["\']',
        'og_type': r'<meta[^>]*property=["\']og:type["\'][^>]*content=["\']([^"\']+)["\']',
    }
    
    for key, pattern in og_patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        metadata[key] = match.group(1) if match else ""
    
    # Twitter Card tags
    twitter_patterns = {
        'twitter_card': r'<meta[^>]*name=["\']twitter:card["\'][^>]*content=["\']([^"\']+)["\']',
        'twitter_title': r'<meta[^>]*name=["\']twitter:title["\'][^>]*content=["\']([^"\']+)["\']',
        'twitter_description': r'<meta[^>]*name=["\']twitter:description["\'][^>]*content=["\']([^"\']+)["\']',
    }
    
    for key, pattern in twitter_patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        metadata[key] = match.group(1) if match else ""
    
    return metadata

def _extract_main_content(content, max_length):
    """Extract main content using multiple strategies"""
    # Remove unwanted elements
    clean_content = re.sub(r'<(script|style|nav|footer|header|aside|advertisement)[^>]*>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Try to find main content areas
    main_patterns = [
        r'<main[^>]*>(.*?)</main>',
        r'<article[^>]*>(.*?)</article>',
        r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*class="[^"]*post[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*id="[^"]*content[^"]*"[^>]*>(.*?)</div>',
        r'<div[^>]*id="[^"]*main[^"]*"[^>]*>(.*?)</div>',
    ]
    
    main_content = ""
    for pattern in main_patterns:
        match = re.search(pattern, clean_content, re.DOTALL | re.IGNORECASE)
        if match:
            main_content = match.group(1)
            break
    
    # Fallback to body content
    if not main_content:
        body_match = re.search(r'<body[^>]*>(.*?)</body>', clean_content, re.DOTALL | re.IGNORECASE)
        main_content = body_match.group(1) if body_match else clean_content
    
    # Remove remaining HTML tags
    text_content = re.sub(r'<[^>]+>', '', main_content)
    
    # Clean up whitespace and normalize
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    # Extract paragraphs
    paragraphs = [p.strip() for p in text_content.split('\n') if len(p.strip()) > 20]
    
    # Limit content length
    if len(text_content) > max_length:
        text_content = text_content[:max_length] + "..."
    
    return {
        "full_text": text_content,
        "paragraphs": paragraphs[:20],  # First 20 paragraphs
        "word_count": len(text_content.split()),
        "character_count": len(text_content),
        "summary": text_content[:500] + "..." if len(text_content) > 500 else text_content
    }

def _extract_all_links(content, base_url):
    """Extract all links from the page"""
    links = []
    
    # Extract all anchor tags
    link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>'
    matches = re.findall(link_pattern, content, re.IGNORECASE)
    
    base_domain = urllib.parse.urlparse(base_url).netloc
    
    for href, text in matches:
        # Skip empty links and javascript
        if not href or href.startswith('javascript:') or href.startswith('mailto:'):
            continue
        
        # Convert relative URLs to absolute
        if href.startswith('/'):
            href = f"https://{base_domain}{href}"
        elif not href.startswith('http'):
            href = f"https://{base_domain}/{href}"
        
        # Categorize links
        link_domain = urllib.parse.urlparse(href).netloc
        is_internal = link_domain == base_domain
        
        links.append({
            "url": href,
            "text": text.strip()[:100],  # Limit text length
            "is_internal": is_internal,
            "domain": link_domain
        })
    
    return links

def _extract_structured_data(content):
    """Extract structured data (JSON-LD, microdata)"""
    structured_data = []
    
    # Extract JSON-LD
    jsonld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    jsonld_matches = re.findall(jsonld_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for jsonld in jsonld_matches:
        try:
            data = json.loads(jsonld.strip())
            structured_data.append({
                "type": "json-ld",
                "data": data
            })
        except:
            pass
    
    return structured_data

def _analyze_content_structure(main_content):
    """Analyze the structure and quality of content"""
    text = main_content.get("full_text", "")
    
    if not text:
        return {}
    
    words = text.split()
    sentences = text.split('.')
    
    # Calculate readability metrics
    avg_words_per_sentence = len(words) / max(len(sentences), 1)
    avg_chars_per_word = sum(len(word) for word in words) / max(len(words), 1)
    
    # Count different types of content
    question_count = text.count('?')
    exclamation_count = text.count('!')
    number_count = len(re.findall(r'\d+', text))
    
    return {
        "total_words": len(words),
        "total_sentences": len(sentences),
        "avg_words_per_sentence": round(avg_words_per_sentence, 2),
        "avg_chars_per_word": round(avg_chars_per_word, 2),
        "question_count": question_count,
        "exclamation_count": exclamation_count,
        "number_count": number_count,
        "estimated_reading_time_minutes": round(len(words) / 200, 1)  # Assuming 200 WPM
    }

def _extract_media_info(content, base_url):
    """Extract information about images and media"""
    media_info = {
        "images": [],
        "videos": [],
        "audio": []
    }
    
    # Extract images
    img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*>'
    img_matches = re.findall(img_pattern, content, re.IGNORECASE)
    
    base_domain = urllib.parse.urlparse(base_url).netloc
    
    for src, alt in img_matches[:10]:  # Limit to 10 images
        if src.startswith('/'):
            src = f"https://{base_domain}{src}"
        elif not src.startswith('http'):
            src = f"https://{base_domain}/{src}"
        
        media_info["images"].append({
            "src": src,
            "alt": alt or "",
            "type": "image"
        })
    
    # Extract videos
    video_pattern = r'<video[^>]*src=["\']([^"\']+)["\'][^>]*>'
    video_matches = re.findall(video_pattern, content, re.IGNORECASE)
    
    for src in video_matches[:5]:  # Limit to 5 videos
        if src.startswith('/'):
            src = f"https://{base_domain}{src}"
        media_info["videos"].append({"src": src, "type": "video"})
    
    return media_info

def research_topic(query: str, num_sources: int = 5, deep_fetch: bool = True) -> str:
    """
    Comprehensive research function that searches and deeply analyzes multiple sources.
    
    Args:
        query (str): Research topic/query
        num_sources (int): Number of sources to analyze deeply
        deep_fetch (bool): Whether to perform deep content extraction
        
    Returns:
        str: JSON string with comprehensive research results
    """
    try:
        # Step 1: Search for sources
        search_results = json.loads(ddg_search(query, num_sources * 2))
        
        if "error" in search_results:
            return json.dumps(search_results)
        
        research_data = {
            "query": query,
            "search_results": search_results,
            "deep_analysis": [],
            "summary": {},
            "total_sources_analyzed": 0,
            "research_timestamp": str(hash(query) % 1000000),
            "status": "success"
        }
        
        # Step 2: Deep fetch top sources
        sources_analyzed = 0
        for result in search_results.get("results", [])[:num_sources]:
            if sources_analyzed >= num_sources:
                break
                
            url = result.get("url", "")
            if not url:
                continue
            
            print(f"Analyzing source {sources_analyzed + 1}: {url}")
            
            if deep_fetch:
                deep_content = json.loads(deep_fetch_url(url))
            else:
                deep_content = json.loads(fetch_page_content(url))
            
            if "error" not in deep_content:
                research_data["deep_analysis"].append({
                    "source_info": result,
                    "content_analysis": deep_content,
                    "relevance_score": _calculate_relevance_score(query, deep_content)
                })
                sources_analyzed += 1
        
        research_data["total_sources_analyzed"] = sources_analyzed
        
        # Step 3: Generate research summary
        research_data["summary"] = _generate_research_summary(research_data["deep_analysis"], query)
        
        return json.dumps(research_data, indent=2)
        
    except Exception as e:
        return json.dumps({
            "query": query,
            "error": f"Research failed: {str(e)}",
            "status": "error"
        })

def _calculate_relevance_score(query, content_data):
    """Calculate how relevant the content is to the query"""
    if "error" in content_data:
        return 0.0
    
    query_words = set(query.lower().split())
    
    # Get text content
    main_content = content_data.get("main_content", {})
    text = main_content.get("full_text", "").lower()
    title = content_data.get("metadata", {}).get("title", "").lower()
    
    # Count query word matches
    text_matches = sum(1 for word in query_words if word in text)
    title_matches = sum(1 for word in query_words if word in title)
    
    # Calculate score (title matches weighted higher)
    total_query_words = len(query_words)
    if total_query_words == 0:
        return 0.0
    
    text_score = text_matches / total_query_words
    title_score = title_matches / total_query_words
    
    # Weighted average (title 40%, content 60%)
    relevance_score = (title_score * 0.4) + (text_score * 0.6)
    
    return round(relevance_score, 3)

def _generate_research_summary(deep_analysis, query):
    """Generate a summary of the research findings"""
    if not deep_analysis:
        return {"error": "No sources analyzed"}
    
    total_words = 0
    total_sources = len(deep_analysis)
    avg_relevance = 0
    key_findings = []
    
    for analysis in deep_analysis:
        content = analysis.get("content_analysis", {})
        main_content = content.get("main_content", {})
        
        total_words += main_content.get("word_count", 0)
        avg_relevance += analysis.get("relevance_score", 0)
        
        # Extract key finding from summary
        summary = main_content.get("summary", "")
        if summary and len(summary) > 50:
            key_findings.append({
                "source": content.get("metadata", {}).get("title", "Unknown"),
                "url": content.get("url", ""),
                "finding": summary[:200] + "..." if len(summary) > 200 else summary,
                "relevance": analysis.get("relevance_score", 0)
            })
    
    avg_relevance = round(avg_relevance / max(total_sources, 1), 3)
    
    # Sort findings by relevance
    key_findings.sort(key=lambda x: x["relevance"], reverse=True)
    
    return {
        "total_sources": total_sources,
        "total_words_analyzed": total_words,
        "average_relevance_score": avg_relevance,
        "key_findings": key_findings[:5],  # Top 5 findings
        "research_quality": "high" if avg_relevance > 0.5 else "medium" if avg_relevance > 0.3 else "low"
    } 