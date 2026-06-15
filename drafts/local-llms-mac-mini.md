# Running Local LLMs on Your Mac Mini: A Practical Guide

There's something deeply satisfying about running a large language model on your own hardware. No API keys, no rate limits, no wondering where your data goes. Just you, your Mac Mini, and a machine that can write code, summarize documents, or brainstorm ideas — completely offline.

I spent the last few months turning my M4 Mac Mini into a local AI workhorse. It started as an experiment and quickly became my default setup for coding, writing, and quick research tasks. Here's everything I learned, condensed into a guide that'll save you the trial and error.

---

## Why Run Local LLMs?

Before diving into the how, let's talk about the why. Local LLMs aren't for everyone, but they solve some real problems:

**Privacy.** Your prompts never leave your machine. No training on your data, no third-party access, no compliance headaches. This matters if you work with proprietary code, sensitive documents, or just value keeping your thoughts private.

**Cost.** Cloud API bills add up fast. At the time of writing, GPT-4o costs $5 per million input tokens and $15 per million output tokens. For heavy usage — daily coding assistance, document analysis, creative writing — you can burn through $50-100/month easily. A Mac Mini pays for itself.

**Speed.** No network latency. On Apple Silicon with unified memory, inference can be surprisingly fast for models under 10B parameters. Sub-second responses for coding suggestions beat waiting on a round-trip to OpenAI's servers.

**Reliability.** No downtime, no rate limits, no "service temporarily unavailable." Your model works whether you're on a plane, in a cabin, or your ISP is having a bad day.

**Customization.** Want to fine-tune on your codebase? Run a model with a 128K context window? Experiment with quantization levels? Local gives you control cloud APIs don't.

The trade-offs? You won't run GPT-4-class models locally. The best locally-runnable models today are comparable to GPT-3.5 or early GPT-4, depending on size. But for many tasks, that's plenty.

---

## What You Need: Hardware Reality Check

### The Short Version

- **M1 Mac Mini (8GB):** Can run 3B-7B models. Tight but functional.
- **M2/M3 Mac Mini (16GB):** Sweet spot. Comfortable with 7B-13B models.
- **M4 Mac Mini (24GB+):** Ideal. Runs 13B-30B models, or multiple smaller ones simultaneously.
- **Intel Mac Mini:** Technically possible with CPU inference, but painfully slow. Not recommended.

### Why RAM Matters More Than You Think

Apple Silicon uses unified memory — your RAM is your VRAM. A 7B parameter model at 4-bit quantization needs roughly:

```
7 billion parameters × 4 bits ÷ 8 bits/byte = ~3.5GB
```

But you also need memory for the context window, KV cache, and overhead. Real-world rule of thumb: you need 1.5-2x the model size in RAM. So that 3.5GB model actually wants 6-8GB to run comfortably.

For context, here's what fits where:

| Mac Mini | Usable RAM | Approx Model Size | Example Models |
|----------|-----------|-------------------|----------------|
| M1 8GB | ~6GB | Up to 4B | Phi-3 Mini, TinyLlama, Qwen2.5-3B |
| M2 16GB | ~12GB | Up to 7B | Llama 3.1 8B, Qwen2.5-7B, Gemma2 9B |
| M4 24GB | ~20GB | Up to 14B | Qwen2.5-14B, Llama 3.3 70B (Q4) — tight |
| M4 Pro 48GB+ | ~40GB | Up to 30B | Full 70B models at lower quantization |

The M4's improved memory bandwidth (up to 273 GB/s on Pro/Max) makes a noticeable difference in token generation speed compared to M1/M2.

---

## The Tools: Four Ways to Run Local LLMs

### 1. Ollama — The Easy Button

**Best for:** Getting started quickly, CLI users, simple deployments

Ollama is the fastest path to a working local LLM. One command install, one command download, one command run. It handles model formats, quantization, and the server automatically.

```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull qwen2.5:7b

# Run interactively
ollama run qwen2.5:7b

# Or start the API server
ollama serve
```

Ollama's killer feature is its model library. Want Qwen? `ollama pull qwen2.5:7b`. Want Llama? `ollama pull llama3.1:8b`. It Just Works™.

The API is OpenAI-compatible (mostly — more on that later), so tools like OpenWebUI, Continue.dev, or custom scripts drop right in.

### 2. LM Studio — The GUI Experience

**Best for:** Non-technical users, model comparison, quick experiments

LM Studio is a polished desktop app for browsing, downloading, and chatting with models. No terminal required.

- Browse Hugging Face models with one-click download
- Chat interface with history, system prompts, and parameter tuning
- Built-in server mode with OpenAI-compatible API
- GPU acceleration via Metal on Apple Silicon

