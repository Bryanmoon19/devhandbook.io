---
layout: post.njk
title: "The $0 OpenClaw Setup That Nobody Talks About"
date: 2026-03-27
description: "Most OpenClaw users spend $50-200/month on API bills. Here's how to run a fully functional AI agent for free using local models, free cloud tiers, and a hybrid approach that costs under $3/month."
tags: ["openclaw", "ollama", "self-hosted", "ai", "free", "local-llm", "openrouter"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/openclaw-free-setup"
---

*This post is based on [a discussion by u/ShabzSparq on r/AskClaw](https://www.reddit.com/r/AskClaw/comments/1s55ubm/). We verified the configs against the actual OpenClaw schema, corrected some details, and added editorial context.*

---

Every week I see the same post. "Is $200/month normal?" "My API bill is $47 this week." "I'm on Haiku and still spending $22 a day."

And every time, the top answer is "switch to Sonnet." That's fine advice. But nobody ever asks the real question: **do you need to pay anything at all?**

I've been running an OpenClaw agent for free for the last 3 weeks. Not "$5 a month" free. Not "free trial" free. Actually free. Zero dollars. And it handles about 70% of what I used to pay Claude to do.

Here's the setup. No fluff.

## Hardware Context

**Everything in this guide runs on a Mac Mini M4 with 16GB RAM — no fancy GPU rig required.**

I'm running this on a Mac Mini M4 with 16GB RAM. Ollama + Qwen3.5 9B runs fine on it — not blazing fast, but fast enough that I don't notice the difference for basic tasks. If you have similar hardware (any Apple Silicon Mac, a PC with 16GB+ RAM, or even a decent laptop), you can follow along with Path 2. If you don't have local hardware, Path 1 requires nothing but an internet connection.

## Path 1: Free Cloud Models (No Hardware Needed)

**Sign up for a free API tier, paste one config block, and your agent is running at $0/month.**

This is the one most people should start with because it requires nothing except an OpenClaw install you already have.

### OpenRouter Free Tier

Sign up at [openrouter.ai](https://openrouter.ai). No credit card. They offer 27+ free models including Nemotron Super 120B, Llama 3.3 70B, MiniMax M2.5, and Devstral. These aren't toy models — some have 128K+ context windows.

> **⚠️ Free model availability changes.** OpenRouter rotates which models are free based on provider partnerships. The specific models listed here were free as of March 2026. Check [openrouter.ai/models](https://openrouter.ai/models) and filter by "free" for the current list.

Add your OpenRouter provider to `~/.openclaw/openclaw.json`:

```json
{
  "models": {
    "providers": {
      "openrouter": {
        "baseUrl": "https://openrouter.ai/api/v1",
        "apiKey": "sk-or-v1-your-key-here",
        "api": "openai-completions",
        "models": [
          {
            "id": "nvidia/nemotron-3-super-120b-a12b:free",
            "name": "Nemotron Super 120B (Free)",
            "reasoning": false,
            "contextWindow": 131072,
            "maxTokens": 8192,
            "cost": { "input": 0, "output": 0 }
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/nvidia/nemotron-3-super-120b-a12b:free"
      }
    }
  }
}
```

If you don't want to pick a specific model, OpenRouter has a free auto-router:

```json
"primary": "openrouter/openrouter/auto:free"
```

### Gemini Free Tier

Google gives you 15 requests per minute on Gemini Flash for free. That's more than enough for casual daily use. Get an API key from [ai.google.dev](https://ai.google.dev), then run `openclaw onboard` and pick Google AI Studio. It's a built-in provider, so setup is straightforward.

### Groq

Fast. Very fast. Free tier has rate limits but for basic agent tasks it works. Sign up, get an API key, done.

### The Catch with Free Cloud Tiers

Rate limits. You will hit them. Your agent will pause, wait, retry. For light to moderate daily use (10–20 interactions) this is barely noticeable. For "always-on agent doing 100 tasks a day" it won't cut it. But let's be honest — if you just installed OpenClaw this week, you are not running 100 tasks a day.

## Path 2: Local Models via Ollama (Truly $0, Forever)

**Run models on your own hardware — no API key, no account, no rate limits, no data leaving your machine.**

This is the setup where your API bill is literally zero because nothing leaves your machine. No API key. No account. No rate limits. No data going anywhere.

Ollama became an official OpenClaw provider in March 2026, so this is now a first-class setup — not a hack.

**Step 1: Install Ollama.**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Step 2: Pull a model.**

```bash
# If you have 20GB+ VRAM (RTX 3090, 4090, M4 Pro/Max)
ollama pull qwen3.5:27b

# If you have 16GB RAM (most Apple Silicon Macs, decent PCs)
ollama pull qwen3.5:9b

# If you have 8GB RAM
ollama pull qwen3.5:3b
```

Qwen3.5 is the current sweet spot for OpenClaw. It handles tool calling reliably and the smaller variants run comfortably on consumer hardware.

**Step 3: Run onboarding.**

```bash
openclaw onboard
```

Select Ollama from the provider list. It auto-discovers your local models. Done.

### Manual Config (If You Need It)

If Ollama is on a different host or you want explicit control, add this to your `openclaw.json`:

```json
{
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434/v1",
        "apiKey": "ollama-local",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5:9b",
            "name": "Qwen 3.5 9B (Local)",
            "reasoning": false,
            "contextWindow": 131072,
            "maxTokens": 32768,
            "cost": { "input": 0, "output": 0 }
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen3.5:9b"
      }
    }
  }
}
```

### Debugging Tips That Will Save You Hours

These are the things I figured out the hard way so you don't have to:

- **Set `"reasoning": false`** in the model config. When reasoning is enabled, OpenClaw sends prompts in ways that local models don't always handle well, and tool calling breaks silently. You'll stare at broken JSON output for an hour before you figure out why.
- **Set `"api": "openai-completions"`** explicitly in the provider config. This tells OpenClaw exactly how to talk to Ollama and avoids ambiguity in tool-calling behavior.
- **Qwen3.5 > everything else for tool calling.** I tested Mistral, older Llama models, and various CodeLlama variants. Qwen3.5 handles OpenClaw's tool-calling format more reliably than any of them. Don't waste time experimenting — start with Qwen.

## Path 3: The Hybrid (What I Actually Recommend)

**Use free models for 70% of daily tasks, escalate to paid models only when free genuinely fails.**

Pure free has limits. Local models struggle with complex multi-step reasoning. Free cloud tiers have rate limits. So here's what I actually run:

- **Default:** Ollama/Qwen3.5 (local, free). Handles file reads, calendar checks, simple summaries, web searches, reminders. About 70% of daily tasks.
- **Fallback:** Free cloud tier (Gemini Flash or OpenRouter free models). Catches anything the local model fumbles.
- **Emergency escalation:** Sonnet. Only for genuinely complex stuff. Maybe 5 times a week.

With this setup my last month's API spend was **$2.40**. Two dollars and forty cents. The Sonnet calls were the only ones that cost anything.

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen3.5:9b",
        "fallbacks": [
          "google-aistudio/gemini-3-flash-preview",
          "anthropic/claude-sonnet-4-6"
        ]
      }
    }
  }
}
```

OpenClaw handles the cascading automatically. If local fails or returns garbage, it tries the next model in the list. If that hits a rate limit, it goes to the next one. You don't have to manage this manually.

## What Works on Free Models

This surprised me — local and free cloud models handle more than I expected:

- **Reading and summarizing files.** Solid.
- **Calendar management, reminders, basic scheduling.** Fine.
- **Web searches and summarizing results.** Good enough.
- **Simple code edits, config changes, boilerplate.** Works.
- **Quick lookups** ("what's the syntax for X"). Instant and free.
- **Reformatting text, cleaning up notes, drafting short messages.** No issues.

## What Doesn't Work (Be Honest with Yourself)

- **Complex multi-step debugging.** Local models lose the thread after step 3. Use Sonnet for this.
- **Long nuanced conversations with lots of context.** Free models forget things faster with smaller context windows.
- **Anything where precision matters more than speed.** Legal, financial, medical analysis — pay for the good model.
- **Heavy tool chaining.** Five tools in sequence, each dependent on the last — that's Sonnet or Opus territory.

The mental model is simple: if you'd answer the question without thinking hard, a free model can handle it. If you'd need to actually sit down and reason through it, pay for reasoning.

## Hidden Costs Nobody Talks About

### Heartbeats Add Up

OpenClaw runs a health check every 30–60 minutes by default. If your primary model is Claude Opus, every heartbeat costs you tokens. On local models, heartbeats are free. On Opus, heartbeats alone can add $15–30+/month depending on your system prompt size and check frequency. That's the "I'm not even using my agent and my bill is growing" problem.

**Fix:** Set your heartbeat to use a cheap or free model separately:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "model": "google-aistudio/gemini-3-flash-preview"
      }
    }
  }
}
```

