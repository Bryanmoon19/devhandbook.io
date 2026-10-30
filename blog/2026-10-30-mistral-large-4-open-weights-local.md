---
layout: post.njk
title: "Mistral Large 4 Is Open Weights — Can You Run It at Home?"
date: 2026-10-30
description: "Mistral released the weights for Large 4 (Le Chonk), a 1.05-trillion-parameter MoE model that tops the open-weight coding and cybersecurity charts. 'Open weights' doesn't mean 'runs on your Mac mini' — here's the real memory math, what hardware actually holds it, and the honest answer to whether you can self-host it."
tags: ["mistral", "local-llm", "open-weights", "moe", "quantization", "self-hosted", "homelab", "ai", "llm", "inference", "hardware"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-30-mistral-large-4-open-weights-local/"
affiliate: false
cta: true
---

The headline that hit the top of Hacker News this week — over 1,300 points and hundreds of comments — was simple and consequential: **Mistral is releasing the weights of Large 4.** Their flagship model, the one they've been calling "Le Chonk," is now open weights. You can download it, inspect it, fine-tune it, and run it yourself.

That last part — *run it yourself* — is where the story gets interesting. Because "open weights" is not the same thing as "runs on the hardware you already own." Mistral Large 4 is a **1.05-trillion-parameter** model. Not 7 billion. Not 70 billion. A *trillion*.

For months I've been writing about how the frontier keeps drifting down to consumer hardware — a [125B Qwen model hitting 100 tokens/second on a single RTX 4090](/blog/run-125b-frontier-model-on-consumer-hardware/), the [shrink-it-yourself quantization wave](/blog/2026-08-21-shrink-local-llm-quantization/), matching [models to Mac minis and Intel N100s](/blog/local-llms-homelab-hardware-guide/). This release is the honest counterpoint to all of that. It asks the uncomfortable question: **when the model is a trillion parameters, does "open" actually help you?**

Here's the real answer, with the real math.

## What "Le Chonk" Actually Is

Before we get to the hardware, let's pin down what we're dealing with, because the specs explain both the hype *and* the catch.

Mistral Large 4 is a **natively multimodal** model with a **granular Mixture-of-Experts (MoE)** architecture:

| Spec | Value |
|------|-------|
| Total parameters | **1.05 trillion** |
| Active parameters | **~52 billion** |
| Vision encoder | 1.6B parameters |
| Context window | 1M tokens |
| Modalities | Text + vision |
| License | Open Weight License v 26.10 |

That "52B active / 1.05T total" split is the single most important line in the table, and I'll come back to it. But first, why everyone cares.

Since its preview in early October, Mistral put the model through three weeks of aggressive reinforcement learning, and the results are genuinely strong. On coding, it leads open-weight models on FrontierCode and Terminal-Bench. On the Artificial Analysis Coding Agent Index it ties the best open models while using **47% fewer tokens per task**. It's also the best open-weight model for *defensive* cybersecurity — the angle Mistral is clearly pushing hard, with a whole roster of security-vendor endorsements (Cisco, CrowdStrike, Cloudflare, Fortinet, Elastic) in the announcement.

So this isn't a vanity release. It's a flagship model with real benchmark wins, and now the weights are on the table. The question on every homelabber's mind is whether "on the table" means "in your server."

## The Memory Math That Answers Everything

Here's the thing that separates this from every other "frontier model goes local" story I've written: **the model is a trillion parameters, and parameters need memory.**

A model's memory footprint is parameters × bytes-per-weight. At full precision (BF16/FP16), that's 2 bytes each:

```
1.05 trillion × 2 bytes = ~2.1 terabytes
```

Two terabytes. Not gigabytes — *terabytes*. To hold that at full precision you'd need a machine with 2TB of RAM or VRAM, which is datacenter territory — think a server with 16× 128GB DIMMs, or a rack of 80GB H100s.

Quantization helps, but nowhere near enough to make it *small*. Here's the honest size table, across the quantization ladder:

| Precision | Bits/weight | Approx. size | Fits in |
|-----------|-------------|--------------|---------|
| BF16/FP16 | 16 | ~2.1 TB | Datacenter racks |
| Q8_0 | 8 | ~1.05 TB | Nothing you own |
| Q6_K | 6 | ~790 GB | Nothing you own |
| Q5_K_M | 5 | ~660 GB | Nothing you own |
| Q4_K_M | 4 | ~525 GB | 512GB+ Mac Pro / server |
| Q3_K_M | 3 | ~395 GB | 384GB+ RAM server |
| Q2_K | 2 | ~265 GB | 256GB+ RAM server, barely |

Compare that to my usual local-LLM advice: a 7B model at Q4 is ~4GB, an 8B is ~5GB, a 70B is ~40GB. Mistral Large 4 at its *smallest reasonable* quantization is still **roughly half a terabyte**. That's more than the entire disk on most laptops, let alone the RAM.

**The blunt answer: no, you cannot run the full Mistral Large 4 on a Mac mini, a homelab mini PC, or a single consumer GPU.** Not at any usable quantization. The hardware floor is a machine with ~300GB–1TB of combined memory, which starts around the price of a small car and goes up from there.

## But Wait — It's MoE. Doesn't That Change It?

This is where it gets nuanced, and where you might think the trillion-parameter headline overstates the problem.

Mistral Large 4 is a **sparse** model. Of its 1.05T total parameters, only about **52B are active per token**. During inference, the router fires a small subset of experts for each token, so the *compute* per token is closer to a 52B dense model — not a 1T dense model. That's the whole point of MoE: get big-model quality at small-model inference cost.

But here's the catch that trips people up:

**Sparse compute does not mean small memory.** To run a sparse model, you still need *all* the experts resident in memory, because you don't know which experts any given token will route to until you compute the routing. You can't stream just the active experts from disk — the whole point of MoE is that different tokens hit different experts, and if the model has to page experts in and out of RAM, your tokens-per-second collapses to something useless.

So the MoE architecture is exactly why Large 4 is *fast* on Mistral's datacenter infrastructure (you get 52B-parameter latency with 1T-parameter knowledge) — but it does **nothing** to shrink the memory footprint you'd need to run it yourself. You still need ~300GB–2TB resident, even if you're only "computing" 52B of it at a time.

This is the key insight the Hacker News thread largely missed: **the 1.05T number is the whole ballgame for self-hosting, and the 52B number is a red herring when it comes to hardware requirements.**

## What Hardware Would *Actually* Run It

Let's be concrete about what "run it yourself" requires, so you can decide if this is a project or a fantasy. There are three realistic tiers:

**1. The "I have a real server" tier (~$15k–$40k):**

- A single server with **512GB–1TB of system RAM** running CPU inference via llama.cpp. This is genuinely viable if you already run a homelab at this scale — but it'll be *slow*. At Q4 (~525GB), a 1TB-RAM server with fast DDR5 and a high-core-count CPU might sustain single-digit tokens per second. Usable for batch jobs, not for interactive chat.
- A **Mac Pro or high-end Mac Studio** with 512GB+ unified memory. This is actually one of the cleaner options because Apple's unified memory has far more bandwidth than system DDR5, and the MLX framework handles MoE offloading reasonably well. A 512GB M-series machine might hit 10–20 t/s. But a 512GB Mac Studio is a $10k+ machine that most homelabbers are not buying.

**2. The multi-GPU tier (~$20k+):**

- Several RTX 4090s or 5090s won't cut it — even four 4090s is only 96GB of VRAM, an order of magnitude short of the ~525GB you'd need at Q4. This tier genuinely requires **datacenter GPUs**: a pair of H100/H200s (80GB–141GB each), or 6–8× A100 80GB. That's the "small company or well-funded hobbyist" bracket, not the homelab bracket.

**3. The "don't run the full model" tier (free, and the one you'll actually use):**

The realistic path for 99% of us isn't running the full model at all — it's:
- **Using the API.** At $0.70/M input and $2.10/M output tokens, it's cheap enough to experiment with without any hardware.
- **Waiting for the community to shrink it.** This is what always happens with big releases: within weeks-to-months, someone releases aggressive quants (Q2/Q3), expert-pruned variants, or distilled smaller versions that capture most of the quality in a fraction of the memory. My [quantization guide](/blog/2026-08-21-shrink-local-llm-quantization/) is about exactly this cycle.
- **Fine-tuning the weights on rented GPUs**, then deploying the result to modest local hardware. The open weights make this possible even if you can't host the full base model.

## Open Weights ≠ Open Source (A Nuance Worth Noting)

One more thing worth flagging, because "open" gets thrown around loosely. Mistral released these under the **Open Weight License v 26.10** — *not* an OSI-approved open-source license. The weights are downloadable and inspectable, but there are almost certainly restrictions on commercial use, redistribution, or training derivatives at scale.

This is a real and important distinction. It's far more open than the closed labs (OpenAI, Anthropic, Google's frontier models), but it's not the same as an Apache-2.0 or MIT release. If you're planning to build a product on top of Large 4, read the license text carefully before you commit. The "open weights" framing is accurate; "open source" would be marketing.

## So, Can You Run It at Home?

The honest, complete answer:

**No — not the full model, not on anything resembling homelab hardware.** The memory floor of ~300GB–1TB puts it a full order of magnitude beyond even the most ambitious home setups. This is not a Mac mini model. It's not even a single-4090 model, the way the [125B Qwen release](/blog/run-125b-frontier-model-on-consumer-hardware/) was.

**Yes — in the ways that actually matter for most of us:** you can access it cheaply via API, you can fine-tune it on rented hardware, you can wait for community-shrunk variants, and — if you run an actual datacenter-grade server or a 512GB Mac — you can genuinely self-host it today.

The release still matters enormously, just not for the reason the headline implies. "Open weights" here is about **sovereignty and control**, not portability. It's for the enterprise that wants to run its own model on its own infrastructure for data-residency reasons, and for the researchers and developers who want to inspect, fine-tune, and build on a frontier model without a vendor gatekeeper. It's a signal that the top of the open-weight leaderboard is now a trillion-parameter MoE — and a reminder that "frontier" and "desktop" still don't mean the same thing.

My advice hasn't changed for the homelab. If you want a genuinely useful *local* model, a 14B–32B at Q4_K_M on a used 3060 or a Mac mini is still the sweet spot — it runs today, on hardware you already own, at interactive speeds. Large 4 is a fascinating model to watch and a cheap one to call. Just don't go shopping for a 1TB server because a Hacker News headline made it sound like "open" means "fits in your closet."

---

<div class="affiliate-disclosure">This post contains no affiliate links — I'm not going to recommend a $10,000 server on commission. If you want the full list of local-AI hardware I actually run and recommend, see the Gear page.</div>

## Related Posts

- [Run a 125B Frontier Model on Consumer Hardware](/blog/run-125b-frontier-model-on-consumer-hardware/) — the last time "frontier" genuinely met "desktop"
- [Shrink It Yourself: How to Quantize a Local LLM](/blog/2026-08-21-shrink-local-llm-quantization/) — the community's real answer to big models on small hardware
- [Local LLMs for Homelab: Which Model Runs Best on Your Hardware](/blog/local-llms-homelab-hardware-guide/) — match any model to the machine you actually own

---

*Specs and benchmarks reflect Mistral's official announcement at time of writing (October 30, 2026); quantization sizes are my own calculations from the 1.05T parameter count. The source for this post is on [GitHub](https://github.com/bryanmoon19/devhandbook.io). PRs welcome.*
