#!/usr/bin/env python3
"""
Test script for model fetching functionality
"""
import os
import sys
import asyncio
import logging
from unittest.mock import patch, MagicMock, AsyncMock

# Add the current directory to the path so we can import llm_io_intelligence
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import llm_io_intelligence

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_fetch_available_models():
    """Test the fetch_available_models function"""
    print("=== Testing fetch_available_models function ===")
    
    # Test with a mock API response
    mock_response_data = {
        "models": [
            {"id": "test-model-1", "name": "Test Model 1", "context_length": 32000},
            {"id": "test-model-2", "name": "Test Model 2", "context_length": 64000},
        ]
    }
    
    # Mock the aiohttp.ClientSession.get method
    with patch('aiohttp.ClientSession') as mock_session_class:
        # Create a mock session
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        # Create a mock response object
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        # Test the function
        api_key = "test-api-key"
        models = await llm_io_intelligence.fetch_available_models(api_key)
        
        print(f"Retrieved {len(models)} models:")
        for model in models:
            print(f"  - {model}")
            
        # Verify the results
        assert len(models) == 2
        assert models[0] == ("test-model-1", "Test Model 1", 32000)
        assert models[1] == ("test-model-2", "Test Model 2", 64000)
        
        print("✅ fetch_available_models test passed")

def test_register_models():
    """Test the register_models function"""
    print("\n=== Testing register_models function ===")
    
    # Mock the register function
    registered_models = []
    def mock_register(model):
        registered_models.append(model)
    
    # Test with API key set
    with patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-api-key"}):
        # Mock the fetch_available_models function
        with patch('llm_io_intelligence.fetch_available_models') as mock_fetch:
            mock_fetch.return_value = [
                ("api-model-1", "API Model 1", 32000),
                ("api-model-2", "API Model 2", 64000),
            ]
            
            # Call the function
            llm_io_intelligence.register_models(mock_register)
            
            print(f"Registered {len(registered_models)} models from API:")
            for model in registered_models:
                print(f"  - {model.model_id}: {model.full_model_name} ({model.context_length})")
                
            # Verify the results
            assert len(registered_models) == 2
            assert registered_models[0].model_id == "api-model-1"
            assert registered_models[1].model_id == "api-model-2"
            
            print("✅ register_models test with API passed")
    
    # Test without API key (fallback to hardcoded models)
    registered_models.clear()
    with patch.dict(os.environ, {}, clear=True):
        llm_io_intelligence.register_models(mock_register)
        
        print(f"Registered {len(registered_models)} models from hardcoded list:")
        for model in registered_models:
            print(f"  - {model.model_id}: {model.full_model_name} ({model.context_length})")
            
        # Verify that some models were registered (should be more than 0)
        assert len(registered_models) > 0
        
        print("✅ register_models test with fallback passed")

async def main():
    """Run all tests"""
    print("Running model fetching tests...\n")
    
    try:
        await test_fetch_available_models()
        test_register_models()
        
        print("\n🎉 All tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)