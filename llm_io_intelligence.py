import os
import json
import logging
import base64
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
    supports_tools = True
    attachment_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    
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
                        # Ensure we get the string content, not the Prompt object
                        prompt_content = message.prompt
                        if hasattr(prompt_content, 'prompt'):
                            prompt_content = prompt_content.prompt
                        messages.append({"role": "user", "content": str(prompt_content)})
                    if message.text():
                        messages.append({"role": "assistant", "content": message.text()})
            
            # Enhanced system prompt for better tool calling behavior
            base_system_prompt = prompt.system if prompt.system else ""
            if hasattr(prompt, 'tools') and prompt.tools:
                # Create a list of available tools for the prompt
                tool_descriptions = []
                for tool in prompt.tools:
                    tool_descriptions.append(f"- {tool.name}: {tool.description}")
                tools_list = "\n".join(tool_descriptions)
                
                tool_calling_instructions = f"""

You have access to the following tools:
{tools_list}

TOOL CALLING INSTRUCTIONS:
1. When the user's question can be answered using one of these tools, call the appropriate tool
2. To call a tool, output EXACTLY this JSON format: {{"name": "tool_name", "arguments": {{}}}}
3. For tools with no parameters, use empty arguments: {{"name": "tool_name", "arguments": {{}}}}
4. For tools with parameters, include them in arguments: {{"name": "tool_name", "arguments": {{"param": "value"}}}}
5. After calling a tool, the system will execute it and provide results
6. Only call tools when they are relevant to answering the user's question

EXAMPLE:
User: "What version?"
Assistant: {{"name": "llm_version", "arguments": {{}}}}

Do not explain what you're doing, just output the JSON when you need to call a tool."""
                enhanced_system_prompt = base_system_prompt + tool_calling_instructions
                messages.insert(0, {"role": "system", "content": enhanced_system_prompt})
            elif prompt.system:
                messages.insert(0, {"role": "system", "content": prompt.system})
            
            # Handle tool results from previous calls
            if hasattr(prompt, 'tool_results') and prompt.tool_results:
                logger.debug(f"Processing {len(prompt.tool_results)} tool results")
                for tool_result in prompt.tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_result.tool_call_id,
                        "content": str(tool_result.output)
                    })
            
            # Handle attachments for vision models
            user_content = []
            
            # Add text content
            if prompt.prompt:
                user_content.append({"type": "text", "text": prompt.prompt})
            
            # Add image attachments if present
            if hasattr(prompt, 'attachments') and prompt.attachments:
                logger.debug(f"Processing {len(prompt.attachments)} attachments")
                for attachment in prompt.attachments:
                    if attachment.type.startswith('image/'):
                        if attachment.url:
                            # Use URL directly
                            user_content.append({
                                "type": "image_url",
                                "image_url": {"url": attachment.url}
                            })
                            logger.debug(f"Added image URL: {attachment.url}")
                        elif attachment.content:
                            # Convert binary content to base64
                            base64_data = base64.b64encode(attachment.content).decode('utf-8')
                            data_url = f"data:{attachment.type};base64,{base64_data}"
                            user_content.append({
                                "type": "image_url", 
                                "image_url": {"url": data_url}
                            })
                            logger.debug(f"Added base64 image: {attachment.type}")
                        elif attachment.path:
                            # Read file and convert to base64
                            with open(attachment.path, 'rb') as f:
                                file_content = f.read()
                            base64_data = base64.b64encode(file_content).decode('utf-8')
                            data_url = f"data:{attachment.type};base64,{base64_data}"
                            user_content.append({
                                "type": "image_url",
                                "image_url": {"url": data_url}
                            })
                            logger.debug(f"Added file image: {attachment.path}")
                    else:
                        logger.warning(f"Unsupported attachment type: {attachment.type}")
            
            # Use content array if we have attachments, otherwise use simple string
            if len(user_content) > 1 or (len(user_content) == 1 and user_content[0]["type"] != "text"):
                messages.append({"role": "user", "content": user_content})
            else:
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
            
            # Add tool calling optimization parameters
            if hasattr(prompt, 'tools') and prompt.tools:
                # Use lower temperature for more deterministic tool calling
                data["temperature"] = 0.1
                data["top_p"] = 0.9
                # Add max_tokens to prevent overly long responses
                data["max_tokens"] = 1000
            
            # Add tools if they exist
            if hasattr(prompt, 'tools') and prompt.tools:
                logger.debug(f"Adding {len(prompt.tools)} tools to request")
                tools = []
                for tool in prompt.tools:
                    tool_def = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                        }
                    }
                    
                    # Try to get the tool schema from various possible attributes
                    schema = None
                    if hasattr(tool, 'parameters') and tool.parameters:
                        schema = tool.parameters
                    elif hasattr(tool, 'schema') and tool.schema:
                        schema = tool.schema
                    elif hasattr(tool, 'input_schema') and tool.input_schema:
                        schema = tool.input_schema
                    
                    if schema:
                        tool_def["function"]["parameters"] = schema
                    else:
                        # Default empty schema if none provided
                        tool_def["function"]["parameters"] = {"type": "object", "properties": {}}
                    
                    tools.append(tool_def)
                
                data["tools"] = tools
                # Use "none" because server doesn't have --enable-auto-tool-choice flag
                data["tool_choice"] = "none"
            
            # Add options if they exist, being careful about JSON serialization
            if prompt.options:
                try:
                    options_dict = prompt.options.model_dump(exclude_none=True)
                    logger.debug(f"Options dict: {options_dict}")
                    # Only add serializable options
                    for key, value in options_dict.items():
                        if isinstance(value, (str, int, float, bool, type(None))):
                            data[key] = value
                        else:
                            logger.warning(f"Skipping non-serializable option: {key}={value}")
                except Exception as e:
                    logger.warning(f"Failed to process options: {e}")
            
            logger.debug(f"Making request to {self.api_base}/chat/completions")
            # Safe debug logging - avoid JSON serialization issues
            try:
                debug_data = {k: v for k, v in data.items() if isinstance(v, (str, int, float, bool, type(None), list, dict))}
                logger.debug(f"Request data keys: {list(debug_data.keys())}")
                # Log the actual tools being sent
                if "tools" in data:
                    logger.debug(f"Tools being sent to API: {json.dumps(data['tools'], indent=2)}")
            except Exception as e:
                logger.debug(f"Debug serialization error: {e}")
            
            # Track tool calls to prevent duplicates
            called_tools = set()
            # Accumulate content for tool call parsing
            accumulated_content = ""
            
            if stream:
                # Use streaming for real-time parsing
                with httpx.Client() as client:
                    with client.stream(
                        "POST",
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=30.0
                    ) as http_response:
                        # Check for errors before processing
                        if http_response.status_code >= 400:
                            # Read error content before raising
                            error_content = b""
                            for chunk in http_response.iter_bytes():
                                error_content += chunk
                            error_text = error_content.decode('utf-8')
                            logger.error(f"HTTP error {http_response.status_code}: {error_text}")
                            raise httpx.HTTPStatusError(f"HTTP {http_response.status_code}", request=http_response.request, response=http_response)
                        
                        http_response.raise_for_status()
                        
                        for line in http_response.iter_lines():
                            if line.startswith("data: "):
                                chunk_data = line[6:]  # Remove "data: " prefix
                                if chunk_data.strip() == "[DONE]":
                                    break
                                
                                try:
                                    chunk = json.loads(chunk_data)
                                    logger.debug(f"Streaming chunk: {chunk}")
                                    if "choices" in chunk and chunk["choices"]:
                                        delta = chunk["choices"][0].get("delta", {})
                                        logger.debug(f"Delta: {delta}")
                                        
                                        if "content" in delta and delta["content"]:
                                            content = delta["content"]
                                            # Accumulate content for tool call parsing
                                            accumulated_content += content
                                            yield content
                                        
                                        # Handle tool calls in streaming with deduplication
                                        if "tool_calls" in delta and delta["tool_calls"]:
                                            logger.debug(f"Found tool calls in delta: {delta['tool_calls']}")
                                            for tool_call in delta["tool_calls"]:
                                                if response and "id" in tool_call and "function" in tool_call:
                                                    # Safely get arguments, handling streaming chunks
                                                    function_data = tool_call["function"]
                                                    arguments_str = function_data.get("arguments", "")
                                                    tool_signature = f"{function_data['name']}:{arguments_str}"
                                                    if tool_signature not in called_tools:
                                                        called_tools.add(tool_signature)
                                                        try:
                                                            arguments = json.loads(arguments_str) if arguments_str else {}
                                                        except (json.JSONDecodeError, TypeError):
                                                            arguments = {}
                                                        logger.debug(f"Adding tool call: {function_data['name']} with args {arguments}")
                                                        response.add_tool_call(llm.ToolCall(
                                                            name=function_data["name"],
                                                            arguments=arguments,
                                                            tool_call_id=tool_call["id"]
                                                        ))
                                                    else:
                                                        logger.debug(f"Skipping duplicate tool call: {tool_signature}")
                                except json.JSONDecodeError:
                                    continue
                
                # Parse accumulated content for tool calls after streaming is complete
                if response and hasattr(prompt, 'tools') and prompt.tools and accumulated_content:
                    self._parse_text_tool_calls(accumulated_content, response, prompt.tools, called_tools)
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
                    logger.debug(f"Non-streaming result: {result}")
                    
                    if "choices" in result and result["choices"]:
                        choice = result["choices"][0]
                        message = choice["message"]
                        logger.debug(f"Message: {message}")
                        
                        if "content" in message and message["content"]:
                            content = message["content"]
                            # Parse tool calls from the complete content
                            if response and hasattr(prompt, 'tools') and prompt.tools:
                                self._parse_text_tool_calls(content, response, prompt.tools, called_tools)
                            yield content
                        
                        # Handle tool calls in non-streaming with deduplication
                        if "tool_calls" in message and message["tool_calls"]:
                            logger.debug(f"Found tool calls in message: {message['tool_calls']}")
                            for tool_call in message["tool_calls"]:
                                if response:
                                    tool_signature = f"{tool_call['function']['name']}:{tool_call['function'].get('arguments', '')}"
                                    if tool_signature not in called_tools:
                                        called_tools.add(tool_signature)
                                        try:
                                            arguments = json.loads(tool_call["function"]["arguments"]) if tool_call["function"]["arguments"] else {}
                                        except (json.JSONDecodeError, TypeError):
                                            arguments = {}
                                        logger.debug(f"Adding tool call: {tool_call['function']['name']} with args {arguments}")
                                        response.add_tool_call(llm.ToolCall(
                                            name=tool_call["function"]["name"],
                                            arguments=arguments,
                                            tool_call_id=tool_call["id"]
                                        ))
                                    else:
                                        logger.debug(f"Skipping duplicate tool call: {tool_signature}")
                        else:
                            logger.debug("No tool_calls found in message")
                    else:
                        raise llm.ModelError("No response content received")
                        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise llm.ModelError(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise llm.ModelError(f"Request failed: {str(e)}")

    def _parse_text_tool_calls(self, content: str, response, tools, called_tools):
        """Parse JSON tool calls from text content and convert to actual tool calls"""
        import re
        
        # Look for JSON patterns that look like tool calls - flexible pattern
        json_pattern = r'\{"name":\s*"([^"]+)",\s*"arguments":\s*(\{.*?\})\}'
        matches = re.findall(json_pattern, content)
        
        for tool_name, arguments_str in matches:
            # Check if this tool exists in our available tools
            tool_found = False
            for tool in tools:
                if tool.name == tool_name:
                    tool_found = True
                    break
            
            if tool_found:
                tool_signature = f"{tool_name}:{arguments_str}"
                if tool_signature not in called_tools:
                    called_tools.add(tool_signature)
                    try:
                        arguments = json.loads(arguments_str) if arguments_str.strip() != '{}' else {}
                    except (json.JSONDecodeError, TypeError):
                        arguments = {}
                    
                    # Generate a unique tool call ID
                    import uuid
                    tool_call_id = f"text-parsed-{uuid.uuid4().hex[:16]}"
                    
                    logger.debug(f"Parsed text tool call: {tool_name} with args {arguments}")
                    response.add_tool_call(llm.ToolCall(
                        name=tool_name,
                        arguments=arguments,
                        tool_call_id=tool_call_id
                    ))
                    
                    # Note: We don't remove the JSON from content since we want to show the model's response
        
        return content

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