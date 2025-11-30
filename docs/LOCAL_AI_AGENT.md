# Local AI Agent Guide

## Overview

Flyto2 supports **completely offline AI agents** using local LLM providers like Ollama. This means you can run autonomous AI agents, chain agents, and LLM chat without:

- ❌ Cloud API costs
- ❌ Internet connection
- ❌ Sharing data with third parties
- ❌ Rate limits

## Quick Start

### 1. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai
```

### 2. Pull a Model

```bash
# General purpose (7B parameters)
ollama pull llama2

# Better reasoning (7B, faster)
ollama pull mistral

# Code generation
ollama pull codellama

# Larger models (13B, more capable)
ollama pull llama2:13b
ollama pull mistral:13b
```

### 3. Start Ollama Server

```bash
ollama serve
```

Keep this running in a separate terminal.

### 4. Run Local AI Workflows

```bash
# Simple local chat
python -m src.cli.main workflows/local_ollama_chat.yaml

# Autonomous agent (offline reasoning)
python -m src.cli.main workflows/local_autonomous_agent.yaml

# Chain agent (multi-step pipeline)
python -m src.cli.main workflows/local_chain_agent.yaml

# Hybrid workflow (mix cloud + local)
python -m src.cli.main workflows/hybrid_cloud_local_agent.yaml
```

## Available Modules

### 1. Local LLM Chat: `ai.local_ollama.chat`

Simple chat with local LLM.

**Example:**
```yaml
steps:
  - id: chat
    module: ai.local_ollama.chat
    params:
      prompt: "Explain quantum computing in simple terms"
      model: "llama2"
      temperature: 0.7
      ollama_url: "http://localhost:11434"
```

**Output:**
```yaml
{
  "response": "Quantum computing is...",
  "model": "llama2",
  "total_duration": 1234567890,
  "eval_count": 42
}
```

### 2. Autonomous Agent: `agent.autonomous`

Self-directed AI agent with reasoning loop.

**Example:**
```yaml
steps:
  - id: agent
    module: agent.autonomous
    params:
      llm_provider: "ollama"  # ← Use local instead of OpenAI
      model: "mistral"
      ollama_url: "http://localhost:11434"
      goal: "Research the pros and cons of microservices"
      max_iterations: 5
      temperature: 0.7
```

**Output:**
```yaml
{
  "result": "Final analysis...",
  "thoughts": ["Step 1...", "Step 2...", "Step 3..."],
  "iterations": 3,
  "goal_achieved": true
}
```

### 3. Chain Agent: `agent.chain`

Sequential AI processing pipeline.

**Example:**
```yaml
steps:
  - id: pipeline
    module: agent.chain
    params:
      llm_provider: "ollama"
      model: "llama2"
      input: "AI in healthcare"
      chain_steps:
        - "Generate 5 blog ideas about: {input}"
        - "Write outline for first idea: {previous}"
        - "Write intro paragraph: {previous}"
```

**Output:**
```yaml
{
  "result": "Final introduction paragraph...",
  "intermediate_results": ["5 ideas...", "Outline...", "Intro..."],
  "steps_completed": 3
}
```

## Recommended Models

| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| **llama2** | 7B | General chat, content generation | Fast |
| **mistral** | 7B | Reasoning, analysis, problem-solving | Fast |
| **codellama** | 7B/13B | Code generation, technical docs | Medium |
| **mixtral** | 8x7B | Complex tasks, high quality | Slow |
| **llama2:13b** | 13B | Better accuracy, deeper reasoning | Medium |
| **phi** | 2.7B | Very fast, simple tasks | Very Fast |

**Hardware requirements:**
- 7B models: 8GB RAM minimum
- 13B models: 16GB RAM minimum
- 70B models: 64GB RAM (not recommended for laptops)

## Use Cases

### 1. Privacy-Sensitive Tasks

```yaml
# Process confidential data locally
- id: analyze_sensitive_data
  module: ai.local_ollama.chat
  params:
    prompt: "Analyze this confidential business data: ${secret_data}"
    model: "mistral"
    system_message: "All data is confidential. Do not log or share."
```

### 2. Offline Development

```yaml
# Generate code without internet
- id: code_gen
  module: ai.local_ollama.chat
  params:
    prompt: "Write a Python function to parse CSV files"
    model: "codellama"
    temperature: 0.2
