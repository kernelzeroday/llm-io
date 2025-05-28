#!/usr/bin/env python3

import sys
sys.path.append('test_functions')

from news_search import search_news, get_trending_topics, fetch_article
from web_search import web_search, fetch_url, check_url_status

def test_news_search():
    print("=== Testing search_news function ===")
    result = search_news('technology', 'bbc')
    print(result)
    print()

def test_trending_topics():
    print("=== Testing get_trending_topics function ===")
    result = get_trending_topics()
    print(result)
    print()

def test_web_search():
    print("=== Testing web_search function ===")
    result = web_search('python programming')
    print(result)
    print()

def test_url_check():
    print("=== Testing check_url_status function ===")
    result = check_url_status('https://www.google.com')
    print(result)
    print()

def test_fetch_url():
    print("=== Testing fetch_url function ===")
    result = fetch_url('https://httpbin.org/html')
    print(result)
    print()

if __name__ == "__main__":
    print("Testing all web/news functions...\n")
    
    try:
        test_web_search()
    except Exception as e:
        print(f"web_search failed: {e}\n")
    
    try:
        test_news_search()
    except Exception as e:
        print(f"search_news failed: {e}\n")
    
    try:
        test_trending_topics()
    except Exception as e:
        print(f"get_trending_topics failed: {e}\n")
    
    try:
        test_url_check()
    except Exception as e:
        print(f"check_url_status failed: {e}\n")
    
    try:
        test_fetch_url()
    except Exception as e:
        print(f"fetch_url failed: {e}\n")
    
    print("Testing complete!") 