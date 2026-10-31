---
layout: post.njk
title: "DeepInfer vs vLLM vs SGLang: DeepSeek's New Inference Framework, Explained"
date: 2026-10-31
description: "DeepSeek open-sourced DeepInfer, the serving engine behind their production API, and it cleared 24k stars in two weeks. It's built on vLLM, inspired by SGLang, and requires SM100-class hardware you don't own. Here's what it actually is, how it compares to the two engines it stands on, and why it matters even if you'll never run it."
tags: ["deepinfer", "deepseek", "vllm", "sglang", "llm", "inference", "serving", "local-llm", "self-hosted", "homelab", "ai", "gpu", "moE"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-31-deepinfer-vs-vllm-vs-sglang/"
affiliate: false
cta: true
---

For two years, if you wanted to serve a large language model at scale, there were really two serious answers: **vLLM** and **SGLang**. They're the production serving engines — the layer between a model's weights and the API endpoint your app talks to. Everything else (Ollama, llama.cpp, LM Studio) is what you run on *your* machine; vLLM and SGLang are what you run on *a rack of GPUs*.

That changed two weeks ago. On October 16, DeepSeek open-sourced **DeepInfer** — the inference framework that powers their own production API. It crossed **24,500 stars and nearly 3,000 forks in under two weeks**, which for a serving engine (not a model, not a chat app) is an *unprecedented* launch. vLLM took years to build its ~96k-star lead; SGLang has ~38k. DeepInfer cleared a quarter of vLLM's total in a fortnight.

If you follow local LLMs at all, your question is probably the same one I had: **"Do I need to learn a third thing? Does this replace vLLM? Can I run it on my hardware?"**

The answers, in order: **no, no, and absolutely not — but it still matters.** Here's the honest breakdown.

## The 30-Second Verdict

| Question | Answer |
|----------|--------|
| Is it a vLLM/SGLang replacement? | **No** — it's *built on* vLLM, inspired by SGLang |
| Can you run it at home? | **No** — it needs SM100 or Ascend 950 datacenter GPUs |
| Does it matter to self-hosters? | **Yes**, as a signal and a source of techniques |
| Who is it actually for? | Teams serving DeepSeek models at production scale |
| Should you switch off vLLM/SGLang? | **Only if you serve DeepSeek-V4.1-Flash** specifically |

The shortest version: **DeepInfer is vLLM, heavily modified, purpose-built for one family of models (DeepSeek's), and targeted at the exact datacenter hardware the rest of us don't have.** It's not a competitor to vLLM and SGLang in the way you'd normally mean — it's a fork-plus that tells you a lot about where serving is headed.

## What DeepInfer Actually Is

Let me read the README for you so you don't have to wade through it, because there's a lot of jargon and the important details hide in a `<details>` block.

DeepInfer is the **offline inference engine that serves DeepSeek's production traffic**. The "offline" here doesn't mean "not connected to the internet" — it's a term of art for *batch inference* (give it a pile of prompts, get back completions), as opposed to the full online serving stack with a KV cache system, load balancing, and prefill/decode disaggregation. DeepSeek explicitly says those serving-layer pieces are *not* included in this release.

It supports **one model**: `DeepSeek-V4.1-Flash`. That's the entire supported-model list. This is not a general-purpose engine you point at any arbitrary model from Hugging Face — it's a razor-tuned vehicle for DeepSeek's own MoE architecture.

Its feature list is where the interesting stuff lives:

- **Custom kernels** — FlashMLA, DeepGEMM, DeepEP, TileKernels, DeepSelect, plus hand-written TileLang kernels. These are DeepSeek's in-house compute kernels, and they're some of the fastest attention/GEMM/communication kernels in the world.
- **DSpark + confidence-scheduled verification** — speculative decoding that drafts tokens and verifies them, using confidence scores to decide how aggressively to speculate. This is the "make it faster" trick.
- **SWA bounded replay** — a YOCO-style trick that replays only a bounded suffix of context during prefill instead of the whole thing. Cuts prefill work hard.
- **Asynchronous scheduling** — overlaps CPU batch scheduling with GPU execution, so the scheduler never becomes the bottleneck.
- **Batch-invariant inference** — the same request produces the *same* output regardless of what else is in the batch. This matters enormously in production (results shouldn't depend on your traffic mix).
- **Deterministic sampling** — identical inputs + identical sampling params = identical outputs. A reproducibility guarantee most engines don't make.
- **Structured outputs** — constrain generation to a regex, JSON schema, or EBNF grammar natively.

The hardware support is the headline you need to notice: **NVIDIA SM100 GPUs and Huawei Ascend 950 NPUs.** SM100 is Blackwell Ultra — the B200/B300-class datacenter part. Ascend 950 is Huawei's top datacenter accelerator. There is no RTX, no A-series, no Apple Silicon, no CPU-only path. This is a datacenter engine, full stop.

## The vLLM Connection (It's a Fork, Kind Of)

Here's the line that reframes the whole story, straight from DeepInfer's README acknowledgments:

> *"DeepInfer was originally built primarily on vLLM, with additional inspiration from SGLang and TensorRT-LLM."*

So DeepInfer is **vLLM, extensively modified**. This isn't a from-scratch competitor. It's a heavily customized derivative of vLLM that DeepSeek evolved internally to squeeze maximum throughput out of their own models on their own hardware, and then released back under Apache 2.0.

That's why "DeepInfer vs vLLM" is a slightly wrong framing. The real comparison is:

- **vLLM** — the general-purpose engine. Runs essentially *any* model (dense, MoE, multimodal, embedding, reranking) on a broad hardware range (NVIDIA, AMD ROCm, some CPU, TPU, and increasingly other accelerators). The default choice for "I need an OpenAI-compatible endpoint serving model X."
- **SGLang** — vLLM's main rival, also general-purpose, with its own distinctive strengths (RadixAttention for structured/prefix-caching workloads, a powerful DSL for agentic/structured generation, and consistently strong benchmark numbers on frontier models).
- **DeepInfer** — the specialized derivative. vLLM's skeleton, DeepSeek's muscles, tuned for DeepSeek-V4.1-Flash on SM100/Ascend 950, with features (batch invariance, deterministic sampling, DSpark) you don't get from the general-purpose engines.

The right mental model isn't a three-way cage match. It's a spectrum from **general-purpose** (vLLM, SGLang) to **model-and-hardware-specific** (DeepInfer). And that spectrum has a lesson baked into it, which I'll get to.

## Head-to-Head: The Table That Matters

| | **DeepInfer** | **vLLM** | **SGLang** |
|---|---|---|---|
| Stars (Oct 2026) | ~24.5k (2 weeks) | ~96k (years) | ~38k (years) |
| License | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| Model support | **DeepSeek-V4.1-Flash only** | Basically everything | Basically everything |
| Hardware | SM100, Ascend 950 | NVIDIA, AMD, CPU, TPU, broad | NVIDIA, AMD, broad |
| Origin | Fork of vLLM | Original | Original |
| Key edge | DeepSeek-specific kernels + batch invariance | Ubiquity, maturity, ecosystem | RadixAttention, structured-gen DSL |
| Runs on your GPU? | **No** | Yes (consumer + datacenter) | Yes (consumer + datacenter) |
| Target user | DeepSeek-at-scale operators | Anyone serving models | Anyone serving models, esp. agents |

If the only row you read is "Model support," you already know the answer for yourself: **unless you're specifically serving DeepSeek-V4.1-Flash, DeepInfer is not for you.** vLLM and SGLang remain the right tools for everyone else.

## Why It Hit 24k Stars Overnight

A serving engine getting model-level hype is genuinely unusual, and it's worth understanding *why*, because the star count isn't just fanboyism.

**1. It's the "recipe" for DeepSeek's own performance.** People have spent months trying to reverse-engineer how DeepSeek serves their models so fast and so cheaply. DeepInfer *is* that answer, released in full. The kernels, the scheduling, the speculation — it's all there to read. That's catnip for ML engineers.

**2. The benchmark charts are absurd.** The README ships Pareto-frontier plots (prefill throughput vs. latency, decode throughput vs. per-user speed) measured on 4 and 64 SM100 GPUs. These aren't marketing fluff; they're reproducible via a sweep script in the repo. DeepSeek is basically saying "here's the exact config that gets this performance" — and that level of transparency is rare.

**3. Batch invariance and deterministic sampling are genuinely novel.** The general-purpose engines have historically struggled with output variance across batch compositions, and reproducibility is a persistent pain in production. DeepInfer making these first-class guarantees is a real technical contribution that everyone else is now studying.

**4. It validates the fork-not-replace pattern.** The fact that DeepSeek — one of the best systems shops in the world — chose to *build on vLLM* rather than start from scratch is a massive implicit endorsement of vLLM's architecture. It simultaneously validates vLLM and shows what "vLLM, but specialized" can unlock.

So the stars aren't "people switching to DeepInfer." They're "people bookmarking the definitive example of how to specialize an inference engine." The repo is a masterclass, even if you never run it.

## Can *You* Run It? (The Honest Homelab Answer)

No. And not "no, but if you quantize it." A flat **no**, for two independent reasons:

**Reason one — the hardware.** DeepInfer requires SM100 (Blackwell Ultra) or Ascend 950. These are not consumer parts. There is no 4090, 5090, A100, H100, or Mac path. The cheapest SM100-class machine is a multi-tens-of-thousands-of-dollars datacenter box. My whole beat is running LLMs on *your* hardware — Mac minis, used 3060s, Intel N100s, Proxmox boxes — and DeepInfer sits several tiers above anything in that world.

**Reason two — the model.** DeepInfer serves DeepSeek-V4.1-Flash, a frontier MoE model whose memory footprint is itself datacenter-scale. Even if you *could* build DeepInfer for your GPU, the model you'd run on it won't fit your VRAM. You'd be serving a model you can't host, on a framework that doesn't target your hardware. Both halves point the same direction: this is not a homelab tool.

For your actual local serving, the stack you already know still applies, and my [runtime picker tool](/local-llm-runtime-picker/) is still the right way to choose: **Ollama** for ease, **llama.cpp** for maximum compatibility, **LM Studio** for a GUI, and — if you genuinely need high-throughput serving on consumer or single-server NVIDIA hardware — **vLLM** remains the tool. DeepInfer doesn't change that calculus at all. It lives in a different universe.

## What Self-Hosters *Should* Take Away

If you can't run it, what do you do with this information? Three things.

**1. Watch the techniques trickle down.** The ideas in DeepInfer — speculative decoding with confidence scheduling, SWA bounded replay, asynchronous scheduling, batch invariance — will find their way into llama.cpp, Ollama, vLLM, and SGLang over the next year. They already have analogs in vLLM and SGLang (speculative decoding and prefix caching aren't new). DeepInfer is a preview of where the whole ecosystem is going, and reading it now means you'll understand the changelogs later.

**2. DeepSeek validated the "specialized fork" model — and that's good news.** When the smartest systems team on earth builds on vLLM rather than replacing it, it confirms the general-purpose engines are doing something right and aren't going anywhere. Your investment in learning vLLM or SGLang is safe. DeepInfer is a *complement*, not a threat.

**3. The serving layer is now a real, competitive niche.** I've covered local LLMs extensively on this site — [what runs on a Mac mini](/blog/2026-06-12-local-llms-mac-mini-practical-guide/), [Ollama vs LocalAI](/blog/localai-vs-ollama-2026/), [quantization](/blog/2026-08-21-shrink-local-llm-quantization/) — but I've never written about the *serving* layer, the part between weights and endpoint. That was a gap, because serving is where the hard engineering problems actually live once your model runs. This post is the first of what I expect will be more coverage as the space heats up.

## The Bottom Line

**DeepInfer is not your next runtime.** It's DeepSeek's specialized, SM100-only, single-model serving engine — a heavily-modified vLLM that's a gift to production ML engineers and a masterclass for everyone else, but as relevant to your homelab as a formula 1 engine is to a minivan.

**vLLM and SGLang are not going anywhere.** DeepInfer literally stands on vLLM's shoulders, and both general-purpose engines remain the right choice for anyone serving a *range* of models on a *range* of hardware — including, crucially, the hardware you actually own.

If you serve DeepSeek-V4.1-Flash on Blackwell Ultra, you were already going to evaluate DeepInfer and this post just saved you a README read. For everyone else — including me, on my Mac mini — the takeaway is simpler: **read it, learn from it, don't install it.** The future of serving just got more interesting, and it turns out the future runs on hardware we can only rent.

---

<div class="affiliate-disclosure">This post contains no affiliate links. For the local-AI hardware and runtimes I actually run and recommend, see the Gear page and the <a href="/local-llm-runtime-picker/">Local LLM Runtime Picker</a>.</div>

## Related Posts

- [LocalAI vs Ollama: What Self-Hosters Actually Need in 2026](/blog/localai-vs-ollama-2026/) — the serving/runtime choice for your *own* hardware
- [Local LLMs on a Mac Mini: A Practical Guide](/blog/2026-06-12-local-llms-mac-mini-practical-guide/) — what actually runs at home
- [Shrink It Yourself: How to Quantize a Local LLM](/blog/2026-08-21-shrink-local-llm-quantization/) — the community's answer to big models on small hardware

---

*Star counts and repo details reflect GitHub as of October 31, 2026. DeepInfer details are drawn from the official `deepseek-ai/DeepInfer` README and repository metadata. The source for this post is on [GitHub](https://github.com/bryanmoon19/devhandbook.io). PRs welcome.*
