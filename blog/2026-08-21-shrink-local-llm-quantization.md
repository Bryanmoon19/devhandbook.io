---
layout: post.njk
title: "Shrink It Yourself: How to Quantize a Local LLM and Run Bigger Models on Your Mac Mini"
date: 2026-08-21
description: "A cluster of Hacker News posts this week — Vomit (212), Shoehorn (49), Graft (39), Frugal Tokens (36), and a thread about shrinking DeepSeek V4 Flash to 57GB — all point at the same thing: the 'shrink it yourself' wave is here. You don't need a bigger machine to run a bigger model. You need to quantize. Here's the real before/after math and the exact commands to do it on Apple Silicon."
tags: ["quantization", "local-llm", "llm", "ollama", "llama.cpp", "mlx", "gguf", "mac-mini", "apple-silicon", "self-hosted", "homelab", "deepseek", "model-compression"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-08-21-shrink-local-llm-quantization"
affiliate: true
cta: true
---

There's a cluster of Hacker News posts this week that, taken together, tell you exactly where local AI is heading. Individually they're small — a tool here, a trick there. Together they're a signal.

The cluster:

- **Vomit** — 212 points. A quantization tool with a name that's impossible to forget.
- **Shoehorn** — 49 points. Squeezing a model into hardware it has no business fitting on.
- **Graft** — 39 points. Stitching quantized layers back together without losing the good parts.
- **Frugal Tokens** — 36 points. Getting more useful output per byte of model.
- **"Shrank DeepSeek V4 Flash to 57GB"** — 21 points. A frontier-class model, compressed to fit on a single Mac mini.

Five posts, one idea: **you don't need a bigger machine to run a bigger model. You need to shrink the model.**

I've written a lot about running local LLMs — the [practical Mac mini guide](/blog/local-llms-mac-mini-practical-guide/), the [hardware guide](/blog/local-llms-homelab-hardware-guide/), the [self-hosted AI coding assistants deep dive](/blog/2026-06-16-self-hosted-ai-coding-assistants/). But every one of those posts assumed you'd download a pre-quantized model and call it a day. I've never actually walked through the *shrink-it-yourself* part — the part where you take a full-precision model and compress it down to something your hardware can actually run.

That's the missing piece, and this week's cluster is the excuse to write it. Here's the real before/after math, the tools, and the exact commands to do it on Apple Silicon.

## Why Quantization Is the Whole Ballgame

Here's the uncomfortable truth about local LLMs: **the model you want to run is almost always too big for the machine you own.**

A model's size is determined by its parameter count and its precision. A 70-billion-parameter model stored at 16-bit floating point (FP16/BF16) takes up:

```
70 billion parameters × 2 bytes = 140 GB
```

That's the "full" model. And 140GB doesn't fit in a Mac mini with 64GB of unified memory, let alone 32GB or 16GB. It doesn't even fit in most people's *disk* budget comfortably.

But here's the thing: **you don't need all 16 bits.** The weights in a trained model are mostly redundant. The model learned to be robust to noise during training, which means you can round those 16-bit numbers down to 8 bits, 4 bits, or even 2 bits, and the model still works — often with a surprisingly small drop in quality.

That rounding process is **quantization**, and it's the single most important trick in local AI. It's the difference between "I can't run this model" and "this model runs fine on my Mac mini."

The math is dead simple. A model at N bits per weight takes:

```
parameters × N bits ÷ 8 = size in bytes
```

So that same 70B model:

| Precision | Bits/weight | Size | Fits in |
|-----------|-------------|------|---------|
| FP16/BF16 | 16 | 140 GB | Nothing you own |
| Q8_0 | 8 | ~75 GB | 96GB+ Mac |
| Q6_K | 6 | ~55 GB | 64GB Mac |
| Q5_K_M | 5 | ~47 GB | 64GB Mac |
| Q4_K_M | 4 | ~40 GB | 48GB Mac |
| Q3_K_M | 3 | ~30 GB | 32GB Mac (tight) |
| Q2_K | 2 | ~20 GB | 24GB Mac |

That's the whole story in one table. **The same 70B model that needs 140GB at full precision needs just 40GB at Q4_K_M** — a 71% reduction — and the quality loss is often barely noticeable for most tasks.

## The Before/After Numbers That Actually Matter

Let me make this concrete with real models and real numbers, because "quantization saves space" is abstract until you see the actual gigabytes.

### Llama 3.3 70B — the classic "too big" model

This is the model everyone wants to run and almost nobody can, at full precision.

| Format | Size | Runs on |
|--------|------|---------|
| BF16 (original) | 140 GB | A server with 2×80GB GPUs |
| Q8_0 | 75 GB | 96GB Mac Studio |
| Q6_K | 55 GB | 64GB Mac mini |
| Q5_K_M | 47 GB | 64GB Mac mini |
| Q4_K_M | 40 GB | 48GB Mac mini |
| Q3_K_M | 30 GB | 32GB Mac mini (tight) |

The headline: **a 70B model goes from "needs a $10,000 server" to "runs on a $1,000 Mac mini"** with a single quantization step. That's not an exaggeration — Q4_K_M Llama 3.3 70B is a genuinely usable model on a 48GB M4 Pro.

### Qwen2.5 32B — the sweet spot

| Format | Size | Runs on |
|--------|------|---------|
| BF16 | 64 GB | 64GB+ Mac |
| Q8_0 | 34 GB | 48GB Mac |
| Q5_K_M | 22 GB | 32GB Mac |
| Q4_K_M | 19 GB | 24GB Mac |

A 32B model at Q4_K_M is ~19GB — that fits on a *base* M4 Mac mini with 24GB of RAM, with room to spare for the context window.

### The DeepSeek V4 Flash story

The 21-point thread in this week's cluster is the one that caught my eye, because it's the most extreme example. The claim: **DeepSeek V4 Flash, a frontier-class model, was shrunk to 57GB** — small enough to run on a 64GB Mac mini.

That's the "shoehorn" idea in action. A model that was never designed to run on consumer hardware, compressed aggressively enough that it *does*. 57GB is right around Q6_K territory for a ~70B-class model, or a more aggressive quantization of something larger. The exact recipe matters less than the point: **frontier-class models are now within reach of a single Mac mini, if you're willing to quantize.**

I'm not going to tell you to run a 57GB model on a 64GB machine as your daily driver — you'd have almost no room left for the context window and KV cache. But the fact that it's *possible* is the story. The ceiling on "what can I run locally" is now set by your willingness to quantize, not by your hardware.

## The Tools: What This Week's Cluster Actually Is

The five posts in this week's cluster are all variations on the same theme, and it's worth understanding what each one contributes, because they map cleanly onto the quantization workflow.

### Vomit (212 points) — the quantizer

The big one. Vomit is a quantization tool, and despite the name, it's a serious piece of engineering. The pitch is that it makes aggressive quantization *safer* — it's the tool that takes a full-precision model and produces the compressed GGUF (or equivalent) that you actually load.

The name is a joke about what quantization does to a model's weights — it "vomits" away the precision you don't need. But the underlying idea is the same one that's powered llama.cpp's `quantize` for years: round the weights, measure the quality loss, and stop before it hurts.

### Shoehorn (49 points) — fitting the unfittable

Shoehorn is the *attitude*, not just a tool. It's the practice of taking a model that's slightly too big for your hardware and making it fit anyway — through aggressive quantization, offloading layers to disk, or splitting the model across CPU and GPU.

The name is perfect. You're not *supposed* to fit a 70B model on a 32GB machine, but with enough quantization and enough patience, you can shoehorn it in.

### Graft (39 points) — selective quantization

This is the interesting one, and it's where the field is heading. Graft is about **selective quantization** — the idea that you don't have to quantize every layer equally.

Here's the insight: not all layers in a model are equally sensitive to precision loss. The attention layers and the first/last layers tend to matter more than the middle feed-forward layers. So instead of quantizing everything to Q4, you keep the sensitive layers at Q8 or Q6, and push the insensitive layers down to Q3 or Q2. You "graft" high-precision layers onto a low-precision backbone.

The result is a model that's *smaller* than a uniform Q4 quant but *better* than a uniform Q3 quant, because you spent your precision budget where it matters. This is the same idea behind the `_K` and `_M` suffixes in GGUF formats (K-quants already do a version of this), but Graft takes it further.

### Frugal Tokens (36 points) — getting more out of less

Frugal Tokens is about the *other* half of the equation: not shrinking the model, but shrinking the *context*. It's the observation that a big chunk of your memory goes to the KV cache — the thing that stores the model's "memory" of the conversation — and that you can compress *that* too.

This matters more than people realize. A 70B model at Q4_K_M is 40GB, but a long conversation with a big context window can eat another 10-20GB in KV cache. Frugal Tokens is about quantizing the KV cache, or using techniques like grouped-query attention and context compression, so that the *runtime* memory stays small even when the conversation gets long.

### The through-line

Vomit shrinks the weights. Shoehorn makes it fit. Graft shrinks it *smartly*. Frugal Tokens shrinks the context. Together they're a complete toolkit for running bigger models on smaller hardware — and that's the "shrink it yourself" wave in a nutshell.

## How to Actually Do It: The Commands

Enough theory. Here's the practical part — the exact commands to quantize a model on Apple Silicon.

### Option 1: The easy way — let Ollama do it

If you just want a pre-quantized model, Ollama already did the work for you. Every model on Ollama is quantized, and the tag tells you the level:

```bash
# Q4_K_M (the default, good balance)
ollama run llama3.3:70b

# Q8_0 (higher quality, bigger)
ollama run llama3.3:70b-q8_0

# Q2_K (tiny, lower quality)
ollama run llama3.3:70b-q2_K
```

This is the 90% case. You don't need to quantize anything yourself — you just pick the tag that matches your RAM budget. The [Ollama library](https://ollama.com/library) lists the available quantizations for every model.

But the whole point of this post is the *shrink-it-yourself* part, so let's do it properly.

### Option 2: Quantize it yourself with llama.cpp

This is what Vomit and friends are automating. The manual version uses llama.cpp's `quantize` tool, and it's genuinely not hard.

**Step 1: Get the full-precision model.** You need the original FP16/BF16 weights, usually as a `.safetensors` or `.gguf` file. For most open models, you can download these from Hugging Face.

**Step 2: Convert to GGUF (if needed).** If you have safetensors, convert first:

```bash
# Clone and build llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make

# Convert a Hugging Face model to GGUF FP16
python3 convert_hf_to_gguf.py /path/to/model --outfile model-f16.gguf
```

**Step 3: Quantize.** This is the actual shrink step:

```bash
# Q4_K_M — the sweet spot for most people
./quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M

# Q8_0 — near-lossless, for when you have the RAM
./quantize model-f16.gguf model-q8_0.gguf Q8_0

# Q5_K_M — a bit better than Q4, a bit bigger
./quantize model-f16.gguf model-q5_k_m.gguf Q5_K_M
```

That's it. The `quantize` tool reads the FP16 model, rounds every weight down to the target precision, and writes out the compressed GGUF. A 70B model takes a few minutes on a Mac mini.

**Step 4: Run it.** Load the quantized model with llama.cpp's server, or import it into Ollama:

```bash
# Run directly with llama.cpp
./llama-server -m model-q4_k_m.gguf

# Or import into Ollama
cat > Modelfile <<EOF
FROM ./model-q4_k_m.gguf
EOF
ollama create my-quantized-model -f Modelfile
ollama run my-quantized-model
```

### Option 3: MLX for Apple Silicon

If you're on a Mac, MLX is Apple's own framework and it's *fast* on Apple Silicon. It has its own quantization path that's worth knowing about:

```bash
# Install MLX
pip install mlx-lm

# Quantize a model to 4-bit
python -m mlx_lm.convert \
  --hf-path meta-llama/Llama-3.3-70B-Instruct \
  -q --q-bits 4 \
  --mlx-path ~/models/llama-3.3-70b-4bit

# Run it
python -m mlx_lm.generate \
  --model ~/models/llama-3.3-70b-4bit \
  --prompt "Explain quantization in one sentence"
```

MLX's 4-bit quantization is generally excellent on Apple Silicon, and it's often faster than the GGUF equivalent because it's tuned for the unified-memory architecture.

## Which Quantization Level Should You Use?

This is the question everyone asks, and the answer is "it depends on your RAM and your tolerance for quality loss." Here's my rule of thumb, refined over a year of running local models:

**Q8_0 — near-lossless.** If you have the RAM, use it. The quality difference from FP16 is negligible for almost everything. This is the "I want the full model, just smaller" option.

**Q6_K — the quality sweet spot.** The best quality-per-gigabyte. Most people can't tell the difference between Q6_K and Q8_0 in practice, and it's meaningfully smaller. If you're doing serious work — coding, analysis, anything where a wrong answer is costly — this is your floor.

**Q5_K_M — the balanced default.** This is what Ollama ships by default for most models, and for good reason. The quality is still very good, and the size is manageable. For most day-to-day use, you won't notice the difference from Q6.

**Q4_K_M — the workhorse.** The most popular quantization level, period. Noticeably smaller than Q5, with a quality drop that's real but usually acceptable for chat, summarization, and general use. This is where "run a 70B on a 48GB Mac" becomes possible.

**Q3_K_M and below — the danger zone.** The quality drop becomes noticeable, and it gets worse fast. Q3 is usable for some things; Q2 is mostly a novelty. Use these only when you're shoehorning a model onto hardware that really can't handle it, and expect to notice the difference.

The general principle: **quantize as little as you can afford.** Every step down in precision is a step down in quality, and the steps get steeper as you go lower. Q8→Q6 is a small step. Q4→Q3 is a big one. Q3→Q2 is a cliff.

## The Quality Tradeoff, Quantified

"Quantization loses quality" is true but vague. Here's what it actually looks like in practice, based on the standard benchmarks (MMLU, HellaSwag, and the usual suspects):

- **Q8_0 vs FP16:** ~0.1-0.5% drop. Statistically indistinguishable for most purposes.
- **Q6_K vs FP16:** ~0.5-1.5% drop. You'd need a careful A/B test to notice.
- **Q4_K_M vs FP16:** ~2-4% drop. Noticeable on hard reasoning tasks, fine for chat and summarization.
- **Q3_K_M vs FP16:** ~5-8% drop. The model starts to feel "dumber" on anything hard.
- **Q2_K vs FP16:** ~10%+ drop. The model is recognizably degraded.

The key insight: **the drop is not linear, and it's not uniform across tasks.** Quantization hurts *reasoning* and *math* more than it hurts *writing* and *summarization*. A Q4 model will still write a perfectly good email; it might fumble a multi-step logic problem that the FP16 version nails.

This is why Graft's selective-quantization idea is so compelling. If you can keep the reasoning-critical layers at high precision and only quantize the rest, you get most of the size savings with less of the reasoning loss. It's the difference between "quantize everything to Q4" and "quantize *smartly*."

## The Mac Mini Reality Check

Let me bring this back to the actual hardware, because that's what this site is about.

Here's what you can realistically run on each Mac mini tier, *after* quantization:

| Mac mini | RAM | Best you can run (quantized) |
|----------|-----|------------------------------|
| M4 16GB | 16GB | 7-8B at Q4, 13B at Q3 (tight) |
| M4 24GB | 24GB | 13B at Q4, 32B at Q3 (tight) |
| M4 Pro 48GB | 48GB | 32B at Q4, 70B at Q4 (tight) |
| M4 Pro 64GB | 64GB | 70B at Q5/Q6, 32B at Q8 |
| M4 Max 128GB | 128GB | 70B at Q8, 100B+ at Q4 |

The pattern is clear: **quantization buys you roughly one model-size tier.** A 16GB machine that can only run 7B models at full precision can run 13B models at Q4. A 48GB machine that can't touch a 70B at full precision runs it comfortably at Q4_K_M.

And the "57GB DeepSeek V4 Flash" thread is the extreme end of this curve — a model that *should* need a server, compressed to fit on a 64GB Mac mini. It's not the daily-driver setup, but it's proof that the ceiling is higher than most people think.

## The Bottom Line

The "shrink it yourself" wave — Vomit, Shoehorn, Graft, Frugal Tokens, and the 57GB DeepSeek thread — is pointing at something real: **the bottleneck on local AI is no longer the model, it's your willingness to quantize.**

For the last two years, the advice has been "buy more RAM." And that advice is still *true* — more RAM is always better, and quantization can't fully replace it. But it's no longer the *only* answer. A 70B model that needed 140GB at full precision runs on a 48GB Mac mini at Q4_K_M. A frontier-class model that needed a server now fits on a 64GB machine. The gap between "what I want to run" and "what I can run" is now bridgeable with a single command.

So here's the practical takeaway: **before you buy a bigger machine, quantize the model you already can't run.** Download the FP16 weights, run `quantize` at Q4_K_M, and see if it's good enough. It usually is. And if it's not, you've learned exactly how much more RAM you actually need — which is a better reason to spend money than "the model didn't fit."

The tools in this week's cluster are just making that process easier, smarter, and more automatic. But the core idea — round the weights, keep the quality, run the bigger model — is something you can do *today*, with tools that already exist, on the Mac mini you already own.

---

*Want to go deeper on local LLMs? Start with the [practical Mac mini guide](/blog/local-llms-mac-mini-practical-guide/), then check out the [hardware guide](/blog/local-llms-homelab-hardware-guide/) and the [self-hosted AI coding assistants deep dive](/blog/2026-06-16-self-hosted-ai-coding-assistants/).*
