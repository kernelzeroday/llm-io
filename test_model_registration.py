#!/usr/bin/env python3
"""
Test script for model registration functionality
"""
import os
import sys
import logging
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import llm_io_intelligence
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import llm_io_intelligence

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_register_models_with_api_key():
    """Test the register_models function when API key is present"""
    print("=== Testing register_models function with API key ===")
    
    # Mock the register function
    registered_models = []
    def mock_register(model):
        registered_models.append(model)
    
    # Test with API key set via LLM key system
    with patch('llm.get_key') as mock_get_key:
        mock_get_key.return_value = "test-api-key"
        # Mock the fetch_available_models function to simulate API failure
        with patch('llm_io_intelligence.fetch_available_models') as mock_fetch:
            mock_fetch.return_value = []  # Simulate API failure
            
            # Call the function
            llm_io_intelligence.register_models(mock_register)
            
            print(f"Registered {len(registered_models)} models (no fallback when API key present):")
            for model in registered_models:
                print(f"  - {model.model_id}: {model.full_model_name} ({model.context_length})")
                
            # Verify that no models were registered when API key is present but API call fails
            assert len(registered_models) == 0
            
            print("✅ register_models test with API key and API failure passed")
    
    # Test with API key set and successful API response
    registered_models.clear()
    with patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-api-key"}):
        # Mock the fetch_available_models function to simulate successful API response
        with patch('llm_io_intelligence.fetch_available_models') as mock_fetch:
            mock_fetch.return_value = [
                ("ionet/api-model-1", "API Model 1", 32000),
                ("ionet/api-model-2", "API Model 2", 64000),
            ]
            
            # Call the function
            llm_io_intelligence.register_models(mock_register)
            
            print(f"Registered {len(registered_models)} models from API:")
            for model in registered_models:
                print(f"  - {model.model_id}: {model.full_model_name} ({model.context_length})")
                
            # Verify the results
            assert len(registered_models) == 2
            assert registered_models[0].model_id == "ionet/api-model-1"
            assert registered_models[1].model_id == "ionet/api-model-2"
            
            print("✅ register_models test with API key and successful API response passed")

def test_register_models_without_api_key():
    """Test the register_models function when no API key is present"""
    print("\n=== Testing register_models function without API key ===")
    
    # Mock the register function
    registered_models = []
    def mock_register(model):
        registered_models.append(model)
    
    # Test without API key (fallback to hardcoded models)
    registered_models.clear()
    with patch.dict(os.environ, {}, clear=True):
        # Mock llm.get_key to return None
        with patch('llm.get_key', return_value=None):
            llm_io_intelligence.register_models(mock_register)
        
        print(f"Registered {len(registered_models)} models from hardcoded list:")
        for model in registered_models:
            print(f"  - {model.model_id}: {model.full_model_name} ({model.context_length})")
            
        # Verify that some models were registered (should be more than 0)
        assert len(registered_models) > 0
        
        print("✅ register_models test without API key passed")

def main():
    """Run all tests"""
    print("Running model registration tests...\n")
    
    try:
        test_register_models_with_api_key()
        test_register_models_without_api_key()
        
        print("\n🎉 All tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)