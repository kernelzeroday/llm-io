import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

def api_request(url: str, operation: str = "get", **kwargs) -> str:
    """
    Advanced API interaction tools for REST APIs and web services.
    
    Supported operations:
    - get: GET request with query parameters
    - post: POST request with JSON/form data
    - put: PUT request for updates
    - delete: DELETE request
    - json_parse: Parse and validate JSON data
    - json_query: Query JSON data with path notation
    - headers_analyze: Analyze HTTP headers
    - api_test: Test API endpoint availability
    
    Args:
        url (str): The API endpoint URL
        operation (str): The operation to perform
        **kwargs: Additional parameters (data, headers, auth, etc.)
        
    Returns:
        str: JSON string with API response and analysis
    """
    operations = {
        'get': _api_get,
        'post': _api_post,
        'put': _api_put,
        'delete': _api_delete,
        'json_parse': _json_parse,
        'json_query': _json_query,
        'headers_analyze': _headers_analyze,
        'api_test': _api_test
    }
    
    if operation not in operations:
        available_ops = list(operations.keys())
        return json.dumps({
            "error": f"Unknown operation '{operation}'",
            "available_operations": available_ops
        })
    
    try:
        result = operations[operation](url, **kwargs)
        return result
    except Exception as e:
        return json.dumps({
            "error": f"API operation failed: {str(e)}",
            "url": url,
            "operation": operation
        })

