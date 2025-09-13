# Running OllaBench with OpenAI and Anthropic APIs

## Overview

While the original `OllaBench1.py` only supports Ollama, I've analyzed the codebase and created `OllaBench1_enhanced.py` that supports:

- **Ollama** (local models)
- **OpenAI** (GPT-3.5, GPT-4, etc.)  
- **Anthropic** (Claude models)

## Key Findings from Code Analysis

### Original Limitations
The original `OllaBench1.py` has **commented-out** OpenAI integration:
```python
# Lines 52-57 in OllaBench1.py (commented out)
'''
if llm_framework=="openai":
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
'''
```

The `get_response()` function only implements Ollama:
```python
def get_response(llm_framework,a_model,a_prompt):
    if llm_framework =="ollama":
        result = ollama.generate(model=a_model, prompt= a_prompt, stream=False)
        # ... ollama-specific code only
    return result
```

### GUI Implementation Has Full Support
However, the **GUI version** (`pages/OllaBench_gui_generate_responses.py`) has complete implementations for OpenAI and Anthropic that I've adapted for the enhanced version.

## Setup Instructions

### Option 1: Use Enhanced Version (Recommended)

**1. Set up API Keys**
```bash
# For OpenAI
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# For Anthropic  
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key-here"
```

**2. Install Additional Dependencies**
```bash
pip install openai anthropic
```

**3. Configure for OpenAI**

Create/modify `params.json`:
```json
{
    "llm_framework": "openai",
    "llm_models": [
        "gpt-4", 
        "gpt-4-turbo-preview",
        "gpt-3.5-turbo"
    ],
    "llm_leaderboard": "OpenAI_LeaderBoard.csv",
    "bench_tries": 3,
    "QA_inpath": "./OllaGen-1/OllaGen1-QA-full.csv"
}
```

**4. Configure for Anthropic**

Create/modify `params.json`:
```json
{
    "llm_framework": "anthropic", 
    "llm_models": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229", 
        "claude-3-haiku-20240307"
    ],
    "llm_leaderboard": "Anthropic_LeaderBoard.csv",
    "bench_tries": 3,
    "QA_inpath": "./OllaGen-1/OllaGen1-QA-full.csv"
}
```

**5. Run Evaluation**
```bash
python OllaBench1_enhanced.py
```

### Option 2: Modify Original OllaBench1.py

If you want to modify the original file instead:

**1. Uncomment and fix OpenAI section** (lines 52-57):
```python
if llm_framework=="openai":
    from openai import OpenAI
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
```

**2. Add Anthropic support**:
```python
if llm_framework=="anthropic":
    import anthropic
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
```

**3. Enhance get_response() function** - copy the implementation from `OllaBench1_enhanced.py`

## Configuration Examples

### OpenAI Models

**Popular Models:**
- `gpt-4` - Most capable, expensive
- `gpt-4-turbo-preview` - Latest GPT-4 variant
- `gpt-3.5-turbo` - Faster, cheaper
- `gpt-4o` - Multimodal model

**Cost Considerations:**
- GPT-4: ~$0.03-0.06 per 1K tokens
- GPT-3.5-turbo: ~$0.001-0.002 per 1K tokens
- 10,000 questions × 4 question types = ~40K API calls
- Estimated cost: $50-200 for GPT-4, $5-20 for GPT-3.5

### Anthropic Models  

**Available Models:**
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-haiku-20240307` - Fastest, cheapest

**Cost Considerations:**
- Claude-3 Opus: ~$0.015-0.075 per 1K tokens  
- Claude-3 Sonnet: ~$0.003-0.015 per 1K tokens
- Claude-3 Haiku: ~$0.00025-0.00125 per 1K tokens

## Advanced Configuration

### Rate Limiting & Error Handling

The enhanced version includes:
```python
# API rate limiting
if llm_framework in ["openai", "anthropic"]:
    time.sleep(0.1)  # 100ms delay between requests

# Retry logic
tries = 3
while tries > 0:
    try:
        response = get_response(llm_framework, model, prompt)
        break
    except Exception as e:
        tries -= 1
        time.sleep(2)
```

### Response Normalization

Cloud APIs return different formats, but the enhanced version normalizes to Ollama format:

```python
# OpenAI → Ollama format
result = {
    'response': response.choices[0].message.content,
    'eval_count': response.usage.completion_tokens,
    'total_duration': int((end_epoch - begin_epoch) * 1000000000)
}

# Anthropic → Ollama format  
result = {
    'response': response.content[0].text,
    'eval_count': response.usage.output_tokens,
    'total_duration': int((end_epoch - begin_epoch) * 1000000000)
}
```

## Execution Examples

### OpenAI Evaluation
```bash
# Set API key
export OPENAI_API_KEY="sk-your-key"

# Configure params.json for OpenAI
{
    "llm_framework": "openai",
    "llm_models": ["gpt-4", "gpt-3.5-turbo"]
}

# Run evaluation  
python OllaBench1_enhanced.py
```

### Anthropic Evaluation
```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key"

# Configure params.json for Anthropic
{
    "llm_framework": "anthropic", 
    "llm_models": ["claude-3-sonnet-20240229"]
}

# Run evaluation
python OllaBench1_enhanced.py
```

### Mixed Evaluation (Requires Multiple Runs)
```bash
# Run 1: Ollama models
# params.json: "llm_framework": "ollama"
python OllaBench1_enhanced.py

# Run 2: OpenAI models  
# params.json: "llm_framework": "openai"
python OllaBench1_enhanced.py

# Run 3: Anthropic models
# params.json: "llm_framework": "anthropic" 
python OllaBench1_enhanced.py
```

## Expected Output

**File Naming:**
- OpenAI: `gpt-4_chunk0_2024-09-11_16-30_QA_Results.csv`
- Anthropic: `claude-3-sonnet-20240229_chunk0_2024-09-11_16-30_QA_Results.csv`

**Performance:**
- **OpenAI**: ~2-4 seconds per question (API latency)
- **Anthropic**: ~1-3 seconds per question (API latency)  
- **Ollama**: ~0.5-2 seconds per question (local inference)

**Total Time Estimates:**
- 10,000 questions with cloud APIs: 8-12 hours
- 10,000 questions with local Ollama: 2-6 hours

## Troubleshooting

### API Key Issues
```bash
# Verify environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Test API connectivity
python -c "from openai import OpenAI; print(OpenAI().models.list())"
```

### Rate Limiting
- OpenAI: 3,500 RPM (requests per minute) for paid accounts
- Anthropic: 1,000 RPM for Claude-3
- The enhanced version includes automatic delays

### Model Names
- Use exact model names from API documentation
- OpenAI: `gpt-4`, not `gpt4` or `GPT-4`
- Anthropic: `claude-3-sonnet-20240229`, not `claude-3-sonnet`

### Memory/Timeout Issues
For large evaluations:
```python
# Reduce chunk size in enhanced version
chunk_size = 100  # Instead of 500

# Increase timeout handling
tries = 5  # Instead of 3
```

## Cost Management

### Recommendations
1. **Start small**: Test with 100-500 questions first
2. **Use cheaper models**: GPT-3.5-turbo or Claude Haiku for initial runs  
3. **Monitor usage**: Check API dashboards regularly
4. **Set limits**: Configure spending limits in API accounts

### Budget Planning
- **Small test** (1,000 questions): $5-20
- **Full evaluation** (10,000 questions): $50-200
- **Multiple models**: Scale accordingly

The enhanced version provides full cloud LLM support while maintaining compatibility with the original OllaBench evaluation methodology and output formats.