### Sub-Agents Inherit Your Primary Model

When your agent spawns a sub-agent for parallel work, that sub-agent uses whatever model you have set as primary. If primary is Opus, every sub-agent runs on Opus. With model fallbacks configured, this is less painful — but be aware of it.

### Context Window Bloat

Don't overload a free model setup with skills and plugins. Skills inject instructions into your context window. On an 8K–32K context local model, skills can eat half your available context before you even say hello. Learn what your agent can do stock first. Add skills later when you move to a cloud model with bigger context.

## Hardware for Local Models

<div class="affiliate-disclosure">Some links below are affiliate links — I earn a small commission at no extra cost to you. I only recommend hardware I've personally used or researched for local LLM use.</div>

If you're going the Ollama route, the hardware matters more than you think:

**Budget ($100-200) — Run 3B-7B models:**
- [Intel N100 Mini PC](https://www.amazon.com/dp/B0CWJ3X2JH?tag=devhandbook26-20) — Fanless, 16GB RAM, runs llama3.2 and gemma2 comfortably. The cheapest "always-on AI" box you can get.
- [Raspberry Pi 5 (8GB)](https://www.amazon.com/dp/B0CTG3JZ6S?tag=devhandbook26-20) — Surprisingly capable for small models. Great if you already have one.

**Mid-Range ($300-500) — Run 13B-30B models:**
- [Beelink SER7 Mini PC](https://www.amazon.com/dp/B0CR1JNMXL?tag=devhandbook26-20) — AMD 7840HS with 32GB RAM. Runs Proxmox beautifully, handles larger models on CPU.
- [32GB DDR5 SO-DIMM Kit](https://www.amazon.com/dp/B0C9V3HD87?tag=devhandbook26-20) — Max out your mini PC's RAM. More RAM = larger models = better responses.

**GPU Upgrade (if you have a desktop/server):**
- [NVIDIA RTX 3060 12GB](https://www.amazon.com/dp/B08WR34RFY?tag=devhandbook26-20) — 5-10x faster inference than CPU. Often found used for ~$200. The best bang-for-buck local LLM GPU.

## The Real Question

Most people who ask "how do I reduce my OpenClaw costs" are actually asking the wrong question. The right question is: **"which of my tasks actually need a $15/million-token model and which ones don't?"**

The answer, for almost everyone I've talked to, is that 60–80% of what they ask their agent to do could be handled by a model that costs nothing.

Start free. Move tasks up to paid models only when free genuinely can't handle them. Not when it feels slightly slower. Not when the formatting isn't perfect. When it actually fails.

The people spending $200/month on OpenClaw aren't getting 40x more value than I'm getting at $2.40. They're getting maybe 1.3x more value and paying for the convenience of not thinking about it.

Think about it. Your wallet will thank you.
