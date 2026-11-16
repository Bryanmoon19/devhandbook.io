---
layout: post.njk
title: "llama.cpp v1.0 Is Here: What Changed and How to Upgrade Your Self-Hosted Stack"
date: 2026-11-16
description: "llama.cpp hit v1.0.0 on November 13, 2026 — its first stable major release, and it's a breaking one. Here's what actually changed (FP8 KV caches, the MoE expert cache, new model architectures, a hardened server), what the API cleanup breaks, and a step-by-step upgrade path for your Proxmox LXC, Docker, or bare-metal setup."
tags: ["llama.cpp", "llamacpp", "ggml", "local-llm", "self-hosted", "llm", "ai", "inference", "proxmox", "docker", "ollama", "v1.0", "local-ai"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-16-llama-cpp-v1-upgrade-guide/"
affiliate: false
cta: true
---

# llama.cpp v1.0 Is Here: What Changed and How to Upgrade Your Self-Hosted Stack

After years of being the de-facto standard for running LLMs on anything with a CPU and some patience, **llama.cpp hit v1.0.0** on November 13, 2026. It's the first stable major release — 135,000+ GitHub stars, the engine underneath Ollama, LM Studio, and half the "local AI" tutorials on the internet — and it ships alongside **ggml v1.0.0** (the tensor library it's built on, released the same day).

The headline: this is a *breaking* release. The `llama.h` public API got pruned hard, deprecated functions are gone, and some of the new features change the way you configure your server. If you're running llama.cpp in a Proxmox LXC, a Docker container, or bare metal, you should know what changed *before* you pull the update — because a lot of the "how to run a local LLM" guides written in the last two years will now be subtly wrong.

Here's the honest, self-hoster-focused tour: what's new, what breaks, and the exact upgrade path.

---

## Why v1.0 Matters (and Why It's Breaking)

llama.cpp has been on a 0.x version forever, which quietly meant "the API can change under you." v1.0.0 is the project saying *the surface is now stable enough to commit to* — but getting there required **removing the deprecated public API** and promoting the things that had been living in experimental headers. That's the "good pain": one-time breakage now, in exchange for a stable target afterward.

The practical consequences:

1. **35 deprecated functions are gone** from `llama.h`, plus `llama_set_warmup` and the `defrag_thold` / `--defrag-thold` option.
2. **The NextN / speculative-decoding API was promoted** from `llama-ext.h` into the main header — and `llama_set_embd_state_src` was renamed to `llama_set_ctx_state_src`.
3. **ggml's RPC protocol bumped to v9**, which rejects incompatible peers. If you run distributed inference across multiple nodes, they *all* need to be on the same version or they'll refuse to talk.

If you build llama.cpp from source and only use the official `llama-server` binary, you're mostly insulated from the C API churn — but if you compile against `llama.h` (or use a binding that does), expect a recompile and possibly a small port.

---

## What's Actually New (the Self-Hoster's Shortlist)

The release notes are long; here are the changes that genuinely move the needle for a homelab:

### 1. FP8 KV caches (`-ctk/-ctv f8_e4m3`)

KV caches are the hidden memory hog in long-context inference. v1.0 adds **FP8 KV cache support** with optional static per-tensor scales. In plain terms: you can hold roughly *twice* the context in the same VRAM (or RAM) at a small quality cost. If you've been running out of memory on long documents or big agent contexts, this is the single biggest win in the release.

```bash
# halve KV-cache memory with FP8 cache types
llama-server -m model.gguf -ctk f8_e4m3 -ctv f8_e4m3
```

### 2. MoE expert cache with a configurable CPU share

Mixture-of-Experts models (the big frontier MoEs — think Mixtral-style and larger) only activate a fraction of their parameters per token, but *naively* they still load all experts. v1.0 adds a **host-memory expert cache** where cache *misses* can be computed on the CPU and copied back asynchronously — so you can run an MoE that's larger than your GPU VRAM and let the CPU soak up the expert lookups it can handle. Two new knobs in `llama_context_params`:

- `moe_cache_size` — how many experts to keep resident
- `moe_cache_cpu_share` — what fraction of misses the CPU computes

This is the "run a 100B+ MoE on a single consumer GPU" feature, and it's the closest thing to free VRAM this release.

### 3. External PLE / engram shards (`--shard` / `--ple`)

You can now load separate GGUF shards for "PLE"/engram components via `--shard` and `--ple`, instead of one monolithic file. For very large models that don't fit in memory all at once, this means finer control over what stays resident and what streams from disk.

### 4. New model architectures

- **Kimi-K3.1-Pro** — K3 with the full-attention MLA layers replaced by DSA.
- **Ripple-65B-Preview** — a new dense 65B architecture (no new ops required).
- **xing4_0** — mHC + MLA + MoE + MTP.
- **drama-3 TTS** (fishaudio) — text-to-speech in llama.cpp.
- **MageVL-Cowork** and **Kimi-K3.1 vision** — new multimodal/vision support.

The TTS one is quietly notable for self-hosters: it means `llama-server` can now *also* be your speech synthesis endpoint, not just your LLM.

### 5. A hardened `llama-server`

This is the part I care most about for a homelab that's exposed to more than localhost:

