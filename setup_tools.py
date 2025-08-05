#!/usr/bin/env python3
"""
Setup script for LLM IO Intelligence plugin with tool support
"""
import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n=== {description} ===")
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_api_key():
    """Check if API key is set"""
    api_key = os.environ.get('IONET')
    if not api_key:
        print("\n❌ IONET not set")
        print("Please set your API key:")
        print("  export IONET='your-api-key-here'")
        print("Or use: llm keys set ionet")
        return False
    else:
        print(f"✅ API key found: {api_key[:20]}...")
        return True

def main():
    print("🚀 LLM IO Intelligence Plugin Setup")
    print("====================================")
    
    # Check if LLM is installed
    if not run_command("llm --version", "Checking LLM installation"):
        print("❌ LLM not found. Please install it first:")
        print("  pip install llm")
        return
    
    # Install the plugin
    if not run_command("llm install -e .", "Installing IO Intelligence plugin"):
        print("❌ Failed to install plugin")
        return
    
    # Check API key
    if not check_api_key():
        return
    
    # Install useful tool plugins
    tools_to_install = [
        ("llm-tools-simpleeval", "Mathematical calculations"),
        ("llm-tools-sqlite", "SQLite database queries"),
        ("llm-tools-quickjs", "JavaScript execution")
    ]
    
    for tool_package, description in tools_to_install:
        run_command(f"llm install {tool_package}", f"Installing {description}")
    
    # Test basic functionality
    print("\n=== Testing Basic Functionality ===")
    run_command("llm models list | grep llama-3.3-70b", "Checking model availability")
    
    # Test tool calling
    print("\n=== Testing Tool Calling ===")
    run_command('llm --tool llm_version "What version?" --td', "Testing llm_version tool")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Test with: llm -m llama-3.3-70b 'Hello world'")
    print("2. Try tools: llm --tool llm_time 'What time is it?' --td")
    print("3. Math tools: llm --tool simple_eval 'Calculate 15 * 23' --td")
    print("4. Run tests: python debug_tool_execution.py")

if __name__ == "__main__":
    main() 