def _api_get(url: str, **kwargs) -> str:
    """Perform GET request with query parameters"""
    params = kwargs.get('params', {})
    headers = kwargs.get('headers', {})
    timeout = kwargs.get('timeout', 10)
    auth = kwargs.get('auth', None)
    
    # Add query parameters to URL
    if params:
        query_string = urllib.parse.urlencode(params)
        separator = '&' if '?' in url else '?'
        url = f"{url}{separator}{query_string}"
    
    # Set default headers
    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'LLM-Agent/1.0 (API Tools)'
    if 'Accept' not in headers:
        headers['Accept'] = 'application/json, text/plain, */*'
    
    # Add authentication
    if auth:
        if isinstance(auth, dict) and 'bearer' in auth:
            headers['Authorization'] = f"Bearer {auth['bearer']}"
        elif isinstance(auth, dict) and 'api_key' in auth:
            headers['X-API-Key'] = auth['api_key']
    
    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            response_headers = dict(response.headers)
            content = response.read().decode('utf-8')
            
            # Try to parse as JSON
            try:
                json_data = json.loads(content)
                is_json = True
            except json.JSONDecodeError:
                json_data = None
                is_json = False
            
            return json.dumps({
                "status_code": status_code,
                "url": response.geturl(),
                "headers": response_headers,
                "is_json": is_json,
                "data": json_data if is_json else content[:2000],
                "content_length": len(content),
                "request_params": params,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
            
    except urllib.error.HTTPError as e:
        error_content = e.read().decode('utf-8') if e.fp else ""
        return json.dumps({
            "error": f"HTTP {e.code}: {e.reason}",
            "status_code": e.code,
            "url": url,
            "error_content": error_content[:1000],
            "headers": dict(e.headers) if e.headers else {}
        })

def _api_post(url: str, **kwargs) -> str:
    """Perform POST request with JSON or form data"""
    data = kwargs.get('data', {})
    headers = kwargs.get('headers', {})
    timeout = kwargs.get('timeout', 10)
    content_type = kwargs.get('content_type', 'json')
    auth = kwargs.get('auth', None)
    
    # Set default headers
    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'LLM-Agent/1.0 (API Tools)'
    
    # Prepare data based on content type
    if content_type == 'json':
        headers['Content-Type'] = 'application/json'
        post_data = json.dumps(data).encode('utf-8')
    elif content_type == 'form':
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        post_data = urllib.parse.urlencode(data).encode('utf-8')
    else:
        post_data = str(data).encode('utf-8')
    
    # Add authentication
    if auth:
        if isinstance(auth, dict) and 'bearer' in auth:
            headers['Authorization'] = f"Bearer {auth['bearer']}"
        elif isinstance(auth, dict) and 'api_key' in auth:
            headers['X-API-Key'] = auth['api_key']
    
    try:
        req = urllib.request.Request(url, data=post_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            response_headers = dict(response.headers)
            content = response.read().decode('utf-8')
            
            # Try to parse as JSON
            try:
                json_data = json.loads(content)
                is_json = True
            except json.JSONDecodeError:
                json_data = None
                is_json = False
            
            return json.dumps({
                "status_code": status_code,
                "url": response.geturl(),
                "headers": response_headers,
                "is_json": is_json,
                "data": json_data if is_json else content[:2000],
                "request_data": data,
                "content_type": content_type,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
            
    except urllib.error.HTTPError as e:
        error_content = e.read().decode('utf-8') if e.fp else ""
        return json.dumps({
            "error": f"HTTP {e.code}: {e.reason}",
            "status_code": e.code,
            "url": url,
            "error_content": error_content[:1000],
            "request_data": data
        })

def _api_put(url: str, **kwargs) -> str:
    """Perform PUT request for updates"""
    kwargs['method'] = 'PUT'
    return _api_post(url, **kwargs)  # PUT is similar to POST

def _api_delete(url: str, **kwargs) -> str:
    """Perform DELETE request"""
    headers = kwargs.get('headers', {})
    timeout = kwargs.get('timeout', 10)
    auth = kwargs.get('auth', None)
    
    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'LLM-Agent/1.0 (API Tools)'
    
    # Add authentication
    if auth:
        if isinstance(auth, dict) and 'bearer' in auth:
            headers['Authorization'] = f"Bearer {auth['bearer']}"
        elif isinstance(auth, dict) and 'api_key' in auth:
            headers['X-API-Key'] = auth['api_key']
    
    try:
        req = urllib.request.Request(url, headers=headers, method='DELETE')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            response_headers = dict(response.headers)
            content = response.read().decode('utf-8')
            
            return json.dumps({
                "status_code": status_code,
                "url": response.geturl(),
                "headers": response_headers,
                "content": content[:1000],
                "timestamp": datetime.now().isoformat()
            }, indent=2)
            
    except urllib.error.HTTPError as e:
        return json.dumps({
            "error": f"HTTP {e.code}: {e.reason}",
            "status_code": e.code,
            "url": url
        })

def _json_parse(data: str, **kwargs) -> str:
    """Parse and validate JSON data"""
    try:
        parsed_data = json.loads(data)
        
        # Analyze the JSON structure
        def analyze_structure(obj, path="root"):
            if isinstance(obj, dict):
                return {
                    "type": "object",
                    "keys": list(obj.keys()),
                    "key_count": len(obj.keys()),
                    "nested_objects": sum(1 for v in obj.values() if isinstance(v, dict)),
                    "nested_arrays": sum(1 for v in obj.values() if isinstance(v, list))
                }
            elif isinstance(obj, list):
                return {
                    "type": "array",
                    "length": len(obj),
                    "item_types": list(set(type(item).__name__ for item in obj)),
                    "has_objects": any(isinstance(item, dict) for item in obj),
                    "has_arrays": any(isinstance(item, list) for item in obj)
                }
            else:
                return {
                    "type": type(obj).__name__,
                    "value": str(obj)[:100]
                }
        
        structure = analyze_structure(parsed_data)
        
        return json.dumps({
            "valid_json": True,
            "parsed_data": parsed_data,
            "structure_analysis": structure,
            "original_size": len(data),
            "parsed_at": datetime.now().isoformat()
        }, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "valid_json": False,
            "error": str(e),
            "error_line": e.lineno if hasattr(e, 'lineno') else None,
            "error_column": e.colno if hasattr(e, 'colno') else None,
            "original_data": data[:500] + "..." if len(data) > 500 else data
        })

def _json_query(data: str, query_path: str = "", **kwargs) -> str:
    """Query JSON data using dot notation path"""
    try:
        parsed_data = json.loads(data)
        
        if not query_path:
            return json.dumps({
                "query_path": "root",
                "result": parsed_data,
                "result_type": type(parsed_data).__name__
            }, indent=2)
        
        # Navigate through the path
        current = parsed_data
        path_parts = query_path.split('.')
        
        for part in path_parts:
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    return json.dumps({
                        "error": f"Key '{part}' not found in object",
                        "available_keys": list(current.keys()) if isinstance(current, dict) else None,
                        "query_path": query_path
                    })
            elif isinstance(current, list):
                try:
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return json.dumps({
                            "error": f"Index {index} out of range",
                            "array_length": len(current),
                            "query_path": query_path
                        })
                except ValueError:
                    return json.dumps({
                        "error": f"Invalid array index '{part}'",
                        "query_path": query_path
                    })
            else:
                return json.dumps({
                    "error": f"Cannot navigate further from {type(current).__name__}",
                    "query_path": query_path,
                    "stopped_at": part
                })
        
        return json.dumps({
            "query_path": query_path,
            "result": current,
            "result_type": type(current).__name__,
            "success": True
        }, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Invalid JSON: {str(e)}",
            "query_path": query_path
        })

def _headers_analyze(url: str, **kwargs) -> str:
    """Analyze HTTP headers from a response"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'LLM-Agent/1.0 (Header Analyzer)')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            headers = dict(response.headers)
            
            # Analyze security headers
            security_headers = {
                'Content-Security-Policy': headers.get('Content-Security-Policy'),
                'X-Frame-Options': headers.get('X-Frame-Options'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
                'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
                'X-XSS-Protection': headers.get('X-XSS-Protection')
            }
            
            # Analyze caching headers
            caching_headers = {
                'Cache-Control': headers.get('Cache-Control'),
                'ETag': headers.get('ETag'),
                'Last-Modified': headers.get('Last-Modified'),
                'Expires': headers.get('Expires')
            }
            
            return json.dumps({
                "url": url,
                "status_code": response.getcode(),
                "all_headers": headers,
                "security_headers": {k: v for k, v in security_headers.items() if v},
                "caching_headers": {k: v for k, v in caching_headers.items() if v},
                "server_info": {
                    "server": headers.get('Server'),
                    "content_type": headers.get('Content-Type'),
                    "content_length": headers.get('Content-Length'),
                    "powered_by": headers.get('X-Powered-By')
                },
                "security_score": len([v for v in security_headers.values() if v]),
                "analyzed_at": datetime.now().isoformat()
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Header analysis failed: {str(e)}",
            "url": url
        })

def _api_test(url: str, **kwargs) -> str:
    """Test API endpoint availability and basic functionality"""
    endpoints = kwargs.get('endpoints', [])
    if not endpoints:
        endpoints = ['/', '/health', '/status', '/api', '/api/v1']
    
    base_url = url.rstrip('/')
    results = []
    
    for endpoint in endpoints:
        test_url = f"{base_url}{endpoint}"
        try:
            req = urllib.request.Request(test_url, method='GET')
            req.add_header('User-Agent', 'LLM-Agent/1.0 (API Tester)')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                status_code = response.getcode()
                content_type = response.headers.get('Content-Type', 'unknown')
                content = response.read(1000).decode('utf-8', errors='ignore')
                
                results.append({
                    "endpoint": endpoint,
                    "url": test_url,
                    "status": "accessible",
                    "status_code": status_code,
                    "content_type": content_type,
                    "response_preview": content[:200] + "..." if len(content) > 200 else content
                })
                
        except urllib.error.HTTPError as e:
            results.append({
                "endpoint": endpoint,
                "url": test_url,
                "status": "error",
                "status_code": e.code,
                "error": f"HTTP {e.code}: {e.reason}"
            })
        except Exception as e:
            results.append({
                "endpoint": endpoint,
                "url": test_url,
                "status": "failed",
                "error": str(e)
            })
    
    accessible_count = len([r for r in results if r["status"] == "accessible"])
    
    return json.dumps({
        "base_url": base_url,
        "total_endpoints_tested": len(endpoints),
        "accessible_endpoints": accessible_count,
        "success_rate": f"{(accessible_count/len(endpoints)*100):.1f}%",
        "results": results,
        "tested_at": datetime.now().isoformat()
    }, indent=2) 