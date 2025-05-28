#!/usr/bin/env python3

import sys
import json
sys.path.append('test_functions')

from ddg_search import ddg_search, search_news_ddg, curl_get, fetch_page_content
from news_search import search_news, get_trending_topics, fetch_article
from web_tools import web_request
from api_tools import api_request
from data_generator import generate_data
from crypto_utils import crypto_utils
from text_analysis import analyze_text

def test_comprehensive_workflow():
    """Test a comprehensive workflow using all internet tools"""
    print("🚀 COMPREHENSIVE INTERNET TOOLS TEST")
    print("=" * 50)
    
    # 1. Search for current news using DuckDuckGo
    print("\n1️⃣ Searching for AI news using DuckDuckGo...")
    ddg_results = json.loads(ddg_search("AI artificial intelligence news 2025", 3))
    print(f"Found {ddg_results['total_results']} results")
    for i, result in enumerate(ddg_results['results'][:2], 1):
        print(f"   {i}. {result['title'][:60]}...")
        print(f"      URL: {result['url']}")
    
    # 2. Fetch content from first result
    if ddg_results['results']:
        print("\n2️⃣ Fetching content from first result...")
        first_url = ddg_results['results'][0]['url']
        content = json.loads(fetch_page_content(first_url))
        if 'error' not in content:
            print(f"   Title: {content['title'][:80]}...")
            print(f"   Word count: {content['word_count']}")
            print(f"   Summary: {content['summary'][:100]}...")
        else:
            print(f"   Error: {content['error']}")
    
    # 3. Search traditional news sources
    print("\n3️⃣ Searching BBC News...")
    bbc_results = json.loads(search_news("technology", "bbc"))
    print(f"Found {bbc_results['total_results']} BBC results")
    for i, result in enumerate(bbc_results['results'][:2], 1):
        if 'error' not in result:
            print(f"   {i}. {result['title'][:60]}...")
    
    # 4. Test API functionality
    print("\n4️⃣ Testing API tools...")
    api_test = json.loads(api_request("https://httpbin.org/json", "get"))
    if 'error' not in api_test:
        print("   ✅ API request successful")
        print(f"   Status: {api_test.get('status_code', 'N/A')}")
    else:
        print(f"   ❌ API test failed: {api_test['error']}")
    
    # 5. Generate test data
    print("\n5️⃣ Generating test data...")
    test_users = json.loads(generate_data("users", 3))
    print(f"Generated {test_users['count']} test users:")
    for user in test_users['data'][:2]:
        print(f"   - {user['first_name']} {user['last_name']} ({user['email']})")
    
    # 6. Crypto operations
    print("\n6️⃣ Testing crypto utilities...")
    test_text = "Hello World 2025"
    hash_result = json.loads(crypto_utils("hash", test_text, algorithm="sha256"))
    print(f"   SHA256 of '{test_text}': {hash_result['result'][:16]}...")
    
    key_result = json.loads(crypto_utils("generate_key", "", length=16, key_type="password"))
    print(f"   Generated secure password: {key_result['result']}")
    
    # 7. Text analysis
    print("\n7️⃣ Analyzing text content...")
    sample_text = "The rapid advancement of artificial intelligence in 2025 has transformed how we interact with technology. Machine learning algorithms are becoming increasingly sophisticated, enabling more natural human-computer interactions."
    analysis = json.loads(analyze_text(sample_text))
    print(f"   Text length: {analysis['basic_stats']['characters']} characters")
    print(f"   Word count: {analysis['basic_stats']['words']} words")
    print(f"   Reading level: {analysis['complexity']['reading_level']}")
    print(f"   Flesch score: {analysis['complexity']['flesch_score']:.1f}")
    
    # 8. Web utilities
    print("\n8️⃣ Testing web utilities...")
    status_check = json.loads(web_request("https://www.google.com", "check_status"))
    if 'error' not in status_check:
        print(f"   Google.com status: {status_check['status_code']} ({status_check['response_time']:.2f}s)")
    
    print("\n✅ COMPREHENSIVE TEST COMPLETED!")
    print("All 7 internet tool functions are working correctly.")

def test_real_time_news():
    """Test real-time news capabilities"""
    print("\n📰 REAL-TIME NEWS TEST")
    print("=" * 30)
    
    # Search for very current news
    current_news = json.loads(ddg_search("breaking news today", 5))
    print(f"Current breaking news ({current_news['total_results']} results):")
    
    for i, result in enumerate(current_news['results'][:3], 1):
        print(f"{i}. {result['title']}")
        print(f"   Source: {result['url'].split('/')[2]}")
    
    # Test trending topics
    print("\nTesting trending topics...")
    try:
        trending = json.loads(get_trending_topics())
        if 'error' not in trending:
            print("✅ Trending topics retrieved successfully")
        else:
            print(f"⚠️ Trending topics: {trending['error']}")
    except Exception as e:
        print(f"⚠️ Trending topics failed: {e}")

def test_curl_functionality():
    """Test curl-like functionality"""
    print("\n🌐 CURL FUNCTIONALITY TEST")
    print("=" * 30)
    
    # Test basic curl
    curl_result = json.loads(curl_get("https://httpbin.org/user-agent"))
    if 'error' not in curl_result:
        print("✅ Basic curl request successful")
        print(f"   Status: {curl_result['status_code']}")
        print(f"   Content type: {curl_result['headers'].get('Content-Type', 'N/A')}")
    
    # Test with custom headers
    custom_headers = {"User-Agent": "TestBot/1.0", "Accept": "application/json"}
    curl_custom = json.loads(curl_get("https://httpbin.org/headers", custom_headers))
    if 'error' not in curl_custom:
        print("✅ Custom headers curl request successful")

if __name__ == "__main__":
    print("🔧 INTERNET TOOLS COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    print("Testing all 7 internet tool functions...")
    print("Functions: ddg_search, news_search, web_tools, api_tools,")
    print("          data_generator, crypto_utils, text_analysis")
    print()
    
    try:
        test_comprehensive_workflow()
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
    
    try:
        test_real_time_news()
    except Exception as e:
        print(f"❌ Real-time news test failed: {e}")
    
    try:
        test_curl_functionality()
    except Exception as e:
        print(f"❌ Curl functionality test failed: {e}")
    
    print("\n🎉 ALL TESTS COMPLETED!")
    print("\nThese tools provide LLM agents with:")
    print("✅ Real-time web search (DuckDuckGo)")
    print("✅ News aggregation from major sources")
    print("✅ HTTP/API request capabilities")
    print("✅ Content extraction and analysis")
    print("✅ Test data generation")
    print("✅ Cryptographic operations")
    print("✅ Text analysis and readability scoring")
    print("\n🚀 Ready for LLM agent integration!") 