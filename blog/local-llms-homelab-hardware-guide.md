---
layout: post.njk
title: "Local LLMs for Homelab: Which Model Runs Best on Your Hardware"
date: 2026-04-12
description: "Stop guessing. Match the right local LLM to your actual homelab hardware — from Intel N100 mini PCs to RTX GPU servers. Real benchmarks, use-case picks, and quant explained."
tags: ["ollama", "local-llm", "proxmox", "homelab", "ai", "self-hosted", "hardware"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/local-llms-homelab-hardware-guide"
---

The hardest part of running local LLMs isn't the installation — it's knowing which model to run on the hardware you actually own. Pull a 70B model on a 16GB machine and the system crawls. Run a 1B model on a GPU server and you're leaving performance on the table.

This guide matches homelab hardware to the right local LLM, with real benchmarks, specific model + quantization recommendations, and zero guesswork. Whether you're on a fanless Intel N100 or a Proxmox box with an RTX 3060, here's exactly what to run.

## How to Read This Guide

**Two numbers determine whether a local LLM runs well on your machine: RAM capacity and memory bandwidth.** VRAM on a GPU is even better than system RAM because it's attached to thousands of CUDA cores. But if you don't have a GPU, CPU inference relies entirely on your system's DDR4/DDR5 bandwidth.

The tables below use these abbreviations:

- **Q4_K_M** = 4-bit quantized, medium quality. ~75% of full model quality at ~25% of the size. The sweet spot for most homelab use.
- **Q5_K_M** = 5-bit quantized, higher quality. Slightly larger, slightly better reasoning. Good if you have the VRAM/RAM headroom.
- **Q8_0** = 8-bit quantized. Very close to unquantized quality. Best for small models on capable hardware.
- **t/s** = tokens per second. Higher is better. >10 t/s feels responsive. >30 t/s feels instant.

## Tier 1: Entry-Level (8–16GB RAM, No GPU)

**Best models: 1B–3B parameter models at Q4_K_M or Q8_0.**

This is the Intel N100, an old laptop, or a lightweight Proxmox LXC with 8GB allocated. You won't run Llama 70B here, but you can still get surprisingly useful AI for home automation, quick summarization, and basic coding help.

| Model | Quant | Size | Speed (CPU) | Best For |
|-------|-------|------|-------------|----------|
| `qwen2.5:1.5b` | Q4_K_M | ~1.1GB | 15–25 t/s | Home Assistant voice, simple Q&A |
| `llama3.2:1b` | Q4_K_M | ~1.3GB | 20–35 t/s | Fastest responses, basic tasks |
| `gemma3:1b` | Q4_K_M | ~0.8GB | 18–30 t/s | Google ecosystem fans, lightweight chat |
| `qwen2.5:3b` | Q4_K_M | ~1.9GB | 10–18 t/s | Better reasoning than 1B, still snappy |
| `qwen2.5-coder:1.5b` | Q4_K_M | ~1.1GB | 15–25 t/s | Tiny code completions, shell scripts |

**Real benchmark from my setup:** Qwen2.5 1.5B Q4_K_M on an Intel i9-13900H (LXC, 2 cores, 4GB RAM) runs at **21 t/s generation** and **55 t/s prompt processing**[^1]. On an N100, expect roughly half that — still perfectly usable for Home Assistant or quick CLI queries.

**Recommended hardware in this tier:**
- [Intel N100 Mini PC](https://www.amazon.com/dp/B0CWJ3X2JH?tag=devhandbook26-20) — Fanless, ~$150, sips power, perfect for a dedicated Ollama box.
- [Beelink EQ13 (N200)](https://www.amazon.com/dp/B0D9C4V7XQ?tag=devhandbook26-20) — Slightly faster than N100, still silent and cheap.

## Tier 2: Mid-Range (16–32GB RAM, No GPU or iGPU)

**Best models: 7B–9B parameter models at Q4_K_M or Q5_K_M.**

This is the sweet spot for most homelabbers. A 16GB Mac mini, a 32GB Proxmox host, or a Ryzen mini PC with integrated graphics. You can run capable general-purpose and coding models that rival early ChatGPT quality for many tasks.

| Model | Quant | Size | Speed (CPU) | Best For |
|-------|-------|------|-------------|----------|
| `llama3.1:8b` | Q4_K_M | ~4.9GB | 8–15 t/s | General chat, long context (128k) |
| `qwen2.5:7b` | Q4_K_M | ~4.4GB | 8–14 t/s | Strong reasoning, Chinese/English bilingual |
| `gemma3:4b` | Q4_K_M | ~3.2GB | 12–20 t/s | Fast, good quality, Google-trained |
| `qwen2.5-coder:7b` | Q4_K_M | ~4.7GB | 7–12 t/s | Best free coding model in this tier |
| `mistral:7b` | Q4_K_M | ~4.1GB | 8–14 t/s | Apache 2.0 license, clean for commercial use |
| `llama3.1:8b` | Q5_K_M | ~5.8GB | 6–10 t/s | Better reasoning if you have 32GB RAM |

**Practical note:** If you have exactly 16GB system RAM and want to run an 8B model, close browsers and other heavy apps. The model needs ~5GB just to load, and your OS needs 2–3GB. 16GB is the *floor* for this tier. 32GB is comfortable.

**iGPU bonus:** AMD 780M integrated graphics (Ryzen 7 7840HS) can run 7B models via ROCm at **15–30 t/s** — nearly GPU speeds without buying a discrete card.

**Recommended hardware:**
- [Beelink SER7 (Ryzen 7 7840HS)](https://www.amazon.com/dp/B0CR1JNMXL?tag=devhandbook26-20) — iGPU via ROCm, 32GB DDR5, runs 7B models beautifully.
- [32GB DDR5 SO-DIMM Kit](https://www.amazon.com/dp/B0C9V3HD87?tag=devhandbook26-20) — Must-have upgrade to escape the 16GB bottleneck.

## Tier 3: Enthusiast (32–64GB RAM, or 12GB+ VRAM GPU)

**Best models: 13B–14B models at Q4_K_M, or 8B models at Q8_0 / FP16.**

Now you're in the range where local LLMs genuinely compete with cloud APIs for quality. A used RTX 3060 12GB, an RTX 4060 Ti 16GB, or a 64GB Proxmox server opens up much larger models with fast inference.

| Model | Quant | Size | Speed (GPU) | Best For |
|-------|-------|------|-------------|----------|
| `qwen2.5:14b` | Q4_K_M | ~8.9GB | 20–35 t/s | Excellent reasoning, coding, analysis |
| `llama3.1:70b` | Q4_K_M | ~40GB | 3–8 t/s | Best quality, but needs 48GB+ VRAM for fast inference[^2] |
| `deepseek-r1:14b` | Q4_K_M | ~9.0GB | 15–28 t/s | Open-source reasoning model, math/logic champion |
| `qwen2.5-coder:14b` | Q4_K_M | ~8.5GB | 18–32 t/s | Serious local coding assistant |
| `llama3.1:8b` | Q8_0 | ~8.3GB | 15–25 t/s | Near-unquantized quality on mid GPUs |
| `gemma3:12b` | Q4_K_M | ~8.1GB | 18–30 t/s | Strong multi-turn chat, Google model |

**GPU vs CPU at this tier:** A 14B model on CPU (fast DDR5) might give you 4–8 t/s. The same model on an RTX 3060 12GB hits 20–30 t/s. The GPU upgrade is worth it if you interact with the LLM daily.

**VRAM rule of thumb:** You need roughly 1GB of VRAM for every 1.5–2B parameters at Q4_K_M. So:
- **RTX 3060 12GB** → up to 13B–14B models fully offloaded
- **RTX 4060 Ti 16GB** → up to 14B comfortably, or 70B with CPU offload (slower)
- **RTX 3090 / 4090 24GB** → 70B Q4_K_M fully GPU-resident, 20–40 t/s

**Recommended hardware:**
- [NVIDIA RTX 3060 12GB](https://www.amazon.com/dp/B08WR34RFY?tag=devhandbook26-20) — The value king for home LLMs. Used market is ~$200.
- [NVIDIA RTX 4060 Ti 16GB](https://www.amazon.com/dp/B0C9KLS6BN?tag=devhandbook26-20) — Future-proofing for 30B+ models.
- [Samsung 990 Pro 2TB NVMe](https://www.amazon.com/dp/B0BHJJ9Y77?tag=devhandbook26-20) — Models load from disk first; fast NVMe reduces cold-start time.

## Tier 4: Power User (64GB+ RAM, 24GB+ VRAM, or Multi-GPU)

**Best models: 30B–70B parameters at Q4_K_M, or vision models with image understanding.**

This is dual RTX 3090s, a Mac Studio with 64GB unified memory, or a threaded-ripper server with 128GB RAM. You're running models that rival GPT-4o-mini and sometimes GPT-4o on specific tasks.

| Model | Quant | Size | Speed | Best For |
|-------|-------|------|-------|----------|
| `llama3.3:70b` | Q4_K_M | ~40GB | 8–20 t/s | Near-frontier quality, general purpose |
| `qwen2.5:32b` | Q4_K_M | ~20GB | 12–25 t/s | Coding and reasoning powerhouse |
| `mixtral:8x7b` | Q4_K_M | ~26GB | 10–20 t/s | Sparse MoE model, excellent reasoning |
| `gemma3:27b` | Q4_K_M | ~17GB | 12–22 t/s | Vision + text, Google multimodal flagship |
| `llava:34b` | Q4_K_M | ~20GB | 5–12 t/s | Describe images locally with high accuracy |

**MoE models note:** Models like Mixtral 8x7b and Qwen2.5-MoE use "sparse" activation — only a subset of parameters fire per token. This means a 47B-parameter MoE model might run as fast as a 13B dense model during inference. They're some of the most efficient ways to get high quality on limited VRAM.

## Use-Case Quick Picks

Don't want to think about tiers? Here's the right model for common homelab jobs:

| What You Want | Best Model | Hardware Needed |
|---------------|-----------|-----------------|
| Home Assistant voice assistant | `llama3.2:1b` or `qwen2.5:1.5b` | 8GB RAM |
| Daily chat / general knowledge | `llama3.1:8b` Q4_K_M | 16GB RAM |
| Coding helper | `qwen2.5-coder:7b` or `14b` | 16GB+ RAM / 12GB+ VRAM |
| Document summarization (long books) | `llama3.1:8b` or `qwen2.5:14b` | 16GB+ RAM — 128k context |
| Write blog posts / creative writing | `llama3.3:70b` or `qwen2.5:32b` | 24GB+ VRAM / 64GB RAM |
| Math / logic / reasoning | `deepseek-r1:14b` or `32b` | 16GB+ VRAM |
| Describe security camera events | `llava:7b` or `gemma3:4b` | 8GB+ RAM / 8GB+ VRAM |
| Build a RAG pipeline (chat with docs) | `nomic-embed-text` + `llama3.1:8b` | 16GB RAM |

## Understanding Quantization

**Quantization is the single most important concept for matching models to hardware.**

LLMs are trained with 16-bit or 32-bit floating-point weights (FP16 / FP32). A 7B model at FP16 needs ~14GB just to load. Quantization squishes those weights into 4-bit or 5-bit integers, slashing memory use at a modest quality cost.

| Precision | Bits per Weight | 7B Model Size | Quality vs FP16 |
|-----------|-----------------|---------------|-----------------|
| FP16 | 16 | ~14GB | 100% (baseline) |
| Q8_0 | 8 | ~7.5GB | ~98% |
| Q5_K_M | 5 | ~5.2GB | ~88% |
| Q4_K_M | 4 | ~4.1GB | ~78% |
| Q3_K_M | 3 | ~3.2GB | ~65% |
| Q2_K | 2 | ~2.4GB | ~45% |

**My recommendation:** Stick to Q4_K_M for almost everything. It's the best balance of size, speed, and quality. Only go to Q5_K_M or Q8_0 if you have the VRAM headroom and notice the model struggling with complex reasoning. Avoid Q3 and below unless you're experimenting on very constrained hardware.

## Proxmox & LXC Tips

If you're running Ollama inside Proxmox like I am, here are three practical tips:

1. **Allocate 2GB more RAM than the model size.** A 7B Q4_K_M model loads at ~4.5GB, but inference needs working memory. Give the LXC at least 6–8GB.

2. **Bind-mount model storage to your NAS or a large local disk.** Models live in `/root/.ollama/models/`. Symlink that to a larger volume so your root disk doesn't fill up:
   ```bash
   mkdir -p /mnt/nas/ollama-models
   ln -s /mnt/nas/ollama-models /root/.ollama/models
   ```

3. **Snapshot before experimenting.** Proxmox makes this trivial. I always snapshot the Ollama LXC before pulling a 20GB+ model. If it doesn't run well, restore in 10 seconds instead of re-downloading.

For the full Ollama-on-Proxmox setup, see the [step-by-step guide](/blog/ollama-proxmox-lxc/).

## Final Thoughts

You don't need a $3,000 GPU to run useful local LLMs. A $150 Intel N100 running `llama3.2:1b` is enough for a private Home Assistant voice assistant. A used RTX 3060 opens up 14B models that code, reason, and write at a level that would have required API credits a year ago.

The key is matching the model size and quantization to the RAM or VRAM you actually have. Start with Q4_K_M, measure tokens per second, and upgrade your hardware only after you've proven the use case.

---

<div class="affiliate-disclosure">Some links above are affiliate links — I earn a small commission at no extra cost to you. I only recommend hardware I've personally used or researched for homelab use.</div>

## Related Posts

- [Run Ollama on Proxmox LXC (Full Setup Guide)](/blog/ollama-proxmox-lxc/) — Installation, GPU passthrough, and Home Assistant integration
- [Proxmox Home Assistant LXC Setup](/blog/proxmox-home-assistant-lxc/) — Build the foundation for local smart-home AI

---

[^1]: Benchmark from LXC 1004 on Intel i9-13900H, 2 cores allocated, 4GB RAM, CPU backend via llama.cpp. Your results will vary with CPU generation, RAM speed, and thread allocation.
[^2]: 70B models at Q4_K_M need ~40GB VRAM for full GPU offload at good speeds. On 24GB VRAM, partial CPU offload works but drops to 2–5 t/s.

*Questions or benchmark data from your own setup? The source for this post is on [GitHub](https://github.com/bryanmoon19/devhandbook.io). PRs welcome.*
