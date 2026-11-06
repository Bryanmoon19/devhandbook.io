---
layout: post.njk
title: "Self-Hosted Image Generation in 2026: A Reality-Check With a VRAM-vs-Model Table"
date: 2026-11-06
description: "Best self-hosted image generation model, run Stable Diffusion in Docker, and what your GPU can actually handle in 2026. A no-hype VRAM-vs-model table for SD1.5, SDXL, SD3.5, and FLUX — plus the exact Docker setup and a picker to cut through the guesswork."
tags: ["self-hosted", "image-generation", "stable-diffusion", "docker", "comfyui", "flux", "sdxl", "vram", "gpu", "ai", "homelab", "diffusion", "automatic1111"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-06-self-hosted-image-generation-2026"
affiliate: true
cta: true
---

Type "best self hosted image generation model" into Google and you'll get a wall of 2023-era Reddit threads, a few SEO listicles, and a lot of advice that was stale the moment FLUX shipped. Same with "self hosted stable diffusion docker" — half the results point at an `automatic1111` image that hasn't been the default in two years.

This post is a 2026 reality-check. No nostalgia for the SD1.5 era, no "just rent a GPU in the cloud" cop-out. Here's what actually runs well on the hardware you own *right now*, a VRAM-vs-model table you can trust, and the exact Docker setup I use — plus a tool idea that would have saved you (and me) a lot of time.

I've written at length about running local LLMs in this guide ([Local LLMs for Homelab](/blog/local-llms-homelab-hardware-guide/)), and the same "match the model to your actual hardware" lesson applies twice as hard to diffusion models. Image generation is *brutally* VRAM-hungry in a way LLM inference isn't.

## The Landscape Has Moved (Again)

If you haven't looked since 2023, here's the state of play:

- **SD1.5** (Stable Diffusion 1.5) is now the "runs on a potato" baseline. ~2GB VRAM, fast, but it shows its age. Still useful for quick drafts and low-end hardware.
- **SDXL** (Stable Diffusion XL, ~3.5B base + refiner) is the mature mid-tier. It's what most people *actually* land on in 2026 — good quality, reasonable VRAM, enormous ecosystem of fine-tunes and LoRAs.
- **SD3.5 / SD3 Medium** is the awkward middle child. Better than SDXL in some ways, but the licensing saga and mixed community adoption mean it's never really settled into the default slot.
- **FLUX.1** (Black Forest Labs) is the current quality king. FLUX.1 dev is open-weights and genuinely impressive, but it *wants* 12–24GB of VRAM and a beefy box. On a 8GB card you're running the quantized `fp8`/`nf4` variants, with real quality tradeoffs.
- **SANA, PixArt, Lumina** and a dozen other "efficient" architectures are chasing FLUX's quality at a fraction of the cost — worth watching, but not yet the safe default.

The short version: **SDXL is the pragmatic default in 2026, FLUX is the aspiration, and SD1.5 is the fallback.** Everything else is a bet.

## The VRAM-vs-Model Table

This is the table I wanted someone to give me two years ago. "Fits comfortably" means the model runs fully GPU-resident at a sane batch size and step count. "Tight" means it runs but you'll hit offload or need to drop resolution/batch.

| Model | VRAM (fp16) | VRAM (quantized) | Quality | Runs well on | Notes |
|-------|-------------|------------------|---------|--------------|-------|
| **SD1.5** | ~4GB | ~2GB | Good for drafts | 4GB–8GB cards | Fast, huge LoRA ecosystem, dated aesthetics |
| **SDXL** | ~8GB | ~6GB (fp8) | Very good | 8GB–12GB cards | The 2026 default. Sweet spot |
| **SD3.5 Medium** | ~10GB | ~7GB | Very good | 12GB cards | Good, but ecosystem is thinner |
| **FLUX.1 dev** | ~24GB | ~12GB (fp8), ~6GB (nf4) | Excellent | 16GB+ (fp8), 24GB ideal | Quality king, hungry. Quantized = tradeoffs |
| **SANA / PixArt** | ~6GB | ~4GB | Good–very good | 8GB cards | Efficient, promising, less mature |

**The rule of thumb:** diffusion models want roughly **1GB of VRAM per ~2 billion parameters at fp16** — and unlike LLMs, you can't cheat as hard with quantization because the image quality degrades visibly. An 8GB card comfortably owns SDXL; a 24GB card owns FLUX. Anything in between is a negotiation.

This is exactly the kind of math my [GPU VRAM Calculator](/gpu-vram-calculator/) does for LLMs — pick your GPU, see what fits. Diffusion needs a sibling of it, and I'll get to that at the end.

**Real-world example from my own box:** a 16GB card runs SDXL at 1024×1024 with zero drama, and FLUX.1 dev `fp8` at a *workable* but not snappy pace. A 12GB card is the realistic floor for FLUX `nf4`, and it's honestly more frustrating than fun. If FLUX is your goal, save for a 24GB card.

## The Docker Setup (2026 Edition)

"Self hosted stable diffusion docker" is a popular search for a reason — Docker is the cleanest way to run this stuff without poisoning your host with CUDA and Python-version hell. The short version: **use ComfyUI in 2026, not Automatic1111.**

Automatic1111's webui was the default for years, but it's now in maintenance mode, single-user-by-design, and increasingly painful to keep patched. ComfyUI is faster, node-based (better for repeatable workflows), multi-GPU aware, and has first-class FLUX support. There's also [SwarmUI](https://github.com/mcmonkeyprojects/SwarmUI) (a friendly frontend wrapping ComfyUI) if the node graph scares you off.

Here's the compose file I actually run:

```yaml
services:
  comfyui:
    image: ghcr.io/ai-dock/comfyui:latest
    container_name: comfyui
    ports:
      - "8188:8188"
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ./comfyui-data:/workspace
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped
```

Then:

```bash
docker compose up -d
# open http://localhost:8188
```

The `ghcr.io/ai-dock/comfyui` images ship with CUDA, torch, and the common custom nodes preinstalled — a huge time-saver over building your own image. Models go into `/workspace/models/checkpoints` (or the `unet` folder for FLUX). Drop your `.safetensors` files there, refresh, and you're rendering.

**Three gotchas that bite everyone:**

1. **VRAM isn't RAM.** A model that *downloads* fine doesn't *run* fine. Check the table above before you pull a 24GB checkpoint onto an 8GB card.
2. **`nvidia` driver + toolkit on the host first.** Docker doesn't give you CUDA for free — you need the NVIDIA Container Toolkit installed on the host or the `--gpus all` flag silently does nothing.
3. **Quantized ≠ free.** FLUX `nf4` fits on smaller cards but you'll see softness and artifacts. It's a tradeoff, not a cheat code.

For the LLM side of the same homelab, the [Local LLM Runtime Picker](/local-llm-runtime-picker/) asks you three questions and hands back the right runtime (Ollama vs llama.cpp vs vLLM vs LM Studio). Diffusion deserves the same treatment.

## The Tool Idea: A Self-Hosted Image-Model Picker

Here's where I put my money where my mouth is. I've built two adjacent tools for the LLM world:

- The **[GPU VRAM Calculator](/gpu-vram-calculator/)** — pick a GPU + model, see which quantizations actually fit in VRAM, with an estimated tokens/sec.
- The **[Local LLM Runtime Picker](/local-llm-runtime-picker/)** — answer three questions, get the right runtime for your hardware and use case.

What's missing is the **diffusion sibling**: a self-hosted image-model picker. The decision tree is basically:

1. **What GPU/VRAM do you have?** (4GB → SD1.5, 8GB → SDXL, 12GB → SD3.5, 24GB → FLUX)
2. **What are you making?** (drafts → SD1.5; general art → SDXL; photorealistic/professional → FLUX)
3. **How much do you care about speed vs quality?** (fast → SD1.5/SDXL; best → FLUX)
4. **Any specific need?** (anime/LoRA ecosystem → SDXL; text rendering → FLUX; efficiency → SANA)

Out pops a recommendation — *and* the matching `docker compose` snippet and the exact checkpoint name to download. That's the tool I want to build next, and it plugs directly into the same VRAM math the calculator already does for LLMs.

If that's something you'd use, tell me — [the source for this site is on GitHub](https://github.com/bryanmoon19/devhandbook.io), and I build tools people actually ask for.

## The Honest Verdict

Self-hosting image generation in 2026 is genuinely good, and genuinely *hardware-gated*. There's no software trick that turns an 8GB card into a 24GB card — quantization gets you maybe 50% more headroom, and then physics wins.

**If you have 8GB:** run SDXL and be happy. It's fast, the quality is legitimately good, and the LoRA ecosystem is massive. Don't chase FLUX.

**If you have 12–16GB:** SDXL is effortless, FLUX `fp8`/`nf4` is a real option if you're patient. This is the comfort zone.

**If you have 24GB+:** FLUX.1 dev is the answer. It's the best open-weights image model you can run at home, full stop.

The frustrating part isn't the software — it's the *selection* problem. Too many models, too many VRAM numbers, too much stale advice. That's why I built the [VRAM calculator](/gpu-vram-calculator/) for LLMs, and why a diffusion picker is the obvious next move. Match the model to the metal, and self-hosting stops feeling like a gamble.

---

<div class="affiliate-disclosure">Some links above are affiliate links — I earn a small commission at no extra cost to you. I only recommend hardware and software I've personally used or researched for homelab use.</div>

## Related Posts

- [Local LLMs for Homelab: Which Model Runs Best on Your Hardware](/blog/local-llms-homelab-hardware-guide/) — the LLM-side twin of this post, with the same match-the-model-to-metal philosophy
- [Run Ollama on Proxmox LXC (Full Setup Guide)](/blog/ollama-proxmox-lxc/) — the LLM stack this complements
- [GPU VRAM Calculator](/gpu-vram-calculator/) — pick a GPU, see which LLM quantizations actually fit
- [Local LLM Runtime Picker](/local-llm-runtime-picker/) — three questions to the right runtime

---

*Questions, benchmarks from your own GPU, or want the image-model picker built? The source for this post is on [GitHub](https://github.com/bryanmoon19/devhandbook.io). PRs welcome.*
