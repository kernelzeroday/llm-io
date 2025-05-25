#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

# Set API key
os.environ['IOINTELLIGENCE_API_KEY'] = 'io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImYwMDdkNjM0LWVjMzctNTA2ZS1iNmI4LTZmNzAxMjk3OTBlMCIsImV4cCI6NDg5NTMwNzY1NH0.A78xxXbsoIlPXQDzkETLd-oAh4MmcmIZwK2MqMTwxsYP01jnh6eP1hQGAKSoHkEbSWy2LOSQY1JjZAn6kxgOhA'

# Import LLM after setting the API key
import llm

def test_streaming():
    print("Testing IO Intelligence streaming with timestamps...")
    print("=" * 60)
    
    # Get the model
    model = llm.get_model("llama-3.3-70b")
    
    # Create a prompt
    prompt = "Write a short story about a robot learning to paint, with vivid descriptions"
    
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Starting streaming test...")
    print(f"Prompt: {prompt}")
    print("-" * 60)
    
    start_time = time.time()
    chunk_count = 0
    
    try:
        # Execute with streaming
        response = model.prompt(prompt, stream=True)
        
        for chunk in response:
            chunk_count += 1
            elapsed = time.time() - start_time
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            # Print each chunk with timestamp
            print(f"[{timestamp}] (+{elapsed:.2f}s) Chunk {chunk_count}: {repr(chunk)}")
            sys.stdout.flush()
            
    except Exception as e:
        print(f"Error: {e}")
        return
    
    total_time = time.time() - start_time
    print("-" * 60)
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Test completed in {total_time:.2f}s with {chunk_count} chunks")

if __name__ == "__main__":
    test_streaming() 