#!/usr/bin/env python3
"""
Simple test script to verify model registration
"""
import os
import sys
import logging

# Add the current directory to the path so we can import llm_io_intelligence
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_registration():
    """Test model registration"""
    print("=== Testing model registration ===")
    
    # Import the module
    import llm_io_intelligence
    
    # Mock register function
    registered_models = []
    def mock_register(model):
        registered_models.append(model)
        print(f"Registered: {model.model_id}")
    
    # Test registration
    llm_io_intelligence.register_models(mock_register)
    
    print(f"\nTotal models registered: {len(registered_models)}")
    for model in registered_models:
        print(f"  - {model.model_id}: {model.full_model_name}")

if __name__ == "__main__":
    test_registration()