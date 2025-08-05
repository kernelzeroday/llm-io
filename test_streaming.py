#!/usr/bin/env python3
"""
Test script to verify real-time streaming functionality
"""
import os
import sys
import time
import llm

def test_streaming():
    """Test streaming functionality"""
    print("Testing real-time streaming...")
    
    # Check if API key is set
    api_key = os.environ.get('IOINTELLIGENCE_API_KEY')
    if not api_key:
        print("ERROR: IOINTELLIGENCE_API_KEY environment variable not set")
        print("Please set your API key: export IOINTELLIGENCE_API_KEY='your-key-here'")
        return False
    
    try:
        # Get a streaming-capable model
        model = llm.get_model("llama-3.3-70b")
        print(f"Using model: {model}")
        
        # Test streaming with a simple prompt
        print("\nSending streaming request...")
        start_time = time.time()
        
        response = model.prompt(
            "Count from 1 to 10, with each number on a new line.",
            stream=True
        )
        
        print("Streaming response (chunks should appear in real-time):")
        print("-" * 50)
        
        char_count = 0
        chunk_count = 0
        
        for chunk in response:
            if chunk:
                print(chunk, end="", flush=True)
                char_count += len(chunk)
                chunk_count += 1
                
        end_time = time.time()
        print("\n" + "-" * 50)
        print(f"Total characters: {char_count}")
        print(f"Total chunks: {chunk_count}")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        print("✅ Streaming test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_streaming()