```

### 3. Cost Optimization

```yaml
# Use local LLM for simple tasks to save API costs
- id: simple_task
  module: ai.local_ollama.chat
  params:
    prompt: "Summarize: ${long_text}"
    model: "llama2"

# Use cloud LLM only for complex tasks
- id: complex_task
  module: api.openai.chat
  params:
    prompt: "Deep analysis of: ${complex_data}"
    model: "gpt-4"
```

### 4. Automated Research

```yaml
# Autonomous agent researches topics offline
- id: research
  module: agent.autonomous
  params:
    llm_provider: "ollama"
    model: "mistral"
    goal: "Research best practices for Docker multi-stage builds"
    max_iterations: 10
```

## Hybrid Cloud + Local Setup

Switch between cloud and local based on requirements:

```yaml
parameters:
  use_local:
    type: boolean
    default: false

steps:
  - id: ai_task
    module: agent.autonomous
    params:
      llm_provider: "${params.use_local ? 'ollama' : 'openai'}"
      model: "${params.use_local ? 'mistral' : 'gpt-4'}"
      ollama_url: "http://localhost:11434"
      goal: "Analyze system architecture"
```

Run with:
```bash
# Use cloud (requires OPENAI_API_KEY)
python -m src.cli.main workflow.yaml

# Use local (offline, free)
python -m src.cli.main workflow.yaml --param use_local=true
```

## Performance Tips

### 1. Model Selection
- **Fast tasks**: Use `phi` or `llama2`
- **Quality tasks**: Use `mistral` or `mixtral`
- **Code tasks**: Use `codellama`

### 2. Temperature Settings
```yaml
temperature: 0.2   # Factual, deterministic
temperature: 0.7   # Balanced (default)
temperature: 1.2   # Creative, diverse
```

### 3. Hardware Optimization
```bash
# GPU acceleration (NVIDIA)
ollama serve --gpu

# Limit concurrent requests
ollama serve --max-loaded-models 1
```

### 4. Context Management
```yaml
# Keep responses concise to save memory
max_tokens: 500

# Or let model decide
max_tokens: null
```

## Troubleshooting

### Error: "Failed to connect to Ollama"

```bash
# Make sure Ollama is running
ollama serve

# Check if model is installed
ollama list

# Pull model if missing
ollama pull llama2
```

### Error: "Model not found"

```bash
# List available models
ollama list

# Pull the model
ollama pull mistral
```

### Slow Performance

- Use smaller models (7B instead of 13B)
- Reduce `max_tokens`
- Close other applications to free RAM
- Enable GPU acceleration if available

### Out of Memory

```bash
# Use smaller model
ollama pull phi  # Only 2.7B parameters

# Or increase system swap/virtual memory
```

## Comparison: Cloud vs Local

| Feature | Cloud (OpenAI) | Local (Ollama) |
|---------|----------------|----------------|
| **Cost** | $0.002-0.03/1k tokens | Free (electricity only) |
| **Privacy** | Data sent to OpenAI | 100% private |
| **Speed** | Fast (optimized infra) | Depends on hardware |
| **Quality** | GPT-4 best-in-class | Llama2/Mistral competitive |
| **Internet** | Required | Offline capable |
| **Rate Limits** | Yes (TPM/RPM) | No limits |
| **Setup** | API key only | Install + download models |

**Recommendation**:
- Use **cloud** for complex reasoning, production apps
- Use **local** for sensitive data, development, offline work
- Use **hybrid** for cost optimization

## Examples

See these workflow files:
- `workflows/local_ollama_chat.yaml` - Basic local chat
- `workflows/local_autonomous_agent.yaml` - Offline reasoning agent
- `workflows/local_chain_agent.yaml` - Multi-step pipeline
- `workflows/hybrid_cloud_local_agent.yaml` - Cloud + local mix

## Resources

- **Ollama**: https://ollama.ai
- **Models**: https://ollama.ai/library
- **Flyto2 Modules**: [MODULES.md](MODULES.md)
- **DSL Reference**: [DSL.md](DSL.md)

## Next Steps

1. Install Ollama
2. Run example workflows
3. Build your own local AI agents
4. Contribute new local AI modules!

---

**Questions?** Open an issue on [GitHub](https://github.com/flytohub/flyto2/issues)
