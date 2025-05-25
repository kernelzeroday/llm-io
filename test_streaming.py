#!/usr/bin/env python3
import subprocess
import sys
import time
from datetime import datetime

def test_streaming():
    print("Testing LLM streaming with timestamps...")
    print("=" * 50)
    
    # Set the API key
    import os
    os.environ['IOINTELLIGENCE_API_KEY'] = 'io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImYwMDdkNjM0LWVjMzctNTA2ZS1iNmI4LTZmNzAxMjk3OTBlMCIsImV4cCI6NDg5NTMwNzY1NH0.A78xxXbsoIlPXQDzkETLd-oAh4MmcmIZwK2MqMTwxsYP01jnh6eP1hQGAKSoHkEbSWy2LOSQY1JjZAn6kxgOhA'
    
    # Test streaming
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Starting streaming test...")
    
    cmd = ['llm', '-m', 'llama-3.3-70b', 'Write a step-by-step guide for making coffee, with detailed explanations for each step']
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    start_time = time.time()
    line_count = 0
    
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line_count += 1
                elapsed = time.time() - start_time
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                print(f"[{timestamp}] (+{elapsed:.2f}s) Line {line_count}: {output.strip()}")
                sys.stdout.flush()
    
    except KeyboardInterrupt:
        process.terminate()
        print("\nTest interrupted by user")
    
    process.wait()
    total_time = time.time() - start_time
    print(f"\n[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Test completed in {total_time:.2f}s with {line_count} lines")

if __name__ == "__main__":
    test_streaming() 