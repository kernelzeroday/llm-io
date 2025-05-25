#!/usr/bin/env python3
import argparse
import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import httpx

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IOIntelligenceClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.intelligence.io.solutions/api/v1"):
        self.api_key = api_key or os.environ.get("IOINTELLIGENCE_API_KEY")
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        logger.info(f"Initialized client with base URL: {self.base_url}")
        
    def list_models(self) -> List[Dict[str, Any]]:
        logger.info("Fetching available models")
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{self.base_url}/models", headers=self.headers)
            response.raise_for_status()
            result = response.json()
            models = result.get("data", [])
            logger.info(f"Found {len(models)} models")
            return models
            
    def chat_completion(self, model: str, messages: List[Dict[str, str]], 
                       temperature: float = 0.7, max_tokens: Optional[int] = None,
                       stream: bool = False, **kwargs) -> Dict[str, Any]:
        logger.info(f"Creating chat completion with model: {model}")
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        
        if max_tokens:
            data["max_completion_tokens"] = max_tokens
            
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
                
        logger.info(f"Request data: {json.dumps(data, indent=2)}")
        
        with httpx.Client(timeout=60.0) as client:
            if stream:
                return self._handle_streaming_response(client, data)
            else:
                response = client.post(f"{self.base_url}/chat/completions", headers=self.headers, json=data)
                response.raise_for_status()
                result = response.json()
                logger.info(f"Received response with {len(result.get('choices', []))} choices")
                return result
                
    def _handle_streaming_response(self, client: httpx.Client, data: Dict[str, Any]):
        logger.info("Handling streaming response")
        with client.stream("POST", f"{self.base_url}/chat/completions", headers=self.headers, json=data) as response:
            response.raise_for_status()
            
            content_chunks = []
            for line in response.iter_lines():
                if line.startswith("data: "):
                    line = line[6:]
                    
                if line.strip() == "[DONE]":
                    logger.info("Streaming complete")
                    break
                    
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                content = delta["content"]
                                content_chunks.append(content)
                                print(content, end="", flush=True)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON: {line} - {e}")
                        continue
                        
            print()  # New line after streaming
            return {"content": "".join(content_chunks)}
            
    def create_embeddings(self, model: str, texts: List[str]) -> Dict[str, Any]:
        logger.info(f"Creating embeddings with model: {model} for {len(texts)} texts")
        
        data = {
            "model": model,
            "input": texts,
        }
        
        logger.info(f"Embedding request data: {json.dumps(data, indent=2)}")
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(f"{self.base_url}/embeddings", headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Received embeddings for {len(result.get('data', []))} items")
            return result

def list_models_command(args):
    logger.info("Executing list models command")
    client = IOIntelligenceClient(args.api_key)
    
    try:
        models = client.list_models()
        
        if args.json:
            print(json.dumps(models, indent=2))
        else:
            print(f"Available models ({len(models)}):")
            print("-" * 50)
            for i, model in enumerate(models, 1):
                model_id = model.get("id", "Unknown")
                owned_by = model.get("owned_by", "Unknown")
                created = model.get("created", "Unknown")
                print(f"{i:2d}. {model_id}")
                print(f"    Owner: {owned_by}")
                print(f"    Created: {created}")
                print()
                
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def chat_command(args):
    logger.info("Executing chat command")
    client = IOIntelligenceClient(args.api_key)
    
    messages = []
    
    if args.system:
        messages.append({"role": "system", "content": args.system})
        logger.info(f"Added system message: {args.system[:50]}...")
        
    if args.conversation_file:
        logger.info(f"Loading conversation from: {args.conversation_file}")
        with open(args.conversation_file, 'r') as f:
            conversation = json.load(f)
            messages.extend(conversation.get("messages", []))
            
    messages.append({"role": "user", "content": args.prompt})
    logger.info(f"Added user message: {args.prompt[:50]}...")
    
    try:
        kwargs = {}
        if args.top_p:
            kwargs["top_p"] = args.top_p
        if args.frequency_penalty:
            kwargs["frequency_penalty"] = args.frequency_penalty
        if args.presence_penalty:
            kwargs["presence_penalty"] = args.presence_penalty
        if args.reasoning_content:
            kwargs["reasoning_content"] = args.reasoning_content
            
        result = client.chat_completion(
            model=args.model,
            messages=messages,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            stream=args.stream,
            **kwargs
        )
        
        if not args.stream:
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    print(content)
                    
                    if args.save_conversation:
                        logger.info(f"Saving conversation to: {args.save_conversation}")
                        conversation_data = {
                            "messages": messages + [{"role": "assistant", "content": content}]
                        }
                        with open(args.save_conversation, 'w') as f:
                            json.dump(conversation_data, f, indent=2)
                else:
                    print("No response content received")
                    
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def embed_command(args):
    logger.info("Executing embed command")
    client = IOIntelligenceClient(args.api_key)
    
    texts = []
    
    if args.text:
        texts.append(args.text)
        
    if args.file:
        logger.info(f"Reading texts from file: {args.file}")
        with open(args.file, 'r') as f:
            file_texts = [line.strip() for line in f if line.strip()]
            texts.extend(file_texts)
            
    if not sys.stdin.isatty():
        logger.info("Reading texts from stdin")
        stdin_texts = [line.strip() for line in sys.stdin if line.strip()]
        texts.extend(stdin_texts)
        
    if not texts:
        print("Error: No texts provided for embedding")
        sys.exit(1)
        
    logger.info(f"Processing {len(texts)} texts for embedding")
    
    try:
        result = client.create_embeddings(args.model, texts)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            embeddings = result.get("data", [])
            print(f"Generated {len(embeddings)} embeddings:")
            print("-" * 50)
            
            for i, embedding_data in enumerate(embeddings):
                embedding = embedding_data.get("embedding", [])
                print(f"Text {i+1}: {texts[i][:50]}{'...' if len(texts[i]) > 50 else ''}")
                print(f"Embedding dimensions: {len(embedding)}")
                if args.show_vectors:
                    print(f"Vector (first 10): {embedding[:10]}")
                print()
                
    except Exception as e:
        logger.error(f"Error creating embeddings: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="IO Intelligence API CLI Tool")
    parser.add_argument("--api-key", help="IO Intelligence API key (or set IOINTELLIGENCE_API_KEY)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List models command
    list_parser = subparsers.add_parser("list", help="List available models")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Generate chat completions")
    chat_parser.add_argument("prompt", help="User prompt")
    chat_parser.add_argument("-m", "--model", required=True, help="Model ID to use")
    chat_parser.add_argument("-s", "--system", help="System prompt")
    chat_parser.add_argument("-t", "--temperature", type=float, default=0.7, help="Temperature (0.0-2.0)")
    chat_parser.add_argument("--max-tokens", type=int, help="Maximum tokens to generate")
    chat_parser.add_argument("--top-p", type=float, help="Top-p nucleus sampling")
    chat_parser.add_argument("--frequency-penalty", type=float, help="Frequency penalty")
    chat_parser.add_argument("--presence-penalty", type=float, help="Presence penalty")
    chat_parser.add_argument("--reasoning-content", action="store_true", help="Include reasoning content")
    chat_parser.add_argument("--stream", action="store_true", help="Enable streaming")
    chat_parser.add_argument("--conversation-file", help="Load conversation from JSON file")
    chat_parser.add_argument("--save-conversation", help="Save conversation to JSON file")
    
    # Embed command
    embed_parser = subparsers.add_parser("embed", help="Generate embeddings")
    embed_parser.add_argument("-m", "--model", required=True, help="Embedding model ID")
    embed_parser.add_argument("-t", "--text", help="Text to embed")
    embed_parser.add_argument("-f", "--file", help="File containing texts to embed (one per line)")
    embed_parser.add_argument("--show-vectors", action="store_true", help="Show first 10 vector components")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")
        
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    if args.command == "list":
        list_models_command(args)
    elif args.command == "chat":
        chat_command(args)
    elif args.command == "embed":
        embed_command(args)

if __name__ == "__main__":
    main() 