import json
import urllib.request
import urllib.parse
import urllib.error
import re
from datetime import datetime

def web_request(url: str, method: str = "GET", **kwargs) -> str:
    """
    Perform HTTP requests and web operations.
    
    Supported operations:
    - GET: Fetch content from URL
    - HEAD: Get headers only
    - POST: Send data to URL
    - parse_url: Parse URL components
    - extract_links: Extract all links from HTML
    - extract_text: Extract clean text from HTML
    - check_status: Check if URL is accessible
    
    Args:
        url (str): The URL to request
        method (str): HTTP method (GET, HEAD, POST, parse_url, extract_links, extract_text, check_status)
        **kwargs: Additional parameters (data, headers, timeout, etc.)
        
    Returns:
        str: JSON string with request results
    """
    try:
        if method.lower() == "parse_url":
            return _parse_url(url)
        elif method.lower() == "extract_links":
            return _extract_links(url, **kwargs)
        elif method.lower() == "extract_text":
            return _extract_text(url, **kwargs)
        elif method.lower() == "check_status":
            return _check_status(url, **kwargs)
        else:
            return _http_request(url, method, **kwargs)
    except Exception as e:
        return json.dumps({
            "error": f"Request failed: {str(e)}",
            "url": url,
            "method": method
        })

def _http_request(url: str, method: str = "GET", **kwargs) -> str:
    """Perform HTTP request"""
    timeout = kwargs.get('timeout', 10)
    headers = kwargs.get('headers', {})
    data = kwargs.get('data', None)
    max_size = kwargs.get('max_size', 1024 * 1024)  # 1MB default
    
    # Add user agent
    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'LLM-Agent/1.0 (Web Tools)'
    
    try:
        # Prepare request
        if data and method.upper() == "POST":
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data).encode('utf-8')
            elif isinstance(data, str):
                data = data.encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
        
        # Make request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            # Get response info
            status_code = response.getcode()
            response_headers = dict(response.headers)
            
            # Read content with size limit
            content = response.read(max_size)
            content_length = len(content)
            
            # Try to decode as text
            try:
                content_text = content.decode('utf-8')
                is_text = True
            except UnicodeDecodeError:
                content_text = f"<Binary content, {content_length} bytes>"
                is_text = False
            
            return json.dumps({
                "status_code": status_code,
                "url": response.geturl(),
                "headers": response_headers,
                "content_length": content_length,
                "is_text": is_text,
                "content": content_text[:5000] + "..." if len(content_text) > 5000 else content_text,
                "truncated": len(content_text) > 5000,
                "request_method": method.upper(),
                "timestamp": datetime.now().isoformat()
            }, indent=2)
            
    except urllib.error.HTTPError as e:
        return json.dumps({
            "error": f"HTTP Error {e.code}: {e.reason}",
            "status_code": e.code,
            "url": url,
            "headers": dict(e.headers) if e.headers else {}
        })
    except urllib.error.URLError as e:
        return json.dumps({
            "error": f"URL Error: {e.reason}",
            "url": url
        })

def _parse_url(url: str) -> str:
    """Parse URL into components"""
    try:
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)
        
        return json.dumps({
            "original_url": url,
            "scheme": parsed.scheme,
            "netloc": parsed.netloc,
            "hostname": parsed.hostname,
            "port": parsed.port,
            "path": parsed.path,
            "params": parsed.params,
            "query": parsed.query,
            "fragment": parsed.fragment,
            "query_parameters": query_params,
            "is_valid": bool(parsed.scheme and parsed.netloc)
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"URL parsing failed: {str(e)}"})

def _extract_links(url: str, **kwargs) -> str:
    """Extract all links from HTML page"""
    try:
        # First get the page content
        response_data = json.loads(_http_request(url, "GET", **kwargs))
        
        if "error" in response_data:
            return json.dumps(response_data)
        
        content = response_data.get("content", "")
        
        # Extract links using regex
        link_patterns = [
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>',  # <a href="url">text</a>
            r'<link[^>]+href=["\']([^"\']+)["\'][^>]*>',  # <link href="url">
            r'src=["\']([^"\']+)["\']',  # src="url"
        ]
        
        all_links = []
        base_url = f"{urllib.parse.urlparse(url).scheme}://{urllib.parse.urlparse(url).netloc}"
        
        for pattern in link_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    link_url, link_text = match[0], match[1] if len(match) > 1 else ""
                else:
                    link_url, link_text = match, ""
                
                # Convert relative URLs to absolute
                if link_url.startswith('/'):
                    link_url = base_url + link_url
                elif not link_url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                    continue
                
                all_links.append({
                    "url": link_url,
                    "text": link_text.strip(),
                    "type": "internal" if base_url in link_url else "external"
                })
        
        # Remove duplicates
        unique_links = []
        seen_urls = set()
        for link in all_links:
            if link["url"] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link["url"])
        
        return json.dumps({
            "source_url": url,
            "total_links": len(unique_links),
            "internal_links": len([l for l in unique_links if l["type"] == "internal"]),
            "external_links": len([l for l in unique_links if l["type"] == "external"]),
            "links": unique_links[:50],  # Limit to first 50
            "truncated": len(unique_links) > 50
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Link extraction failed: {str(e)}"})

def _extract_text(url: str, **kwargs) -> str:
    """Extract clean text content from HTML page"""
    try:
        # Get page content
        response_data = json.loads(_http_request(url, "GET", **kwargs))
        
        if "error" in response_data:
            return json.dumps(response_data)
        
        content = response_data.get("content", "")
        
        # Remove HTML tags and extract text
        # Remove script and style elements
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        # Extract title
        original_content = response_data.get("content", "")
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', original_content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "No title found"
        
        # Basic text statistics
        word_count = len(content.split())
        char_count = len(content)
        
        return json.dumps({
            "source_url": url,
            "title": title,
            "text_content": content[:3000] + "..." if len(content) > 3000 else content,
            "word_count": word_count,
            "character_count": char_count,
            "truncated": len(content) > 3000,
            "extracted_at": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Text extraction failed: {str(e)}"})

def _check_status(url: str, **kwargs) -> str:
    """Check if URL is accessible and get basic info"""
    timeout = kwargs.get('timeout', 5)
    
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'LLM-Agent/1.0 (Status Checker)')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.dumps({
                "url": url,
                "status": "accessible",
                "status_code": response.getcode(),
                "content_type": response.headers.get('Content-Type', 'unknown'),
                "content_length": response.headers.get('Content-Length', 'unknown'),
                "server": response.headers.get('Server', 'unknown'),
                "last_modified": response.headers.get('Last-Modified', 'unknown'),
                "response_time_ms": "< 5000",  # Approximate since we don't measure precisely
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
    except urllib.error.URLError as e:
        return json.dumps({
            "url": url,
            "status": "unreachable",
            "error": str(e.reason)
        })
    except Exception as e:
        return json.dumps({
            "url": url,
            "status": "failed",
            "error": str(e)
        }) 