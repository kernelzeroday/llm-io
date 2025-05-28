#!/usr/bin/env python3

import sys
sys.path.append('test_functions')

from ddg_search import ddg_search, search_news_ddg, curl_get, fetch_page_content

def test_ddg_search():
    print("=== Testing ddg_search function ===")
    result = ddg_search('news today')
    print(result)
    print()

def test_news_search():
    print("=== Testing search_news_ddg function ===")
    result = search_news_ddg('technology')
    print(result)
    print()

def test_curl_get():
    print("=== Testing curl_get function ===")
    result = curl_get('https://html.duckduckgo.com/html/?q=news')
    print(result[:1000] + "..." if len(result) > 1000 else result)
    print()

def test_fetch_content():
    print("=== Testing fetch_page_content function ===")
    result = fetch_page_content('https://www.bbc.com/news')
    print(result)
    print()

if __name__ == "__main__":
    print("Testing DuckDuckGo search functions...\n")
    
    try:
        test_ddg_search()
    except Exception as e:
        print(f"ddg_search failed: {e}\n")
    
    try:
        test_news_search()
    except Exception as e:
        print(f"search_news_ddg failed: {e}\n")
    
    try:
        test_curl_get()
    except Exception as e:
        print(f"curl_get failed: {e}\n")
    
    try:
        test_fetch_content()
    except Exception as e:
        print(f"fetch_page_content failed: {e}\n")
    
    print("Testing complete!") 