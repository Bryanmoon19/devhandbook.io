---
layout: post.njk
title: "What Are 'System 1' Decision Models? The Laya/Jev Wave Explained (and Can You Self-Host Them?)"
date: 2026-10-10
description: "Non-autoregressive 'System 1' decision models are the fastest-growing niche in local AI. Laya, Jev, Kev, Magpie — what yes/no/score/choice models actually are, why they're orders of magnitude cheaper than LLMs, and how to run them on a Mac mini with Ollama and MLX."
tags: ["local-llm", "ollama", "mac-mini", "apple-silicon", "mlx", "self-hosted", "homelab", "ai-agents", "laya", "jev", "non-autoregressive", "decision-model"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-10-system-1-decision-models/"
affiliate: false
cta: true
---

If you've been following the local-AI scene the last few months, you've probably seen a strange new category of models rocket up the GitHub trending charts. Names like **Laya**, **Jev**, **Kev**, and **Magpie** — each with tens of thousands of stars, each described with a vocabulary that doesn't quite sound like the LLMs you're used to. "Non-autoregressive." "System 1." "Decision engine." "Every agent's model."

If your mental model of AI is "ChatGPT but smaller," these projects don't fit it. That's because they're a genuinely different thing — and for a homelabber running local LLMs on a Mac mini, they might be the most useful new thing in months.

Here's the plain-English explainer: what "System 1 decision models" actually are, why they're so cheap and fast compared to autoregressive LLMs, and a concrete guide to running the whole family self-hosted on Apple Silicon.

---

## First: The Two Systems in Your Head

The "System 1" name comes from psychologist Daniel Kahneman's *Thinking, Fast and Slow*. He split human cognition into two modes:

- **System 1** — fast, automatic, instinctive. You see a ball flying at your face and you flinch. You don't deliberate; you *react*. It's the part of you that reads a room, spots danger, or knows "this email is spam" without reading it twice.
- **System 2** — slow, deliberate, effortful. Doing long division. Writing a careful essay. Reasoning through a multi-step problem.

An autoregressive LLM — the thing you pull with `ollama pull` and chat with — is a **System 2** machine. It generates text token by token, left to right, each token conditioned on everything before it. That's why it *can* write essays and solve problems, but it's also why it's expensive: every one of those tokens costs compute, and the chain is sequential, so it can't be parallelized. Fast reasoning is fundamentally at odds with "predict the next word 4,000 times."

A **System 1 decision model** skips the essay entirely. It's built to answer *one kind of question* instantly: **"Which one?"**

---

## What "Non-Autoregressive Decision" Actually Means

Strip away the jargon and a System 1 decision model does one of a handful of very specific jobs:

1. **Yes / No** — "Is this request safe to run?" → `yes`
2. **Score** — "How relevant is this search result?" → `0.87`
3. **Typed choice** — "Is this email spam, personal, or work?" → `personal`
4. **Pick-one / rank** — "Which of these 5 tool calls should the agent make next?" → option 3

Notice what's *not* on that list: prose. A decision model doesn't write you a paragraph. It outputs a single token, or a short structured blob — a label, a number, a JSON object.

That's the whole trick. Because the output is *one token* (or a small fixed set) instead of a stream of thousands, the model doesn't need to be autoregressive at all. It can look at the whole input at once and produce the whole answer in a single forward pass. No left-to-right chain. No "generate 50 tokens to say `yes`."

The result is a model that is:

- **Orders of magnitude faster** — one pass instead of hundreds or thousands of sequential passes.
- **Dramatically cheaper** — fewer FLOPs per decision, so less energy, less time, less memory.
- **Tiny** — decision models are often in the 0.5B–8B range, because you don't need a 70B brain to say "yes" or "no."
- **Deterministic-feeling** — no long tail of rambling to sample, just a crisp structured answer.

Put differently: an LLM is a *writer*. A decision model is a *switch*. Agents need both — but they need the switch a *lot* more often, and it's been a waste to spin up a 70B writer every time the agent just needs to answer "should I proceed?"

---

## Why This Matters for Agents (and Your Mac mini)

Here's the context that makes this wave make sense. Over the last year the local-AI community has moved hard into **agents** — systems that loop: read → decide → act → observe → repeat. Tools like OpenClaw, Continue, Claude Code, and a dozen open-source orchestrators all run this same loop.

And it turns out the loop is *dominated by decisions*. An agent spends most of its tokens not writing, but *choosing*: which tool, which file, is-this-done-yet, is-this-safe, does-this-need-a-human.

Every one of those checks, done with a full autoregressive LLM, is like calling a novelist to ask "should I turn left?" You pay novelist prices for a one-word answer. System 1 models are the fix: a dedicated, cheap, fast *decision layer* that the big model delegates to.

The practical payoff for a homelabber:

- Your agent's per-step cost collapses. Decisions that used to eat 2,000 tokens now eat one.
- Latency drops from seconds to milliseconds — an agent that feels instant instead of laggy.
- Your Mac mini's limited unified memory is freed up. You keep one big "thinking" model and one tiny "deciding" model, and the tiny one handles the firehose of cheap choices.

That's the pitch. Now the family.

---

## The Family: Laya, Jev, Kev, and Magpie

These five projects form a loose cluster of the same core idea — small, fast, non-autoregressive decision engines — with different wrappers and runtimes. (Star counts are as of October 2026; these are moving fast.)

### NandhaKishorM/laya — the System 1 decision engine (32K⭐)

**Laya** is the anchor of the wave and the most explicit about the "System 1" framing. It's positioned as a *non-autoregressive decision engine*: give it a prompt and a set of options, get back a yes/no, a score, or a typed choice in a single pass. It's the project most people mean when they say "System 1 model."

The core idea: don't generate. *Decide.* Laya reads the full input context at once and emits the decision directly, which is what lets it run so much faster than an equivalent-size autoregressive model.

### browser-use/jev-ultrafast — decisions for the browser (22.5K⭐)

**Jev** comes out of the browser-use ecosystem — the tooling that drives LLM agents around web pages. It's tuned for exactly the kind of micro-decisions a browsing agent faces constantly: "is this the login page?", "did the action succeed?", "which element should I click next?" The "ultrafast" in the name is the point — these checks need to happen faster than a human can perceive, or the agent feels sluggish.

### jaredpalmer/kev — the lean single-purpose choice model (8.8K⭐)

**Kev** is the minimalist take. Small, focused, designed to slot in as a drop-in decision layer for agent frameworks. If Laya is the general-purpose decision engine and Jev is browser-tuned, Kev is the "just give me a fast yes/no router" option — lightweight enough to run comfortably even on an 8GB machine.

### yetone/magpie — "every agent's model" (7.6K⭐)

**Magpie** brands itself as "every agent's model" — the model you keep *resident* (loaded in memory) at all times because it handles the long tail of cheap decisions an agent throws off. It's the clearest articulation of the workflow I described above: one always-on small model for decisions, plus a big model you spin up only when real generation is needed.

### laya-mlx — native MLX runtime (6.9K⭐)

**laya-mlx** is the one Mac users should care most about. It's Laya re-implemented to run natively on **Apple's MLX** framework — the same Metal-accelerated runtime that makes MLX the fastest inference path on Apple Silicon. This is the difference between "runs on a Mac" and "runs *well* on a Mac," which matters when your whole goal is millisecond decisions.

---

## System 1 vs. Autoregressive: The Numbers

Let me make the cost difference concrete, because it's the single most important thing to understand about this wave.

An autoregressive LLM producing a 50-token answer to "which tool should I call next?" does ~50 sequential forward passes, each one paying attention over the entire accumulated context. A decision model answering the same question with a single label does **one** forward pass.

That's not a 10% or 2x difference. It's a *50x–100x* difference in compute for that particular job, before you even account for the model being smaller to begin with.

A rough, honest comparison:

| | Autoregressive LLM | System 1 decision model |
|---|---|---|
| Typical size | 7B–125B | 0.5B–8B |
| Output | stream of N tokens | 1 token / small structured blob |
| Passes per answer | ~N (sequential) | 1 |
| Latency | 100ms–seconds | single-digit milliseconds |
| Parallelizable | No (sequential chain) | Yes (one shot) |
| Cost per decision | high (tokens × passes) | near-zero |
| What it's *for* | writing, reasoning, generation | yes/no, score, choose, classify |

The key mental model: **you don't replace your LLM with a decision model. You offload the cheap decisions to it and keep the LLM for the expensive thinking.** They're complementary, not competing.

This is also why these models run so comfortably on a Mac mini. A 0.5B–3B decision model in MLX uses a rounding error's worth of unified memory and returns answers in milliseconds, leaving your 24GB for the big reasoning model when you actually need it.

---

## Self-Hosting on a Mac mini: The Guide

Enough theory. Here's how to actually run these on Apple Silicon. There are two clean paths — Ollama (easiest, most compatible) and MLX (fastest, native Metal).

### Hardware reality check

The good news: this is *far* more forgiving than running a 14B LLM. A decision model in the 0.5B–3B range needs well under 2GB of unified memory and runs comfortably on **any** Apple Silicon Mac mini — yes, even an 8GB M1. If you've been reading my [Mac mini local LLM guide](/blog/2026-10-09-local-llms-mac-mini/) and feeling constrained by RAM, this category is the opposite of constrained.

### Path 1: Ollama (the easy button)

Ollama is the fastest way to get *any* model running, and the decision-model projects publish Ollama-ready artifacts. Check the specific repo's README for the exact tag, but the flow is always the same:

```bash
# Install Ollama if you haven't (see my full guide)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a System 1 decision model (tag will vary by project)
ollama pull laya          # or the repo's published tag

# Try an interactive decision
ollama run laya
```

Since these models aren't chatty, the more useful path is the API — your agent framework calls it as a decision endpoint:

```bash
# Start the server
ollama serve

# Ask a yes/no decision
curl http://localhost:11434/api/generate -d '{
  "model": "laya",
  "prompt": "Should this shell command be executed? rm -rf /tmp/build-cache",
  "stream": false
}'
```

The response is a crisp label or structured JSON instead of a paragraph — that's the whole point.

### Path 2: MLX (fastest on Apple Silicon)

For maximum speed — and given these models *are* the speed play — the native MLX route is worth the extra five minutes:

```bash
# Install MLX
pip install mlx-lm

# Run a decision model via the MLX server
python -m mlx_lm.server \
  --model laya-mlx/Laya-System-1-3B-4bit \
  --port 8080
```

Or in Python, which is handy if you're wiring it into your own agent loop:

```python
from mlx_lm import load, generate

model, tokenizer = load("laya-mlx/Laya-System-1-3B-4bit")
answer = generate(model, tokenizer, prompt="Is this safe? [context...]")
print(answer)  # a single token / short structured output
```

MLX uses Metal and unified memory natively, so on Apple Silicon you'll get the fastest possible decisions — often single-digit milliseconds for a small model.

### Wiring it into your agent

The real win is architectural: keep the decision model resident and delegate. The pattern looks like this in any agent loop:

1. **Big thinking model** (e.g., a 14B–32B LLM) — does the actual reasoning and writing.
2. **Resident decision model** (Laya/Jev/Kev/Magpie, 0.5B–3B) — answers the constant stream of yes/no, score, and choice questions.

Because the decision model is tiny and always loaded, the agent stops paying novelist prices for one-word answers. On a Mac mini, you can keep the decision model loaded in MLX at all times (it's using almost no RAM) and only spin the big model up when generation is actually required.

A concrete starting point: run `laya-mlx` resident on port 8080, and point your agent's "router" / "safety check" / "tool choice" steps at it instead of at your main LLM.

---

## The Honest Trade-offs

Before you rip out your LLM, some reality checks — this category is young and moving fast.

**These models are not general-purpose.** They don't write, they don't reason through multi-step problems, they don't hold long coherent conversations. They decide. Use them for the wrong job and they'll fail, usually silently and confidently.

**The vocabulary is unsettled.** "System 1," "non-autoregressive," "decision engine," "choice model" — the field hasn't standardized on names yet. Read each repo's README carefully, because two projects describing the "same" thing may expose very different APIs and output formats.

**Benchmarks are thin and self-reported.** There's no equivalent of the LMSYS arena for decision models yet. You'll need to evaluate on *your* actual decision tasks, not on the repo's marketing numbers.

**Star counts ≠ production readiness.** These are fast-moving, somewhat experimental projects. The GitHub stars are real, but they reflect interest more than maturity. Pin versions, test on your real workloads, and expect breaking changes.

The honest summary: this is the *right idea* for the agent era, it's genuinely useful on a Mac mini today, and it's also early. Treat it as a powerful new tool, not a finished platform.

---

## Conclusion

The "System 1 decision model" wave — Laya, Jev, Kev, Magpie, and the MLX ports — is one of those shifts that's easy to miss if you're still thinking of every AI model as "a thing you chat with." But for anyone running agents locally, it solves a real, constant problem: agents are mostly making *decisions*, and decisions don't need a 70B-parameter novelist.

The models are small enough to run on any Mac mini, fast enough to answer in milliseconds, and cheap enough to keep resident at all times. They don't replace your LLM — they *offload* it, and in the process they make your whole local-AI setup feel dramatically faster.

Start with `laya-mlx` via MLX if you're on Apple Silicon, or the Ollama tag if you want the easy path. Point your agent's router and safety checks at it. Watch your per-step latency and cost drop through the floor.

The writer and the switch, working together — that's the whole game.

---

*The System 1 model ecosystem is moving fast, and star counts, project names, and APIs will drift. Check each repo's README for current tags and output formats before wiring anything into production. Experiment on your own decision tasks, share what you find, and iterate.*