Download from [lmstudio.ai](https://lmstudio.ai), pick a model from the sidebar, and start chatting. It's the most approachable option for anyone uncomfortable with the command line.

### 3. llama.cpp — The Lightweight Option

**Best for:** Minimal resource usage, custom builds, embedded systems

llama.cpp is the C++ inference engine that powers much of the local LLM ecosystem. It's what Ollama uses under the hood.

```bash
# Clone and build (requires CMake)
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DLLAMA_METAL=ON
cmake --build build --config Release

# Convert and run a model
./build/bin/llama-cli -m ~/models/qwen2.5-7b-q4_k_m.gguf -p "Explain quantum computing"
```

You trade convenience for control. llama.cpp exposes every knob: thread count, batch size, memory mapping, context size, sampling parameters. If you need to squeeze performance out of limited hardware, this is where you go.

### 4. MLX — Apple Silicon Optimized

**Best for:** Maximum performance on Apple Silicon, research, fine-tuning

Apple's MLX framework is purpose-built for their chips. It uses unified memory efficiently and can be significantly faster than generic implementations for certain workloads.

```bash
# Install
pip install mlx-lm

# Run a model
python -m mlx_lm.server --model mlx-community/Qwen2.5-7B-Instruct-4bit

# Or in Python
from mlx_lm import load, generate
model, tokenizer = load("mlx-community/Qwen2.5-7B-Instruct-4bit")
response = generate(model, tokenizer, prompt="Hello, world!")
```

MLX shines for fine-tuning (LoRA support is excellent) and when you want the absolute best inference speed on Apple Silicon. The trade-off is a smaller model selection — not every Hugging Face model has an MLX conversion.

---

## Step-by-Step: Ollama Setup on Mac Mini

Let's walk through a complete setup. I'll use Ollama because it's the easiest entry point, but the concepts apply everywhere.

### Step 1: Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This installs the `ollama` CLI and a LaunchAgent that keeps the server running in the background.

### Step 2: Verify Installation

```bash
ollama --version
# ollama version 0.5.x

ollama list
# NAME    ID    SIZE    MODIFIED
# (empty — no models yet)
```

### Step 3: Download Your First Model

```bash
# Good all-rounder, ~4.5GB
ollama pull qwen2.5:7b

# For coding tasks, ~4GB
ollama pull codellama:7b

# Small and fast, ~2GB
ollama pull phi3:medium
```

Downloads are resumable and cached. Models live in `~/.ollama/models/`.

### Step 4: Test It

```bash
ollama run qwen2.5:7b
>>> Write a Python function to flatten a nested list

def flatten(nested_list):
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
```

Exit with `/bye` or Ctrl+D.

### Step 5: Start the API Server

```bash
ollama serve
```

By default, it listens on `localhost:11434`. Test it:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "Why is the sky blue?"
}'
```

---

## Model Recommendations by Use Case

### General Chat & Reasoning

| Model | Size | Quantization | Speed* | Quality |
|-------|------|-------------|--------|---------|
| Qwen2.5 7B | 7B | Q4_K_M | ~35 tok/s | ⭐⭐⭐⭐ |
| Llama 3.1 8B | 8B | Q4_K_M | ~32 tok/s | ⭐⭐⭐⭐ |
| Gemma 2 9B | 9B | Q4_K_M | ~28 tok/s | ⭐⭐⭐⭐ |
| Qwen2.5 14B | 14B | Q4_K_M | ~22 tok/s | ⭐⭐⭐⭐⭐ |

*Speed measured on M4 Mac Mini 24GB. Your mileage varies by quantization and context length.

Qwen2.5 is my daily driver. It handles instructions well, has a strong context window (128K), and the 7B version is fast enough for real-time use. Llama 3.1 is similarly capable with better English prose. Gemma 2 is Google's offering — slightly different "personality" but objectively strong.

### Coding Assistance

| Model | Size | Best For |
|-------|------|----------|
| CodeQwen 7B | 7B | General coding, fast completions |
| CodeLlama 7B | 7B | Python, C++, established codebase |
| DeepSeek-Coder 6.7B | 6.7B | Complex algorithms, math |
| Qwen2.5-Coder 7B | 7B | Best all-rounder for coding |

For VS Code integration via Continue.dev, I run Qwen2.5-Coder 7B. It generates sensible completions, explains code well, and debugs without hallucinating too aggressively.

### Small & Fast (Edge Cases)

| Model | Size | Use Case |
|-------|------|----------|
| Phi-3 Mini | 3.8B | Tight memory, simple tasks |
| TinyLlama 1.1B | 1.1B | Extremely fast, basic Q&A |
| Qwen2.5 3B | 3B | Good balance of size and capability |

Phi-3 Mini punches above its weight. On an 8GB Mac Mini, it's your best option for anything beyond toy problems.

---

## Performance Tuning

### Memory Usage

Ollama automatically picks a quantization based on your hardware, but you can override:

```bash
# Force a specific quantization level
ollama pull qwen2.5:7b-q4_K_M
ollama pull qwen2.5:7b-q8_0    # Higher quality, more RAM
```

Quantization levels (from smallest to largest):
- **Q2_K** — Aggressive compression. Smaller, noticeably dumber.
- **Q4_K_M** — Balanced. The default sweet spot.
- **Q5_K_M** — Better quality. Worth it for 13B+ models.
- **Q8_0** — Near-uncompressed. Best quality, ~2x the size of Q4.

### Context Window

Default context is usually 4096 or 8192 tokens. For long documents:

```bash
# Run with extended context
ollama run qwen2.5:7b --ctx-size 32768
```

More context = more KV cache = more RAM. A 7B model at 32K context uses significantly more memory than at 4K. Monitor with Activity Monitor.

### Metal GPU Acceleration

Ollama and llama.cpp automatically use Metal on Apple Silicon. Verify it's working:

```bash
ollama run qwen2.5:7b
# In another terminal:
ollama ps
# NAME              ID              SIZE      PROCESSOR    UNTIL
# qwen2.5:7b        xxx             4.5 GB    100% GPU     4 minutes from now
```

"100% GPU" means Metal is engaged. CPU-only fallback happens automatically if the model won't fit.

---

## Integration With Other Tools

### OpenWebUI (Previously Ollama WebUI)

A polished chat interface that connects to your Ollama instance:

```bash
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

