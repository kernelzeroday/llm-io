#!/usr/bin/env python3

import sys
import json
sys.path.append('test_functions')

from ddg_search import ddg_search, deep_fetch_url, research_topic, fetch_page_content

def test_deep_fetch():
    """Test the deep URL fetching capability"""
    print("🔍 TESTING DEEP URL FETCHING")
    print("=" * 40)
    
    # Test with a news article
    test_url = "https://www.bbc.com/news"
    print(f"Deep fetching: {test_url}")
    
    result = json.loads(deep_fetch_url(test_url))
    
    if "error" not in result:
        print("✅ Deep fetch successful!")
        print(f"   Title: {result['metadata']['title'][:80]}...")
        print(f"   Content length: {result['content_length']} bytes")
        print(f"   Word count: {result['main_content']['word_count']}")
        print(f"   Total links found: {result['total_links']}")
        print(f"   Images found: {len(result['media_info']['images'])}")
        print(f"   Reading time: {result['content_analysis']['estimated_reading_time_minutes']} minutes")
        
        # Show some extracted links
        if result['links']:
            print(f"\n   Sample links:")
            for i, link in enumerate(result['links'][:3], 1):
                print(f"     {i}. {link['text'][:50]}... -> {link['url'][:60]}...")
        
        # Show metadata
        metadata = result['metadata']
        if metadata.get('description'):
            print(f"\n   Description: {metadata['description'][:100]}...")
        
    else:
        print(f"❌ Deep fetch failed: {result['error']}")
    
    print()

def test_research_topic():
    """Test the comprehensive research function"""
    print("🎓 TESTING COMPREHENSIVE RESEARCH")
    print("=" * 40)
    
    research_query = "artificial intelligence 2025 developments"
    print(f"Researching: {research_query}")
    print("This will search, fetch, and analyze multiple sources...")
    
    result = json.loads(research_topic(research_query, num_sources=3, deep_fetch=True))
    
    if "error" not in result:
        print("✅ Research completed successfully!")
        
        # Show search results
        search_results = result['search_results']
        print(f"\n📊 SEARCH PHASE:")
        print(f"   Found {search_results['total_results']} initial results")
        
        # Show deep analysis
        deep_analysis = result['deep_analysis']
        print(f"\n🔬 DEEP ANALYSIS PHASE:")
        print(f"   Analyzed {result['total_sources_analyzed']} sources in detail")
        
        for i, analysis in enumerate(deep_analysis, 1):
            source_info = analysis['source_info']
            content_analysis = analysis['content_analysis']
            relevance = analysis['relevance_score']
            
            print(f"\n   Source {i}: {source_info['title'][:60]}...")
            print(f"     URL: {source_info['url']}")
            print(f"     Relevance Score: {relevance}")
            print(f"     Word Count: {content_analysis['main_content']['word_count']}")
            print(f"     Summary: {content_analysis['main_content']['summary'][:100]}...")
        
        # Show research summary
        summary = result['summary']
        print(f"\n📋 RESEARCH SUMMARY:")
        print(f"   Total sources: {summary['total_sources']}")
        print(f"   Total words analyzed: {summary['total_words_analyzed']}")
        print(f"   Average relevance: {summary['average_relevance_score']}")
        print(f"   Research quality: {summary['research_quality']}")
        
        # Show key findings
        if summary.get('key_findings'):
            print(f"\n🔑 KEY FINDINGS:")
            for i, finding in enumerate(summary['key_findings'], 1):
                print(f"   {i}. {finding['source']} (relevance: {finding['relevance']})")
                print(f"      {finding['finding'][:150]}...")
                print()
    
    else:
        print(f"❌ Research failed: {result['error']}")

def test_compare_fetch_methods():
    """Compare regular fetch vs deep fetch"""
    print("⚖️  COMPARING FETCH METHODS")
    print("=" * 40)
    
    test_url = "https://www.reuters.com/technology/"
    print(f"Testing URL: {test_url}")
    
    # Regular fetch
    print("\n1. Regular fetch:")
    regular_result = json.loads(fetch_page_content(test_url))
    if "error" not in regular_result:
        print(f"   Word count: {regular_result['word_count']}")
        print(f"   Summary: {regular_result['summary'][:100]}...")
    else:
        print(f"   Error: {regular_result['error']}")
    
    # Deep fetch
    print("\n2. Deep fetch:")
    deep_result = json.loads(deep_fetch_url(test_url, extract_links=True))
    if "error" not in deep_result:
        print(f"   Word count: {deep_result['main_content']['word_count']}")
        print(f"   Links extracted: {deep_result['total_links']}")
        print(f"   Images found: {len(deep_result['media_info']['images'])}")
        print(f"   Structured data: {len(deep_result['structured_data'])} items")
        print(f"   Reading time: {deep_result['content_analysis']['estimated_reading_time_minutes']} min")
        print(f"   Summary: {deep_result['main_content']['summary'][:100]}...")
        
        # Show content analysis
        analysis = deep_result['content_analysis']
        print(f"\n   Content Analysis:")
        print(f"     Avg words/sentence: {analysis['avg_words_per_sentence']}")
        print(f"     Questions found: {analysis['question_count']}")
        print(f"     Numbers found: {analysis['number_count']}")
    else:
        print(f"   Error: {deep_result['error']}")

def test_link_extraction():
    """Test link extraction from a page"""
    print("\n🔗 TESTING LINK EXTRACTION")
    print("=" * 40)
    
    test_url = "https://news.ycombinator.com"
    print(f"Extracting links from: {test_url}")
    
    result = json.loads(deep_fetch_url(test_url, extract_links=True))
    
    if "error" not in result:
        links = result['links']
        print(f"✅ Found {len(links)} links")
        
        # Categorize links
        internal_links = [l for l in links if l['is_internal']]
        external_links = [l for l in links if not l['is_internal']]
        
        print(f"   Internal links: {len(internal_links)}")
        print(f"   External links: {len(external_links)}")
        
        # Show sample external links
        print(f"\n   Sample external links:")
        for i, link in enumerate(external_links[:5], 1):
            print(f"     {i}. {link['text'][:40]}... -> {link['domain']}")
    
    else:
        print(f"❌ Link extraction failed: {result['error']}")

if __name__ == "__main__":
    print("🚀 DEEP RESEARCH & URL FETCHING TEST SUITE")
    print("=" * 50)
    print("Testing enhanced URL fetching and research capabilities...")
    print()
    
    try:
        test_deep_fetch()
    except Exception as e:
        print(f"❌ Deep fetch test failed: {e}\n")
    
    try:
        test_compare_fetch_methods()
    except Exception as e:
        print(f"❌ Comparison test failed: {e}\n")
    
    try:
        test_link_extraction()
    except Exception as e:
        print(f"❌ Link extraction test failed: {e}\n")
    
    try:
        test_research_topic()
    except Exception as e:
        print(f"❌ Research test failed: {e}\n")
    
    print("\n🎉 DEEP RESEARCH TESTING COMPLETED!")
    print("\nNew capabilities added:")
    print("✅ Deep URL content extraction with metadata")
    print("✅ Comprehensive link extraction and categorization")
    print("✅ Media detection (images, videos)")
    print("✅ Structured data extraction (JSON-LD)")
    print("✅ Content quality analysis and readability metrics")
    print("✅ Multi-source research with relevance scoring")
    print("✅ Automatic research summarization")
    print("\n🔬 Perfect for deep research and content analysis!") 