# LLM IO Intelligence Plugin

A plugin for [LLM](https://llm.datasette.io/) that provides access to IO Intelligence models with **full tool calling support**.

## Features

- **31 IO Intelligence models** including Llama, Qwen, DeepSeek, Gemma, and more
- **Complete tool calling support** - works with all LLM tools
- **Text-based tool call parsing** - innovative approach for models that simulate tool calls
- **Streaming and non-streaming support**
- **Vision model support** for image analysis
- **Embedding models** for text embeddings

## Installation

```bash
llm install llm-io-intelligence
```

## Setup

Set your IO Intelligence API key:

```bash
llm keys set iointelligence
# Paste your API key when prompted
```

Or set it as an environment variable:

```bash
export IOINTELLIGENCE_API_KEY="your-api-key-here"
```

## Tool Calling Support

This plugin provides **complete tool calling support** for IO Intelligence models. All LLM tools work seamlessly:

### Basic Tools

```bash
# Get LLM version
llm --tool llm_version "What version?" --td

# Get current time
llm --tool llm_time "What time is it?" --td
```

### Mathematical Tools

```bash
# Install math tools
llm install llm-tools-simpleeval

# Use mathematical calculations
llm --tool simple_eval "Calculate 15 * 23 + 7" --td
```

### Database Tools

```bash
# Install SQLite tools
llm install llm-tools-sqlite

# Query a database
llm -T 'SQLite("database.db")' "Show me all users" --td
```

### JavaScript Tools

```bash
# Install JavaScript tools
llm install llm-tools-quickjs

# Execute JavaScript code
llm --tool quickjs "Calculate factorial of 5" --td
```

### Custom Functions (Inline)

```bash
# Powerful math calculator (one-liner)
llm -m llama-3.3-70b --functions 'def calc(expression): import math; return eval(expression, {"math": math, "sqrt": math.sqrt, "sin": math.sin, "pi": math.pi})' --td 'Calculate sqrt(144) + sin(pi/2) * 10'

# Simple operations
llm --functions 'def add(a, b): return a + b' --td 'Add 15 and 27'

# String manipulation
llm --functions 'def reverse(text): return text[::-1]' --td 'Reverse the word "hello"'
```

### File-based Functions

```bash
# Create a functions file
echo 'def calc(expression): import math; return eval(expression, {"math": math, "sqrt": math.sqrt, "sin": math.sin, "pi": math.pi})' > my_functions.py

# Use the functions file
llm -m qwen3-235b --functions my_functions.py --td 'What is the area of a circle with radius 5?'
```

## Available Models

### Chat Models

| Model ID | Full Name | Context Length | Tool Support |
|----------|-----------|----------------|--------------|
| `llama-3.3-70b` | meta-llama/Llama-3.3-70B-Instruct | 128K | ✅ Full |
| `qwen3-235b` | Qwen/Qwen3-235B-A22B-FP8 | 8K | ✅ Full |
| `llama-3.2-90b-vision` | meta-llama/Llama-3.2-90B-Vision-Instruct | 16K | ✅ Full |
| `llama-4-maverick-17b` | meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8 | 430K | ✅ Full |
| `llama-3.1-nemotron-70b` | neuralmagic/Llama-3.1-Nemotron-70B-Instruct-HF-FP8-dynamic | 128K | ✅ Full |
| `deepseek-r1` | deepseek-ai/DeepSeek-R1 | 128K | ❌ Server config |
| `phi-4` | microsoft/phi-4 | 16K | ❌ Server config |

*And 24 more models - see full list with `llm models list`*

### Vision Models

- `llama-3.2-90b-vision` - Image analysis and understanding
- `qwen2-vl-7b` - Vision-language model

### Embedding Models

- `bge-multilingual-gemma2` - Multilingual embeddings
- `mxbai-embed-large-v1` - Large context embeddings

## Usage Examples

### Basic Chat

```bash
llm -m llama-3.3-70b "Explain quantum computing"
```

### With Tools

```bash
# Mathematical calculation
llm -m llama-3.3-70b --tool simple_eval "What's the square root of 12345?" --td

# Database query
llm -m llama-3.3-70b -T 'SQLite("data.db")' "Show top 5 customers by revenue" --td

# Custom function calculation
llm -m qwen3-235b --functions 'def calc(expression): import math; return eval(expression, {"math": math, "sqrt": math.sqrt, "sin": math.sin, "pi": math.pi})' --td 'Calculate sqrt(144) + sin(pi/2) * 10'
```

### Vision Analysis

```bash
llm -m llama-3.2-90b-vision "Describe this image" -a image.jpg
```

### Python API

```python
import llm
from llm_tools_sqlite import SQLite

# Get model
model = llm.get_model("llama-3.3-70b")

# Use with tools
response = model.prompt(
    "Show me all users with age > 25",
    tools=[SQLite("database.db")]
)

print(response.text())

# Check tool calls
for tool_call in response.tool_calls:
    print(f"Tool: {tool_call.name}, Args: {tool_call.arguments}")

# Using custom functions
import math

def calc(expression):
    """Powerful calculator with math functions"""
    safe_dict = {"math": math, "sqrt": math.sqrt, "sin": math.sin, "pi": math.pi}
    return str(eval(expression, safe_dict))

# Register as tool and use
response = model.prompt(
    "Calculate the circumference of a circle with radius 10",
    tools=[calc]  # Functions can be used directly as tools
)
```

## How Tool Calling Works

This plugin implements an innovative **text-based tool call parsing** approach:

1. **Tool definitions sent** - Proper OpenAI-compatible tool schemas sent to API
2. **Model outputs JSON** - Models output tool calls as JSON text like `{"name": "tool_name", "arguments": {}}`
3. **Text parsing** - Plugin detects and parses JSON patterns from model output
4. **Tool execution** - Converts text to actual `ToolCall` objects and executes them
5. **Results returned** - Tool results fed back to model for final response

This approach bridges the gap between IO Intelligence's text-based responses and LLM's tool calling framework.

## Tool Compatibility

✅ **Working Tools:**
- `llm_version`, `llm_time` - Built-in LLM tools
- `simple_eval` - Mathematical expressions
- `SQLite` - Database queries and schema inspection
- `quickjs` - JavaScript code execution
- `Datasette` - Remote database queries
- **Custom functions** - Inline Python functions via `--functions`

✅ **All tool types supported:**
- Simple tools (no parameters)
- Parameterized tools (with arguments)
- Complex toolbox-style tools (multiple methods)
- Async and sync tools
- **Inline functions** (one-liners and file-based)
- **Custom eval functions** with math libraries

✅ **Tested Models:**
- `llama-3.3-70b` - Full tool support, multiple verification calls
- `qwen3-235b` - Full tool support, clean execution with thinking process
- `llama-3.2-90b-vision` - Vision + tool calling combined
- `llama-4-maverick-17b` - Advanced tool calling capabilities

## Configuration

### Model Options

```bash
# Set temperature
llm -m llama-3.3-70b -o temperature 0.8 "Creative writing task"

# Set max tokens
llm -m llama-3.3-70b -o max_tokens 1000 "Long explanation needed"

# Enable reasoning content (for compatible models)
llm -m deepseek-r1 -o reasoning_content true "Complex problem"
```

### Default Model

```bash
# Set default model
llm models default llama-3.3-70b

# Now you can omit -m
llm "Hello world"
```

## Development

### Running Tests

```bash
# Test basic functionality
python debug_tool_execution.py

# Test SQLite integration
python test_sqlite_real.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Troubleshooting

### Tool Calling Issues

If tools aren't working:

1. **Check model support** - Use models like `llama-3.3-70b` or `qwen3-235b` that support tool calling
2. **Verify API key** - Ensure `IOINTELLIGENCE_API_KEY` is set correctly
3. **Use debug mode** - Add `--td` flag to see tool call details
4. **Check tool installation** - Ensure tool plugins are installed
5. **Parameter names** - For custom functions, use parameter names the model expects (e.g., `expression` not `expr`)

### Common Errors

- `"does not support tools"` - Use a tool-compatible model (see table above)
- `"API key not found"` - Set the `IOINTELLIGENCE_API_KEY` environment variable
- `"Chain limit exceeded"` - Model made too many tool calls (safety limit)
- `"unexpected keyword argument"` - Check function parameter names match model expectations
- `"missing required argument"` - Ensure function parameters are properly defined

## License

Apache License 2.0

## Links

- [LLM Documentation](https://llm.datasette.io/)
- [IO Intelligence API](https://intelligence.io.solutions/)
- [Tool Plugins Directory](https://llm.datasette.io/en/stable/plugins/directory.html#tools)
- [Simon Willison's Tool Guide](https://simonwillison.net/2025/May/27/llm-tools/) 