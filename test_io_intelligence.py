import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
import httpx
import llm
from pydantic import ValidationError
from llm_io_intelligence import (
    IOIntelligenceModel,
    IOIntelligenceEmbedModel,
    register_models,
    register_embedding_models
)

class TestIOIntelligenceModel:
    def setup_method(self):
        self.model = IOIntelligenceModel("meta-llama/Llama-3.3-70B-Instruct", "llama-3.3-70b", 128000)
        
    def test_model_initialization(self):
        assert self.model.full_model_name == "meta-llama/Llama-3.3-70B-Instruct"
        assert self.model.model_id == "llama-3.3-70b"
        assert self.model.context_length == 128000
        assert self.model.needs_key == "iointelligence"
        assert self.model.key_env_var == "IOINTELLIGENCE_API_KEY"
        
    def test_str_representation(self):
        assert str(self.model) == "IO Intelligence: llama-3.3-70b"
        
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_get_key_success(self):
        api_key = self.model.get_key()
        assert api_key == "test-key"
        
    @patch.dict(os.environ, {}, clear=True)
    def test_get_key_missing(self):
        api_key = self.model.get_key()
        assert api_key is None
        
    def test_build_messages_simple(self):
        mock_prompt = Mock()
        mock_prompt.system = None
        mock_prompt.prompt = "Hello, world!"
        
        messages = self.model._build_messages(mock_prompt, None)
        
        assert len(messages) == 1
        assert messages[0] == {"role": "user", "content": "Hello, world!"}
        
    def test_build_messages_with_system(self):
        mock_prompt = Mock()
        mock_prompt.system = "You are a helpful assistant."
        mock_prompt.prompt = "Hello, world!"
        
        messages = self.model._build_messages(mock_prompt, None)
        
        assert len(messages) == 2
        assert messages[0] == {"role": "system", "content": "You are a helpful assistant."}
        assert messages[1] == {"role": "user", "content": "Hello, world!"}
        
    def test_build_messages_with_conversation(self):
        mock_prompt = Mock()
        mock_prompt.system = None
        mock_prompt.prompt = "What's next?"
        
        mock_prev_response = Mock()
        mock_prev_response.prompt.prompt = "Hello"
        mock_prev_response.text.return_value = "Hi there!"
        
        mock_conversation = Mock()
        mock_conversation.responses = [mock_prev_response]
        
        messages = self.model._build_messages(mock_prompt, mock_conversation)
        
        assert len(messages) == 3
        assert messages[0] == {"role": "user", "content": "Hello"}
        assert messages[1] == {"role": "assistant", "content": "Hi there!"}
        assert messages[2] == {"role": "user", "content": "What's next?"}
        
    @patch('httpx.Client')
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_non_stream_response_success(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello! How can I help you?"}}]
        }
        mock_client.post.return_value = mock_response
        
        mock_prompt = Mock()
        mock_prompt.options = Mock()
        mock_prompt.options.temperature = 0.7
        mock_prompt.options.max_tokens = None
        mock_prompt.options.top_p = None
        mock_prompt.options.frequency_penalty = None
        mock_prompt.options.presence_penalty = None
        mock_prompt.options.reasoning_content = None
        mock_prompt.system = None
        mock_prompt.prompt = "Hello"
        
        result = self.model.execute(mock_prompt, False, None, None)
        
        assert result == "Hello! How can I help you?"
        mock_client.post.assert_called_once()
        
    @patch('httpx.Client')
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_non_stream_response_http_error(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_client.post.side_effect = httpx.HTTPStatusError("401", request=Mock(), response=mock_response)
        
        mock_prompt = Mock()
        mock_prompt.options = Mock()
        mock_prompt.options.temperature = None
        mock_prompt.options.max_tokens = None
        mock_prompt.options.top_p = None
        mock_prompt.options.frequency_penalty = None
        mock_prompt.options.presence_penalty = None
        mock_prompt.options.reasoning_content = None
        mock_prompt.system = None
        mock_prompt.prompt = "Hello"
        
        with pytest.raises(llm.ModelError, match="HTTP 401"):
            self.model.execute(mock_prompt, False, None, None)
            
    @patch('httpx.Client')
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_stream_response_success(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            "data: " + json.dumps({"choices": [{"delta": {"content": "Hello"}}]}),
            "data: " + json.dumps({"choices": [{"delta": {"content": " world"}}]}),
            "data: [DONE]"
        ]
        
        # Create a proper context manager mock
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_response
        mock_client.stream.return_value = mock_context_manager
        
        mock_prompt = Mock()
        mock_prompt.options = Mock()
        mock_prompt.options.temperature = None
        mock_prompt.options.max_tokens = None
        mock_prompt.options.top_p = None
        mock_prompt.options.frequency_penalty = None
        mock_prompt.options.presence_penalty = None
        mock_prompt.options.reasoning_content = None
        mock_prompt.system = None
        mock_prompt.prompt = "Hello"
        
        result = list(self.model.execute(mock_prompt, True, None, None))
        
        assert result == ["Hello", " world"]
        
    def test_execute_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            mock_prompt = Mock()
            mock_prompt.options = Mock()
            
            with pytest.raises(llm.ModelError, match="API key not found"):
                self.model.execute(mock_prompt, False, None, None)

class TestIOIntelligenceEmbedModel:
    def setup_method(self):
        self.embed_model = IOIntelligenceEmbedModel("BAAI/bge-multilingual-gemma2", "bge-multilingual-gemma2", 4096)
        
    def test_embed_model_initialization(self):
        assert self.embed_model.full_model_name == "BAAI/bge-multilingual-gemma2"
        assert self.embed_model.model_id == "bge-multilingual-gemma2"
        assert self.embed_model.max_tokens == 4096
        assert self.embed_model.needs_key == "iointelligence"
        assert self.embed_model.key_env_var == "IOINTELLIGENCE_API_KEY"
        
    @patch('httpx.Client')
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_embed_batch_success(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]}
            ]
        }
        mock_client.post.return_value = mock_response
        
        items = ["Hello", "World"]
        result = list(self.embed_model.embed_batch(items))
        
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_client.post.assert_called_once()
        
    @patch('httpx.Client')
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_embed_batch_http_error(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_client.post.side_effect = httpx.HTTPStatusError("400", request=Mock(), response=mock_response)
        
        items = ["Hello", "World"]
        
        with pytest.raises(llm.ModelError, match="HTTP 400"):
            list(self.embed_model.embed_batch(items))
            
    def test_embed_batch_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            items = ["Hello", "World"]
            
            with pytest.raises(llm.ModelError, match="API key not found"):
                list(self.embed_model.embed_batch(items))

class TestModelOptions:
    def test_temperature_validation(self):
        options = IOIntelligenceModel.Options()
        
        # Valid temperatures
        options.temperature = 0.0
        options.temperature = 1.0
        options.temperature = 2.0
        
        # Invalid temperature - should raise validation error
        with pytest.raises(ValidationError, match="Input should be less than or equal to 2"):
            IOIntelligenceModel.Options(temperature=3.0)
            
        with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
            IOIntelligenceModel.Options(temperature=-1.0)
            
    def test_max_tokens_validation(self):
        options = IOIntelligenceModel.Options()
        
        # Valid max_tokens
        options.max_tokens = 100
        options.max_tokens = None
        
        # Invalid max_tokens - should raise validation error
        with pytest.raises(ValidationError, match="Input should be greater than 0"):
            IOIntelligenceModel.Options(max_tokens=0)
            
        with pytest.raises(ValidationError, match="Input should be greater than 0"):
            IOIntelligenceModel.Options(max_tokens=-1)

class TestRegistration:
    def test_register_models(self):
        mock_register = Mock()
        
        register_models(mock_register)
        
        # Should register 31 models based on the list in the plugin
        assert mock_register.call_count == 31
        
        # Check first and last calls
        first_call_args = mock_register.call_args_list[0][0][0]
        assert isinstance(first_call_args, IOIntelligenceModel)
        assert first_call_args.model_id == "llama-4-maverick-17b"
        
        last_call_args = mock_register.call_args_list[-1][0][0]
        assert isinstance(last_call_args, IOIntelligenceModel)
        assert last_call_args.model_id == "qwen2-vl-7b"
        
    def test_register_embedding_models(self):
        mock_register = Mock()
        
        register_embedding_models(mock_register)
        
        # Should register 2 embedding models
        assert mock_register.call_count == 2
        
        # Check both calls
        first_call_args = mock_register.call_args_list[0][0][0]
        assert isinstance(first_call_args, IOIntelligenceEmbedModel)
        assert first_call_args.model_id == "bge-multilingual-gemma2"
        
        second_call_args = mock_register.call_args_list[1][0][0]
        assert isinstance(second_call_args, IOIntelligenceEmbedModel)
        assert second_call_args.model_id == "mxbai-embed-large-v1"

class TestEdgeCases:
    def setup_method(self):
        self.model = IOIntelligenceModel("test-model", "test", 1000)
        
    def test_empty_prompt(self):
        mock_prompt = Mock()
        mock_prompt.system = None
        mock_prompt.prompt = ""
        
        messages = self.model._build_messages(mock_prompt, None)
        
        assert len(messages) == 1
        assert messages[0] == {"role": "user", "content": ""}
        
    def test_very_long_prompt(self):
        long_text = "x" * 10000
        mock_prompt = Mock()
        mock_prompt.system = None
        mock_prompt.prompt = long_text
        
        messages = self.model._build_messages(mock_prompt, None)
        
        assert len(messages) == 1
        assert messages[0] == {"role": "user", "content": long_text}
        
    @patch('httpx.Client')
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_malformed_streaming_response(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            "data: invalid json",
            "data: " + json.dumps({"invalid": "structure"}),
            "data: [DONE]"
        ]
        
        # Create a proper context manager mock
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_response
        mock_client.stream.return_value = mock_context_manager
        
        mock_prompt = Mock()
        mock_prompt.options = Mock()
        for attr in ['temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty', 'reasoning_content']:
            setattr(mock_prompt.options, attr, None)
        mock_prompt.system = None
        mock_prompt.prompt = "Hello"
        
        result = list(self.model.execute(mock_prompt, True, None, None))
        
        # Should handle malformed responses gracefully and return empty list
        assert result == []
        
    @patch('httpx.Client')
    @patch.dict(os.environ, {"IOINTELLIGENCE_API_KEY": "test-key"})
    def test_empty_response_choices(self, mock_client_class):
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}
        mock_client.post.return_value = mock_response
        
        mock_prompt = Mock()
        mock_prompt.options = Mock()
        for attr in ['temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty', 'reasoning_content']:
            setattr(mock_prompt.options, attr, None)
        mock_prompt.system = None
        mock_prompt.prompt = "Hello"
        
        with pytest.raises(llm.ModelError, match="No response content received"):
            self.model.execute(mock_prompt, False, None, None) 