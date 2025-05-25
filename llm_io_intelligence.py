import os
import json
import logging
from typing import Iterator, List, Optional, Dict, Any
import httpx
import llm
from pydantic import BaseModel, Field, ValidationError, field_validator

# Configure logging to be less verbose - only warnings and errors
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@llm.hookimpl
def register_models(register):
    logger.debug("Registering io intelligence models")
    
    models = [
        ("llama-4-maverick-17b", "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", 430000),
        ("deepseek-r1-distill-llama-70b", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B", 128000),
        ("qwen3-235b", "Qwen/Qwen3-235B-A22B-FP8", 8000),
        ("deepseek-r1", "deepseek-ai/DeepSeek-R1", 128000),
        ("qwq-32b", "Qwen/QwQ-32B", 32000),
        ("deepseek-r1-distill-qwen-32b", "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", 128000),
        ("llama-3.3-70b", "meta-llama/Llama-3.3-70B-Instruct", 128000),
        ("dbrx-instruct", "databricks/dbrx-instruct", 32000),
        ("llama-3.1-nemotron-70b", "neuralmagic/Llama-3.1-Nemotron-70B-Instruct-HF-FP8-dynamic", 128000),
        ("phi-4", "microsoft/phi-4", 16000),
        ("acemath-7b", "nvidia/AceMath-7B-Instruct", 4000),
        ("gemma-3-27b", "google/gemma-3-27b-it", 8000),
        ("mistral-large-2411", "mistralai/Mistral-Large-Instruct-2411", 128000),
        ("watt-tool-70b", "watt-ai/watt-tool-70B", 128000),
        ("dobby-mini-8b", "SentientAGI/Dobby-Mini-Unhinged-Llama-3.1-8B", 128000),
        ("falcon3-10b", "tiiuae/Falcon3-10B-Instruct", 32000),
        ("bespoke-stratos-32b", "bespokelabs/Bespoke-Stratos-32B", 32000),
        ("confucius-o1-14b", "netease-youdao/Confucius-o1-14B", 32000),
        ("aya-expanse-32b", "CohereForAI/aya-expanse-32b", 8000),
        ("qwen2.5-coder-32b", "Qwen/Qwen2.5-Coder-32B-Instruct", 32000),
        ("sky-t1-32b", "NovaSky-AI/Sky-T1-32B-Preview", 32000),
        ("glm-4-9b", "THUDM/glm-4-9b-chat", 128000),
        ("ministral-8b", "mistralai/Ministral-8B-Instruct-2410", 32000),
        ("readerlm-v2", "jinaai/ReaderLM-v2", 512000),
        ("minicpm3-4b", "openbmb/MiniCPM3-4B", 32000),
        ("qwen2.5-1.5b", "Qwen/Qwen2.5-1.5B-Instruct", 32000),
        ("granite-3.1-8b", "ibm-granite/granite-3.1-8b-instruct", 128000),
        ("0x-lite", "ozone-ai/0x-lite", 32000),
        ("phi-3.5-mini", "microsoft/Phi-3.5-mini-instruct", 128000),
        ("llama-3.2-90b-vision", "meta-llama/Llama-3.2-90B-Vision-Instruct", 16000),
        ("qwen2-vl-7b", "Qwen/Qwen2-VL-7B-Instruct", None),
    ]
    
    for model_id, full_name, context_length in models:
        logger.debug(f"Registering model: {model_id} ({full_name})")
        model = IOIntelligenceModel(model_id, full_name, context_length)
        register(model)

class IOIntelligenceModel(llm.Model):
    can_stream = True
    
    def __init__(self, model_id: str, full_model_name: str, context_length: Optional[int] = None):
        self.model_id = model_id
        self.full_model_name = full_model_name
        self.context_length = context_length
        self.api_base = "https://api.intelligence.io.solutions/api/v1"
        logger.debug(f"Initialized model {model_id} with context length {context_length}")

    needs_key = "iointelligence"
    key_env_var = "IOINTELLIGENCE_API_KEY"

    class Options(llm.Options):
        temperature: Optional[float] = Field(
            description="Controls randomness in output. Higher values make output more random.",
            default=0.7,
            ge=0.0,
            le=2.0,
        )
        max_tokens: Optional[int] = Field(
            description="Maximum number of tokens to generate",
            default=None,
            gt=0,
        )
        top_p: Optional[float] = Field(
            description="Nucleus sampling parameter",
            default=None,
            ge=0.0,
            le=1.0,
        )
        frequency_penalty: Optional[float] = Field(
            description="Penalty for frequent tokens",
            default=None,
            ge=-2.0,
            le=2.0,
        )
        presence_penalty: Optional[float] = Field(
            description="Penalty for repeated tokens",
            default=None,
            ge=-2.0,
            le=2.0,
        )
        reasoning_content: Optional[bool] = Field(
            description="Include reasoning content in response",
            default=False,
        )

        @field_validator("temperature")
        def validate_temperature(cls, v):
            if v is not None and not (0.0 <= v <= 2.0):
                raise ValueError("temperature must be between 0.0 and 2.0")
            return v

        @field_validator("max_tokens")
        def validate_max_tokens(cls, v):
            if v is not None and v <= 0:
                raise ValueError("max_tokens must be positive")
            return v

    def __str__(self):
        return f"IO Intelligence: {self.model_id}"

    def execute(self, prompt, stream: bool = True, response=None, conversation=None, **kwargs):
        logger.debug(f"Executing model {self.model_id} with streaming={stream}")
        
        try:
            api_key = os.environ.get(self.key_env_var)
            if not api_key:
                logger.error("API key not found. Set IOINTELLIGENCE_API_KEY environment variable")
                raise ValueError("IOINTELLIGENCE_API_KEY environment variable is required")
            logger.debug("API key found in environment")
            
            messages = []
            if conversation:
                for message in conversation.responses:
                    if message.prompt:
                        messages.append({"role": "user", "content": message.prompt})
                    if message.text():
                        messages.append({"role": "assistant", "content": message.text()})
            
            if prompt.system:
                messages.insert(0, {"role": "system", "content": prompt.system})
            
            messages.append({"role": "user", "content": prompt.prompt})
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.full_model_name,
                "messages": messages,
                "stream": stream
            }
            
            if prompt.options:
                options_dict = prompt.options.model_dump(exclude_none=True)
                data.update(options_dict)
            
            logger.debug(f"Making request to {self.api_base}/chat/completions")
            
            if stream:
                # Use streaming for real-time parsing
                with httpx.stream(
                    "POST",
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                ) as http_response:
                    http_response.raise_for_status()
                    
                    for line in http_response.iter_lines():
                        if line.startswith("data: "):
                            chunk_data = line[6:]  # Remove "data: " prefix
                            if chunk_data.strip() == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(chunk_data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta and delta["content"]:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
            else:
                # Non-streaming request
                with httpx.Client() as client:
                    http_response = client.post(
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=30.0
                    )
                    http_response.raise_for_status()
                    result = http_response.json()
                    
                    if "choices" in result and result["choices"]:
                        content = result["choices"][0]["message"]["content"]
                        yield content
                        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise llm.ModelError(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise llm.ModelError(f"Request failed: {str(e)}")

    def get_key(self):
        api_key = os.environ.get(self.key_env_var)
        if api_key:
            logger.debug("API key found in environment")
        else:
            logger.warning("API key not found in environment")
        return api_key

# Adding embedding models
@llm.hookimpl
def register_embedding_models(register):
    logger.debug("Registering io intelligence embedding models")
    
    embedding_models = [
        ("bge-multilingual-gemma2", "BAAI/bge-multilingual-gemma2", 4096),
        ("mxbai-embed-large-v1", "mixedbread-ai/mxbai-embed-large-v1", 512),
    ]
    
    for model_id, full_name, max_tokens in embedding_models:
        logger.debug(f"Registering embedding model: {model_id} ({full_name})")
        model = IOIntelligenceEmbedModel(model_id, full_name, max_tokens)
        register(model)

class IOIntelligenceEmbedModel(llm.EmbeddingModel):
    def __init__(self, model_id: str, full_model_name: str, max_tokens: int):
        self.model_id = model_id
        self.full_model_name = full_model_name
        self.max_tokens = max_tokens
        self.api_base = "https://api.intelligence.io.solutions/api/v1"
        logger.debug(f"Initialized embedding model {model_id} with max tokens {max_tokens}")

    needs_key = "iointelligence"
    key_env_var = "IOINTELLIGENCE_API_KEY"

    def embed_batch(self, items):
        logger.debug(f"Embedding {len(list(items))} items with model {self.model_id}")
        items_list = list(items)  # Convert to list since we might iterate multiple times
        
        api_key = self.get_key()
        if not api_key:
            logger.error("API key not found. Set IOINTELLIGENCE_API_KEY environment variable")
            raise llm.ModelError("API key not found. Set IOINTELLIGENCE_API_KEY environment variable")

        base_url = "https://api.intelligence.io.solutions/api/v1"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.full_model_name,
            "input": [str(item) for item in items_list],
        }

        logger.debug(f"Embedding request data: {json.dumps(data, indent=2)}")

        with httpx.Client(timeout=60.0) as client:
            try:
                response = client.post(f"{base_url}/embeddings", headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Embedding response received for {len(result.get('data', []))} items")
                
                for item in result.get("data", []):
                    yield item["embedding"]
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error in embedding: {e.response.status_code} - {e.response.text}")
                raise llm.ModelError(f"HTTP {e.response.status_code}: {e.response.text}")
            except Exception as e:
                logger.error(f"Embedding request failed: {str(e)}")
                raise llm.ModelError(f"Embedding request failed: {str(e)}")

    def get_key(self):
        api_key = os.environ.get(self.key_env_var)
        if api_key:
            logger.debug("Embedding API key found in environment")
        else:
            logger.warning("Embedding API key not found in environment")
        return api_key 