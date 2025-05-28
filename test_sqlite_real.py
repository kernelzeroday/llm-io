#!/usr/bin/env python3
import os
import llm
from llm_tools_sqlite import SQLite

def test_sqlite_real():
    """Test SQLite tool with real API call"""
    print("=== TESTING SQLITE TOOL WITH REAL API ===")
    
    # Set the API key from environment
    os.environ['IOINTELLIGENCE_API_KEY'] = os.environ.get('IOINTELLIGENCE_API_KEY', 'your-api-key-here')
    
    # Get the model
    model = llm.get_model("llama-3.3-70b")
    print(f"Model: {model}")
    
    # Create SQLite tool
    sqlite_tool = SQLite("test.db")
    print(f"SQLite tool: {sqlite_tool}")
    
    try:
        print("\n=== Testing SQLite query with Python API ===")
        response = model.prompt(
            "Show me all users in the database with their names and ages. The database has a 'users' table with columns: id, name, age. Use the SQLite_query tool with the 'sql' parameter.",
            tools=[sqlite_tool]
        )
        
        print(f"Response text: {response.text()}")
        
        # Check tool calls
        if hasattr(response, 'tool_calls'):
            tool_calls = response.tool_calls
            if callable(tool_calls):
                tool_calls = tool_calls()
            print(f"\nTool calls made: {len(tool_calls)}")
            for i, tool_call in enumerate(tool_calls):
                print(f"  Tool call {i}: {tool_call}")
            
            if tool_calls:
                print("\n=== Executing tool calls ===")
                try:
                    executed_results = response.execute_tool_calls()
                    print(f"Executed results: {executed_results}")
                    for i, result in enumerate(executed_results):
                        print(f"  Result {i}: {result.name} -> {result.output}")
                except Exception as e:
                    print(f"Tool execution error: {e}")
                    import traceback
                    traceback.print_exc()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sqlite_real() 