---
layout: post.njk
title: "Speculative Decoding: The Free 2–4x Speedup for Your Local LLM Stack"
date: 2026-11-22
description: "Speculative decoding uses a tiny draft model to predict multiple tokens ahead of your main model, then verifies them in a single batch — a 2–4x tokens/sec speedup with no accuracy loss. Here's how it actually works, which draft to pair with which base model, and exact commands for llama.cpp, vLLM, and SGLang."
tags: ["speculative-decoding", "llama.cpp", "vllm", "sglang", "local-llm", "self-hosted", "llm", "ai", "inference", "eagle", "dflash", "ggml", "llamacpp", "local-ai"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-22-speculative-decoding-local-llm-speedup/"
affiliate: false
cta: true
---

# Speculative Decoding: The Free 2–4x Speedup for Your Local LLM Stack

You've already got a GPU sitting in your homelab running llama.cpp or vLLM. Maybe you followed the [llama.cpp v1.0 upgrade guide](/blog/2026-11-16-llama-cpp-v1-upgrade-guide/) last week. The model runs fine, but generation feels slow — 15–25 tokens/sec on a 24 GB card, and you're wondering if the only fix is "buy a bigger GPU."

It's not. **Speculative decoding** is a technique that can roughly double your tokens/sec — and in some cases hit 3–4x — using *models you already have the VRAM for*. No accuracy loss, no quantization tricks, no new hardware. It's built into llama.cpp, vLLM, and SGLang right now, and it's the single highest-leverage optimization most self-hosters haven't turned on.

Here's what it is, why it's free speed, and exactly how to wire it up on your box.

---

## The core idea: why "verify a batch" beats "generate one token"

An LLM generates text one token at a time, and each token requires a full forward pass through every layer of the model. That's expensive — and it's why generation (decode) is *much* slower than prompt processing (prefill), which can chew through an entire prompt in parallel.

Speculative decoding exploits that asymmetry. The insight:

1. A **small draft model** (often 1/10th the size, or a single specialized layer) guesses the next *several* tokens — quickly, because it's small.
2. The **target model** (your real model) then verifies all those guessed tokens in **one batched forward pass** instead of N sequential ones.
3. Accepted tokens are kept; rejected guesses are discarded and regenerated.

Because computing N tokens in a batch is far more efficient than computing N tokens one-at-a-time, this is a net win **whenever the draft model guesses correctly often enough** — which, for a draft that's a similar family to the target, is most of the time.

Crucially, **the output is identical to the target model's**. The draft only *proposes*; the target *verifies*. Nothing changes about what the model would have said — it just says it faster. That's the "free" part: no accuracy trade-off, unlike quantization.

> **The one thing it's not free in is VRAM.** The draft model lives in memory alongside the target. The good news: modern draft methods (EAGLE, DFlash) use tiny one-to-few-layer models, so the footprint is usually 1–2 GB, not a whole second model.

---

## The draft methods, explained without the math

The field has moved fast. What started as "pair a 3B model with a 7B model" (draft-model speculative decoding) has evolved into specialized draft heads trained per-target-model. Here's the landscape as of late 2026:

| Method | What the draft is | How it drafts | Best for |
|--------|------------------|---------------|----------|
| **Draft model** (classic) | A small separate model (e.g. Qwen 1.5B for a Qwen 7B target) | Autoregressive, one token at a time | Quick to set up, any model family |
| **EAGLE / EAGLE-3** | A one-layer transformer reading the *target's* hidden states | Predicts next tokens from internal activations | Highest acceptance on supported models |
| **DFlash** | Small block-diffusion model emitting a whole block per step | Entire block in one forward pass | GPU-friendly, very fast drafting |
| **DSpark** | DFlash backbone + Markov head | Block drafting with Markov prediction | Recent SOTA for DeepSeek-family |
| **MTP** (multi-token prediction) | Extra heads on the target model itself | Predicts multiple tokens per step | Models that ship MTP weights |

**Which should you pick?** In practice:

- **If you run llama.cpp on llama/Qwen/gemma/gpt-oss models** → look for a matching **EAGLE-3** draft. It's the most mature and gives the best acceptance rates.
- **If you run DeepSeek-family or want block drafting** → **DSpark** or **DFlash**.
- **If there's no trained draft for your exact model** → fall back to a **small draft model** of the same family (the classic approach), which works everywhere.

The key constraint: **drafts are trained per target model.** An EAGLE-3 draft for Qwen3-4B won't work for Llama-3.1-8B. You match the draft to the base model, not to the engine.

---

## llama.cpp: the most self-hosted-friendly path

llama.cpp's `llama-server` has the richest speculative-decoding support, and it's what most homelabbers are already running (it's the engine under Ollama and LM Studio). Here's the exact syntax.

### Classic draft model

```bash
llama-server \
  -m /models/Qwen3-8B.gguf \
  -md /models/Qwen3-1.7B.gguf \
  --spec-type draft
```

`-md` points at the draft model. `--spec-type draft` is the classic small-model mode.

### EAGLE-3 (recommended when a matching draft exists)

First convert the EAGLE-3 checkpoint so it inherits the target's tokenizer and layer indices:

```bash
python convert_hf_to_gguf.py AngelSlim/Qwen3-4B_eagle3 \
    --target-model-dir Qwen/Qwen3-4B --outtype bf16 --outfile Qwen3-4B-eagle3.gguf

llama-server -m Qwen3-4B.gguf -md Qwen3-4B-eagle3.gguf --spec-type draft-eagle3
```

### DFlash / DSpark

```bash
# DFlash — block diffusion, emits a whole block per step
python convert_hf_to_gguf.py z-lab/Qwen3-4B-DFlash \
    --target-model-dir Qwen/Qwen3-4B --outtype bf16 --outfile Qwen3-4B-DFlash.gguf

llama-server -m Qwen3-4B.gguf -md Qwen3-4B-DFlash.gguf \
    --spec-type draft-dflash --spec-draft-n-max 15 -fa on --jinja
```

Note the `--spec-draft-n-max` flag — it's clamped to the draft's trained block size. And if you omit `--spec-type`, llama.cpp will try to **infer the type** from the draft model's metadata.

### What draft models are actually available?

From the llama.cpp docs, the supported EAGLE-3 drafts include (as of v1.0, Nov 2026):

- **Qwen3 family:** `AngelSlim/Qwen3-1.7B_eagle3` through `AngelSlim/Qwen3-32B_eagle3`
- **Llama 3.1/3.3:** `yuhuili/EAGLE3-LLaMA3.1-Instruct-8B`, `yuhuili/EAGLE3-LLaMA3.3-Instruct-70B`
- **Gemma 4:** `RedHatAI/gemma-4-31B-it-speculator.eagle3`, `RedHatAI/gemma-4-26B-A4B-it-speculator.eagle3`
- **gpt-oss:** `RedHatAI/gpt-oss-20b-speculator.eagle3`, `lmsys/EAGLE3-gpt-oss-120b-bf16`, `nvidia/gpt-oss-120b-Eagle3-long-context`

The full list is maintained in llama.cpp issue #18039 — check there for updates.

> **Heads-up on the naming.** DFlash2, DSpark, and LiliCorr are all DFlash *backbones* with a different head, and the head determines the spec type: `draft-dspark` needs the Markov head, `draft-dflash2` the candidate selector, `draft-lilicorr` the candidate scorer. On a mismatch, speculative decoding simply won't initialize — so if it silently doesn't speed up, check the head matches.

---

## vLLM: the throughput king

vLLM (97k+ GitHub stars, Apache-2.0) is what you reach for when you're serving multiple users or want max batch throughput. It supports speculative decoding with draft models and, more recently, EAGLE.

The vLLM pattern is straightforward — you pass the draft model as `--speculative-config`:

```bash
vllm serve Qwen/Qwen3-8B \
  --speculative-config '{"model": "AngelSlim/Qwen3-1.7B", "method": "draft"}'
```

For EAGLE-style drafts, vLLM uses its own integration. The general shape:

```bash
vllm serve Qwen/Qwen3-8B \
  --speculative-config '{"model": "AngelSlim/Qwen3-1.7B_eagle3", "method": "eagle"}'
```

The exact `method` strings and supported draft formats change between vLLM releases — check `vllm serve --help` for the current `--speculative-config` options, because the field has been moving quickly in 2026.

---

## SGLang: fast and increasingly the default for research

SGLang (38k+ stars, Apache-2.0) has been gaining on vLLM for raw serving speed and is often the first place new decoding tricks land. It also supports speculative decoding via draft models:

```bash
python -m sglang.launch_server \
  --model Qwen/Qwen3-8B \
  --speculative-draft-model Qwen/Qwen3-1.7B \
  --speculative-algorithm EAGLE
```

SGLang exposes `--speculative-draft-model` and `--speculative-algorithm` flags, and (like the others) is adding EAGLE-3/DFlash support as the trained drafts proliferate.

---

## What speedup should you actually expect?

Be honest with yourself about the numbers, because "2–4x" is the *range*, not the guarantee:

- **2x is the reliable, conservative expectation** for a well-matched draft model on consumer hardware.
- **3–4x shows up** on the newer block-based methods (DFlash/DSpark) and EAGLE-3, especially on GPUs where batching the verification is cheap.
- **Your mileage depends on** how well the draft predicts your *specific* workload. Code, structured output, and repetitive prose see higher acceptance than freeform creative writing.

The recent DSpark work (DeepSpec, 7k+ stars, MIT) demonstrated block speculative decoding achieving strong speedups on consumer GPUs, and the HN discussion that kicked off this cycle reported **up to 55% faster on an RTX 3090** even with the classic draft-model approach. The takeaway: even a naive setup is a real win, and the tuned methods go much further.

The one way to be sure: **measure your own tokens/sec before and after.** Run your normal workload, note the baseline, flip on a matching draft, and re-measure. The `sybil-solutions/inference-optimisation-skill` repo (1.7k+ stars in under a week) automates exactly this "hill-climbing" over decode/speculative/prefill settings if you want it done for you.

---

## The practical recipe

1. **Identify your base model** and its family (Qwen? Llama? gemma? gpt-oss? DeepSeek?).
2. **Find a matching EAGLE-3/DFlash/DSpark draft** — check the llama.cpp supported list (issue #18039) or Hugging Face for `<Model>_eagle3` / `<Model>_dflash` checkpoints.
3. **If none exists**, fall back to a small draft model of the same family (classic `-md` mode).
4. **Convert the draft** with `convert_hf_to_gguf.py --target-model-dir <base>` (llama.cpp) so it inherits the right tokenizer.
5. **Launch with the matching `--spec-type`**, measure before/after tokens/sec.
6. **Verify output quality** — it should be byte-identical in character; if results look *different*, something's misconfigured, not "working but approximate."

---

## Bottom line

If your local LLM stack is running at 15–25 tok/s and you're resigned to it, speculative decoding is the cheapest upgrade you haven't made. It's a small model (1–2 GB of the VRAM you already have), a few flags, and a 2x-or-better speedup with **zero accuracy loss**. For a homelabber serving a coding assistant, a chat bot, or a document pipeline, that's the difference between "usable" and "snappy" — no new GPU required.

---

*Want more local-LLM speed? See the [llama.cpp v1.0 upgrade guide](/blog/2026-11-16-llama-cpp-v1-upgrade-guide/) for the baseline, the [deepinfer vs vLLM vs SGLang comparison](/blog/2026-10-31-deepinfer-vs-vllm-vs-sglang/) for engine choice, and the [quantization guide](/blog/2026-08-21-shrink-local-llm-quantization/) for the complementary memory-side win.*
