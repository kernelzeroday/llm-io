#!/usr/bin/env python3
import os
import logging
import llm
from llm_io_intelligence import IOIntelligenceModel

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_tool_execution():
    """Test tool execution with IO Intelligence models"""
    print("=== TESTING TOOL EXECUTION ===")
    
    # Check if API key is set
    api_key = os.environ.get('IOINTELLIGENCE_API_KEY')
    if not api_key:
        print("ERROR: IOINTELLIGENCE_API_KEY environment variable not set")
        print("Please set your API key: export IOINTELLIGENCE_API_KEY='your-key-here'")
        return
    
    # Test with a tool-compatible model
    model = llm.get_model("llama-3.3-70b")
    print(f"Model: {model}")
    
    try:
        print("\n=== Testing llm_version tool ===")
        response = model.prompt(
            "What version of LLM is this?",
            tools=[llm.get_tool("llm_version")]
        )
        
        print(f"Response: {response.text()}")
        
        # Check tool calls
        if hasattr(response, 'tool_calls'):
            tool_calls = response.tool_calls
            if callable(tool_calls):
                tool_calls = tool_calls()
            print(f"Tool calls made: {len(tool_calls)}")
            for i, tool_call in enumerate(tool_calls):
                print(f"  Tool call {i}: {tool_call.name} -> {tool_call.arguments}")
        
        print("\n=== Testing llm_time tool ===")
        response = model.prompt(
            "What time is it?",
            tools=[llm.get_tool("llm_time")]
        )
        
        print(f"Response: {response.text()}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tool_execution() 