Access at `http://localhost:3000`. Features: multi-model chats, document RAG, image generation integration, user management.

### Continue.dev (VS Code/Cursor)

The best coding assistant integration. Install the VS Code extension, point it at Ollama:

```json
{
  "models": [{
    "title": "Qwen2.5-Coder",
    "provider": "ollama",
    "model": "qwen2.5-coder:7b"
  }]
}
```

Get inline completions, chat, and codebase-aware answers powered by your local model.

### API Integration

Ollama's API is mostly OpenAI-compatible:

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

Most tools that support OpenAI's API work with minor configuration changes.

---

## The /v1 API Gotcha

Here's something that trips up almost everyone: **Ollama's OpenAI-compatible endpoints have quirks.**

The `/v1/chat/completions` endpoint works for basic chat, but:

1. **Tool calling** is supported by some models but not all. Check Ollama's docs for compatibility.
2. **System prompts** work differently than OpenAI. Some models ignore them unless formatted correctly.
3. **Streaming** is supported, but the SSE format has minor differences that break some clients.
4. **JSON mode** (`response_format: { type: "json_object" }`) requires specific model support.

If you're migrating from OpenAI, test thoroughly. Tools like LangChain and LiteLLM have Ollama-specific adapters that handle these quirks.

For the most reliable integration, use Ollama's native API (`/api/generate` and `/api/chat`) when possible, and only fall back to `/v1` when a tool requires it.

---

## Troubleshooting Common Issues

### "Error: model requires more system memory (X GB) than is available (Y GB)"

Your model + context window exceeds available RAM. Solutions:
- Use a smaller model
- Reduce context size: `OLLAMA_CONTEXT_LENGTH=4096 ollama run model`
- Use a more aggressive quantization
- Close other applications

### Slow generation (sub-10 tokens/second)

- Check if Metal is active: `ollama ps` should show "GPU"
- Try a smaller quantization (Q4 instead of Q8)
- Reduce context length
- For CPU-only fallback: more threads help, but not dramatically

### "Connection refused" when accessing API

- Ensure `ollama serve` is running
- Check `OLLAMA_HOST` environment variable
- Default bind is localhost only — set `OLLAMA_HOST=0.0.0.0` for LAN access (security implications!)

### Models download but won't run

- Check architecture: some models are Linux/CUDA only
- Verify you have enough disk space (`~/.ollama/models/`)
- Try `ollama rm modelname && ollama pull modelname` to re-download

### High memory pressure / swapping

macOS will compress memory and eventually swap to SSD. This tanks performance:
- Monitor with Activity Monitor's Memory tab
- Reduce model size or context if "Memory Used" nears physical RAM
- Consider quitting Safari tabs (they're memory hogs)

---

## Local vs Cloud: When to Use Which

**Use local when:**
- Privacy is paramount (proprietary data, personal projects)
- Cost matters (high-volume usage)
- You need offline access
- Latency matters (real-time coding assistance)
- You're experimenting with models/parameters

**Use cloud when:**
- You need frontier capability (GPT-4, Claude 3.5 Sonnet, Gemini Pro)
- One-shot tasks where setup time isn't worth it
- You need features unavailable locally (multimodal with high-res images, web search)
- Your hardware can't run adequate models

My workflow: Local for 80% of daily tasks (coding, writing, quick research), cloud for the 20% that needs the absolute best reasoning or multimodal capabilities.

---

## Conclusion

Running local LLMs on a Mac Mini isn't just a tech demo — it's a genuinely productive setup. An M2 or M4 Mac Mini with 16-24GB RAM can handle 7B-13B models at speeds that feel responsive for coding and writing tasks.

Start with Ollama. Pull Qwen2.5 7B. Install Continue.dev in VS Code. Within an hour, you'll have AI assistance that never phones home, never bills you, and works on airplanes.

The models will keep improving. The hardware will get faster. But the core advantage — owning your compute — only becomes more valuable as AI becomes more central to how we work.

Happy local inferencing.

---

*Have questions or found a model that works particularly well on your setup? The local LLM community moves fast — what's true today might be outdated next month. Experiment, share your findings, and iterate.*
