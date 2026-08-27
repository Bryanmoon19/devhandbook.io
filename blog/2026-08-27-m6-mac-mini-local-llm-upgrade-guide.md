---
layout: post.njk
title: "M6 Mac mini for Local LLMs: Is the Upgrade Worth It?"
date: 2026-08-27
description: "Apple just dropped the M6, M5 Ultra, and M5 Pro — three simultaneous Hacker News front-page stories. If you run local LLMs on a Mac mini, the only question that matters is memory bandwidth vs. tokens per second. Here's the math on whether the upgrade actually pays for itself."
tags: ["local-llm", "mac-mini", "apple-silicon", "m6", "m5-ultra", "ollama", "self-hosted", "ai", "homelab", "hardware", "memory-bandwidth"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/m6-mac-mini-local-llm-upgrade-guide"
---

Apple dropped three chips at once this week — the M6, the M5 Ultra, and the M5 Pro — and Hacker News lit up with three simultaneous front-page stories (1,028, 726, and 457 points at the time I'm writing this). That's a launch-window spike, and it's aimed squarely at people like me: I run local LLMs on a Mac mini, and every new Apple Silicon release makes me do the same mental math.

*Should I upgrade?*

Most of the coverage is a spec recap — core counts, transistor numbers, the usual. That's the wrong frame. If you run local LLMs, there's exactly one number that determines whether an upgrade is worth it: **memory bandwidth.** Because for LLM inference, memory bandwidth *is* tokens per second. Everything else is noise.

This post is the math I actually ran on my own setup, so you can run it on yours.

## The One Number That Matters

Here's the thing most "M6 vs M5" articles gloss over: **LLM inference is memory-bandwidth-bound, not compute-bound.**

When a model generates a token, it has to read every single one of its weights from memory. A 7B model at 4-bit quantization is ~3.5GB of weights. To generate one token, the chip reads all 3.5GB. To generate 30 tokens per second, it has to read 3.5GB × 30 = **105GB per second** — just for the weights, before you account for the KV cache and context.

That's why the theoretical compute ceiling of a chip barely matters for local LLMs. Your M-series chip has more than enough raw compute to run a 7B model. What throttles you is how fast you can *shuffle those weights through memory* on every single token.

The formula is brutally simple:

```
tokens/sec ≈ memory bandwidth ÷ model size (in bytes)
```

A 7B model at Q4_K_M is ~3.5GB. On a chip with 100GB/s of bandwidth, that's ~28 t/s theoretical. On a chip with 273GB/s, it's ~78 t/s. On a chip with 800GB/s, it's ~228 t/s.

**The model size is fixed. The only lever you can pull is bandwidth.** That's the entire upgrade decision, compressed to one variable.

## The Bandwidth Ladder

Let me lay out the actual numbers, because this is where the "should I upgrade" question gets answered.

| Chip | Memory Bandwidth | 7B Q4 (~3.5GB) | 14B Q4 (~7GB) | 32B Q4 (~16GB) | 70B Q4 (~40GB) |
|------|-----------------|----------------|---------------|----------------|----------------|
| M1 | ~68 GB/s | ~19 t/s | ~10 t/s | — | — |
| M2 | ~100 GB/s | ~28 t/s | ~14 t/s | — | — |
| M3 | ~100 GB/s | ~28 t/s | ~14 t/s | — | — |
| M4 | ~120 GB/s | ~34 t/s | ~17 t/s | ~7 t/s | — |
| M4 Pro | ~273 GB/s | ~78 t/s | ~39 t/s | ~17 t/s | ~7 t/s |
| M5 Pro | ~400 GB/s | ~114 t/s | ~57 t/s | ~25 t/s | ~10 t/s |
| M5 Ultra | ~800 GB/s | ~228 t/s | ~114 t/s | ~50 t/s | ~20 t/s |
| M6 | ~150 GB/s | ~43 t/s | ~21 t/s | ~9 t/s | — |

*(These are theoretical ceilings — real-world throughput lands at 70–85% of the number because of KV cache, context processing, and memory contention. But the ratios hold.)*

Look at that table and the upgrade decision writes itself. The jump that matters isn't M4 → M6. It's **M4 → M4 Pro**, or **M4 Pro → M5 Ultra**. The base M6 is a modest bump over the base M4. The *Pro* and *Ultra* tiers are where the bandwidth actually doubles.

## The Mac mini Problem

Here's the catch, and it's the reason I'm not rushing to buy anything: **the Mac mini has historically been capped at the base and Pro tiers.**

The Mac mini has never shipped with an Ultra chip. The Ultra lives in the Mac Studio and Mac Pro, where the thermal envelope and the price tag can absorb it. So if you're a Mac mini person — and I am — your realistic upgrade path is:

- **M4 mini → M6 mini:** base-to-base, ~120 → ~150 GB/s. A ~25% bump. You'll go from ~34 t/s to ~43 t/s on a 7B model. Noticeable, but not transformative.
- **M4 mini → M5 Pro mini (if it exists):** ~120 → ~400 GB/s. A **3.3×** jump. This is the upgrade that actually changes what you can run — 32B models go from "technically works" to "actually pleasant."
- **M4 mini → M5 Ultra:** not a mini. This is a Mac Studio purchase, and it's a different conversation entirely.

So the honest answer to "should I upgrade my Mac mini for local LLMs?" is: **it depends on whether the M5 Pro comes to the mini, and whether you're currently bandwidth-starved.**

## The Real Question: What Are You Actually Running?

Before you spend money, ask what model you actually want to run *well*. Because "well" has a number attached to it:

- **< 10 t/s:** painful. You'll feel the lag on every response.
- **10–20 t/s:** usable, but you'll notice it on long generations.
- **20–40 t/s:** comfortable. Feels like a slightly slow cloud API.
- **40+ t/s:** instant. You stop thinking about speed entirely.

Now map that to the table. If you're on a base M4 mini running 7B models at ~34 t/s, you're already in the "comfortable" zone. An M6 mini gets you to ~43 t/s — still comfortable, marginally snappier. **You will not feel a life-changing difference.**

But if you're trying to run a 14B or 32B model on that base M4 — and you're sitting at 7–17 t/s — then the M5 Pro's 400 GB/s is the difference between "I tolerate this" and "I actually use this." That's the upgrade that pays for itself.

The pattern I keep seeing (and the one I fell into myself): people buy the base mini, then immediately try to run a model one size too big for it, and conclude they need a new machine. The fix isn't always a new machine. Sometimes it's running the *right* model for the bandwidth you have.

## What I'm Actually Doing

I run a base M4 Mac mini as my local LLM box, and I've written at length about [the practical setup](/blog/2026-06-12-local-llms-mac-mini-practical-guide/) and [matching models to hardware](/blog/local-llms-homelab-hardware-guide/). Here's my honest take on this launch:

**I'm not upgrading to the M6 mini.** A ~25% bandwidth bump doesn't change what I can run. I'm already in the comfortable zone for 7B models, and the M6 doesn't unlock a new tier for me.

**I'm watching the M5 Pro mini closely.** If Apple puts the M5 Pro in the mini at a sane price, that's a 3.3× bandwidth jump — the difference between "7B is my ceiling" and "32B is my daily driver." That's the upgrade that would actually change my workflow, because it changes *which models* I can run, not just *how fast* I run the ones I already have.

**The M5 Ultra is a different machine, not an upgrade.** 800 GB/s is genuinely exciting — it's the first Apple Silicon that makes 70B models feel local-first rather than local-tolerated. But it's a Mac Studio, it's a different price bracket, and it's a "do I want a dedicated inference server" question, not a "should I refresh my mini" question.

## The Decision Framework

If you're staring at the same launch and wondering whether to buy, here's the five-minute version:

1. **Find your current bandwidth** (the table above, or look up your exact chip).
2. **Find the model you actually want to run** and its Q4 size.
3. **Divide bandwidth by model size.** That's your current t/s ceiling.
4. **If you're under ~15 t/s on the model you want**, an upgrade to a higher-bandwidth tier is worth it — and the jump that matters is to Pro or Ultra, not base-to-base.
5. **If you're already at 20+ t/s**, a base-to-base upgrade is a marginal speed bump, not a capability unlock. Save your money.

The trap is treating every Apple Silicon release as a reason to upgrade. It isn't. For local LLMs, the only release that matters is the one that **doubles your memory bandwidth** — because that's the only release that doubles your tokens per second.

## The Bottom Line

The M6 is a nice chip. The M5 Ultra is a genuinely exciting one. But for the Mac mini crowd running local LLMs, the headline isn't "M6 is here" — it's "**does the M5 Pro come to the mini?**"

Because memory bandwidth is the whole game, and the base M6 doesn't move the needle enough to matter. If you're bandwidth-starved, wait for the Pro tier. If you're not, you were never the target for this upgrade anyway.

The best local LLM machine is the one that runs the model you actually use at a speed you actually enjoy. For most of us, that's still the mini we already own.

---

*Running local LLMs on Apple Silicon? I'd love to hear your real-world tokens-per-second numbers — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my [practical Mac mini local LLM guide](/blog/2026-06-12-local-llms-mac-mini-practical-guide/), the [homelab hardware matching guide](/blog/local-llms-homelab-hardware-guide/), and the [Ollama on Proxmox LXC setup](/blog/ollama-proxmox-lxc/).*
