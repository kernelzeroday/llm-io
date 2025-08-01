import os
import json
import logging
import base64
from typing import Optional, List, Dict, Any, Union, Iterator
import asyncio
import aiohttp
import llm
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import mimetypes
import queue
import threading

# Configure logging to be less verbose - only warnings and errors
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@llm.hookimpl
def register_models(register):
    logger.debug("Registering io intelligence models")
    
    models = [
        # Current models from API
        ("llama-4-maverick-17b", "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", 430000),
        ("deepseek-r1-0528", "deepseek-ai/DeepSeek-R1-0528", 128000),
        ("intel-qwen3-coder-480b", "Intel/Qwen3-Coder-480B-A35B-Instruct-int4-mixed-ar", 32000),
        ("qwen3-235b", "Qwen/Qwen3-235B-A22B-FP8", 32000),
        ("llama-3.2-90b-vision", "meta-llama/Llama-3.2-90B-Vision-Instruct", 16000),
        ("qwen2.5-vl-32b", "Qwen/Qwen2.5-VL-32B-Instruct", 32000),
        ("llama-3.3-70b", "meta-llama/Llama-3.3-70B-Instruct", 128000),
        ("devstral-small-2505", "mistralai/Devstral-Small-2505", 32000),
        ("magistral-small-2506", "mistralai/Magistral-Small-2506", 32000),
        ("mistral-large-2411", "mistralai/Mistral-Large-Instruct-2411", 128000),
        ("aya-expanse-32b", "CohereForAI/aya-expanse-32b", 8000),
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

        # Set the model ID for llm framework
        self.__dict__["model_id"] = model_id

    def __str__(self):
        return f"IOIntelligenceModel: {self.model_id}"

    def build_messages(self, prompt, conversation) -> List[Dict[str, Any]]:
        messages = []
        if conversation:
            for prev_response in conversation.responses:
                messages.extend(prev_response.request.messages)
                
        # Add the current prompt
        messages.append({"role": "user", "content": prompt.prompt})
        return messages

    async def execute_async_with_tools(self, prompt, tools=None, get_env_var=None, stream=False):
        """Execute the model asynchronously with tool support"""
        api_key = get_env_var("IOINTELLIGENCE_API_KEY") if get_env_var else os.environ.get("IOINTELLIGENCE_API_KEY")
        if not api_key:
            raise ValueError("IOINTELLIGENCE_API_KEY environment variable is required")

        # Build messages
        messages = self.build_messages(prompt, prompt.conversation if hasattr(prompt, 'conversation') else None)
        
        # Prepare the request payload
        payload = {
            "model": self.full_model_name,
            "messages": messages,
            "stream": stream,
            "tools": tools if tools else [],
        }

        # Add attachments if present
        attachments = getattr(prompt, 'attachments', [])
        if attachments:
            payload["attachments"] = self._process_attachments(attachments)

        logger.debug(f"Sending request to {self.api_base}/chat/completions with model {self.full_model_name}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API request failed with status {response.status}: {error_text}")
                        raise Exception(f"API request failed: {response.status} - {error_text}")

                    if stream:
                        # Handle streaming response - parse SSE format
                        buffer = ""
                        async for chunk in response.content:
                            if chunk:
                                buffer += chunk.decode('utf-8')
                                # Process complete lines
                                while '\n' in buffer:
                                    line, buffer = buffer.split('\n', 1)
                                    line = line.strip()
                                    
                                    # Skip empty lines and non-data lines
                                    if not line or not line.startswith('data:'):
                                        continue
                                        
                                    # Extract the data part
                                    data_str = line[5:].strip()  # Remove 'data:' prefix
                                    
                                    # Check for end of stream
                                    if data_str == '[DONE]':
                                        break
                                        
                                    try:
                                        # Parse the JSON data
                                        data = json.loads(data_str)
                                        # Extract content from choices
                                        if 'choices' in data and len(data['choices']) > 0:
                                            choice = data['choices'][0]
                                            if 'delta' in choice and 'content' in choice['delta']:
                                                content = choice['delta']['content']
                                                if content:
                                                    yield content
                                    except json.JSONDecodeError:
                                        # Skip invalid JSON
                                        continue
                    else:
                        # Handle non-streaming response
                        result = await response.json()
                        logger.debug(f"Received response: {result}")

                        # Extract the content and tool calls
                        choice = result["choices"][0]
                        message = choice["message"]
                        
                        # Handle tool calls if present
                        if "tool_calls" in message and message["tool_calls"]:
                            return_message = {
                                "content": message.get("content", ""),
                                "tool_calls": message["tool_calls"]
                            }
                        else:
                            return_message = {
                                "content": message.get("content", ""),
                                "tool_calls": []
                            }
                        # Yield the result for non-streaming mode
                        yield return_message
                        
            except aiohttp.ClientError as e:
                logger.error(f"Network error during API request: {e}")
                raise Exception(f"Network error: {e}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response: {e}")
                raise Exception(f"Invalid JSON response: {e}")
            except KeyError as e:
                logger.error(f"Missing expected key in response: {e}")
                raise Exception(f"Invalid response format: missing key {e}")

    def _process_attachments(self, attachments) -> List[Dict[str, str]]:
        """Process attachments and convert them to base64 encoded strings"""
        processed_attachments = []
        
        for attachment in attachments:
            # Determine MIME type
            mime_type = attachment.mime_type or mimetypes.guess_type(attachment.path)[0] or "application/octet-stream"
            
            # Read and encode the file
            try:
                with open(attachment.path, "rb") as f:
                    encoded_content = base64.b64encode(f.read()).decode('utf-8')
                
                processed_attachments.append({
                    "type": "base64",
                    "media_type": mime_type,
                    "data": encoded_content
                })
            except Exception as e:
                logger.warning(f"Failed to process attachment {attachment.path}: {e}")
                
        return processed_attachments

    def execute(self, prompt, stream: bool, response, conversation=None):
        """Synchronous wrapper for async execution"""
        # Store the prompt JSON for debugging
        messages = self.build_messages(prompt, conversation)
        response._prompt_json = {"messages": messages}
        
        # Run the async method in a new event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if stream:
            # Handle streaming - yield chunks in real-time
            def sync_stream():
                # Create queues to handle async-to-sync streaming
                chunk_queue = queue.Queue()
                exception_queue = queue.Queue()
                done_queue = queue.Queue()
                
                # Producer function that runs in a separate thread
                def producer():
                    async def async_producer():
                        try:
                            async for chunk in self.execute_async_with_tools(prompt, stream=True):
                                chunk_queue.put(chunk)
                        except Exception as e:
                            exception_queue.put(e)
                        finally:
                            done_queue.put(True)
                    
                    # Run the async producer
                    loop.run_until_complete(async_producer())
                
                # Start the producer in a separate thread
                producer_thread = threading.Thread(target=producer)
                producer_thread.start()
                
                # Consumer - yield chunks as they arrive
                while True:
                    try:
                        # Check for exceptions first
                        try:
                            exc = exception_queue.get_nowait()
                            raise exc
                        except queue.Empty:
                            pass
                        
                        # Try to get a chunk with timeout
                        try:
                            chunk = chunk_queue.get(timeout=0.1)
                            yield chunk
                        except queue.Empty:
                            # Check if we're done
                            try:
                                done_queue.get_nowait()
                                break
                            except queue.Empty:
                                # Still waiting, continue
                                continue
                                
                    except Exception as e:
                        # Make sure to join the thread before re-raising
                        producer_thread.join()
                        raise e
                
                # Wait for the producer thread to finish
                producer_thread.join()
                    
            return sync_stream()
        else:
            # Handle non-streaming
            result_generator = self.execute_async_with_tools(prompt, stream=False)
            # Get the first (and only) item from the generator
            result = loop.run_until_complete(result_generator.__anext__())
            content = result["content"]
            
            # Handle tool calls if present
            if result["tool_calls"]:
                for tool_call in result["tool_calls"]:
                    response.add_tool_call(
                        llm.ToolCall(
                            name=tool_call["function"]["name"],
                            arguments=tool_call["function"]["arguments"],
                        )
                    )
            
            # Return the content as an iterator
            return iter([content])

    async def execute_async(self, prompt, get_env_var=None):
        """Async execution without tools for compatibility"""
        result_generator = self.execute_async_with_tools(prompt, get_env_var=get_env_var, stream=False)
        # Get the first (and only) item from the generator
        result = await result_generator.__anext__()
        return result["content"]