- **SSRF protection**, **CORS** handling, and **DNS rebinding** defenses — three of the classic ways a local inference server gets abused or exfiltrated.
- **MCP tool cancellation** — so a runaway tool call doesn't hang the server.
- A new OpenAI-compatible **`/v1/audio/speech`** endpoint (and a `temperature` option for `/tts`).
- A **redesigned web UI** with chat groups and a markdown editor.

If you've been nervous about putting llama.cpp's server on your LAN (or behind a reverse proxy), the SSRF/CORS/DNS-rebinding hardening is the reason to upgrade even if you don't care about FP8.

---

## ggml v1.0.0: the Engine Underneath

Released the same day, **ggml v1.0.0** is mostly invisible to end users but matters for anyone doing custom work. The short version:

- **Pruned the deprecated API** and removed legacy `DIAG_MASK` ops — another one-time breakage for the "commit to stability" goal.
- **Configurable YaRN truncation** (rotation correction-bound rounding) via new `ggml_rope_set_truncate` / `ggml_rope_get_truncate`.
- **FP8 support** added.
- **Broad backend performance work**: few-row quantized matmuls and MoE fusion on CUDA/Metal, a Vulkan prefill FlashAttention path, a device-side MoE scheduler on SYCL, decomposed Adreno FlashAttention in OpenCL, new WebGPU kernels, expanded Hexagon op coverage, and scheduler improvements that stop uploading unused inputs.

The one user-facing gotcha: the **RPC protocol bump to v9** (faster loading, graceful failure on unreachable endpoints). Distributed setups across multiple machines must match versions.

---

## How to Upgrade (Step by Step)

### Option A — Build from source (recommended for Proxmox / bare metal)

```bash
cd ~/llama.cpp
git fetch && git checkout v1.0.0

# CPU-only build
cmake -B build && cmake --build build --config Release -j$(nproc)

# CUDA build (NVIDIA GPU)
cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j$(nproc)

# Metal build (Apple Silicon Mac)
cmake -B build -DGGML_METAL=ON && cmake --build build --config Release -j$(nproc)
```

Then verify:

```bash
./build/bin/llama-server --version
```

If you use a language binding (Python `llama-cpp-python`, Node bindings, etc.), rebuild it against the new headers — the removed functions will cause compile errors that tell you exactly what to update.

### Option B — Docker

The official image tags move with releases. Pin to the v1.0.0 tag rather than `latest` so the breaking change is a deliberate act, not a surprise:

```bash
docker pull ghcr.io/ggml-org/llama.cpp:v1.0.0
# or, for CUDA:
docker pull ghcr.io/ggml-org/llama.cpp:v1.0.0-cuda
```

### Option C — Ollama / LM Studio

If you use Ollama or LM Studio, **you don't need to do anything right now** — they bundle and pin llama.cpp internally and will roll v1.0 support into their own releases. Your models keep working. The FP8 KV cache and MoE expert-cache benefits will arrive when they upgrade their runtime, not when you do.

---

## What Breaks (a Concrete Checklist)

Going into v1.0.0, these are the failure modes to watch for:

1. **C API consumers won't compile.** If you build anything against `llama.h`, the 35 removed functions + the `llama_set_embd_state_src` → `llama_set_ctx_state_src` rename will surface as errors. It's a rename-and-recompile, not a redesign.
2. **`--defrag-thold` is gone.** Any scripts or systemd units passing it will fail. Remove the flag.
3. **`llama_set_warmup` is removed.** If your warmup logic called it, drop the call.
4. **Distributed RPC peers must match.** If you shard across machines with the RPC backend, upgrade *all* of them together or they'll refuse to connect (protocol v9).
5. **The web UI changed.** Chat groups + markdown editor are new; if you bookmarked or scripted against the old UI's structure, re-check it.

None of this is catastrophic — it's exactly what a "1.0" is supposed to do: break old cruft once, then hold still. But if you have a `systemd` unit or cron job that boots `llama-server` with old flags, check it before you reboot the box.

---

## Should You Upgrade Now?

- **If you self-host llama.cpp directly** — yes, on your schedule. The server hardening (SSRF/CORS/DNS rebinding) alone is worth it if your server is reachable beyond localhost, and FP8 KV caches are a genuine memory win for long-context work.
- **If you're on Ollama/LM Studio** — wait for their release; you get the benefits when they ship.
- **If you run MoE models larger than your GPU** — this is the release you've been waiting for. The MoE expert cache with CPU share is the headline feature.
- **If you build against the C API** — budget an hour for the recompile/rename, but do it soon; you don't want to fall multiple breaking versions behind.

The quiet significance here isn't any single feature — it's that llama.cpp *committed to stability*. A 1.0 means the tooling built on top of it (bindings, runtimes, orchestration layers) now has a fixed target. For the self-hosted AI ecosystem, that's a big deal: fewer "it worked yesterday and broke today" moments, more durable tutorials, and a saner upgrade story going forward.

---

*Sources: [llama.cpp v1.0.0 release notes](https://github.com/ggml-org/llama.cpp/releases/tag/v1.0.0), [ggml v1.0.0 release notes](https://github.com/ggml-org/ggml/releases/tag/v1.0.0), and the [Hugging Face llama-cpp-v1 blog post](https://huggingface.co/blog/ggml-org/llama-cpp-v1). Star count and release dates checked live at the time of writing.*
