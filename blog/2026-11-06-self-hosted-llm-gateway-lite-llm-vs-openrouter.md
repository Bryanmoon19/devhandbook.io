---
layout: post.njk
title: "Self-Hosted LLM Gateway: LiteLLM vs OpenRouter vs the Rest (A Cost-First Guide for Homelabbers)"
date: 2026-11-06
description: "There's a quiet boom in open-source LLM gateways — LiteLLM, Portkey, OpenRouter, and a burst of new ones like antirion and llmbrake. They all do the same thing: route your request to the cheapest model that can do the job. The difference is who controls the keys, the cache, and the margin. Here's how to pick one, and why cost-first routing is the only sane way to run a homelab AI stack."
tags: ["litellm", "openrouter", "llm", "gateway", "routing", "ai", "self-hosted", "homelab", "cost", "portkey", "api", "local-llm", "antirion", "llmbrake"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-06-self-hosted-llm-gateway-lite-llm-vs-openrouter/"
affiliate: true
cta: true
---

There's a piece of infrastructure sitting in the middle of almost every serious homelab AI stack right now that nobody talks about as a *category*, because for two years there was only really one answer. It's the **LLM gateway** — the thing that sits between your apps and every model provider you use, taking a single OpenAI-compatible request and routing it to GPT, Claude, Gemini, or your local Ollama instance depending on what you asked and what it costs.

For most of that time, the answer was "LiteLLM, obviously." It's the de-facto standard, the router with the biggest community and the most provider support. But something changed in the last six months, and I want to name it before it gets too obvious: **the gateway category just exploded.**

Two years ago you had LiteLLM and a couple of half-finished projects. Today there's a *burst* of new gateways hitting GitHub every week — [antirion](https://github.com/antirion-ai/antirion), [llmbrake](https://github.com/llmbrake/llmbrake), Portkey's open-core offering, and a dozen more I've lost count of. Every single one of them is selling some version of the same pitch: **route your request to the cheapest model that can do the job, and don't overpay for the smart ones.**

That pitch is exactly why this post exists. Because if you're a homelabber running [local LLMs on a Mac mini](/blog/2026-10-09-local-llms-mac-mini/) and paying for [a few API providers on the side](/blog/2026-08-20-openrouter-stripe-ai-api-costs/), the gateway is the quiet piece in the middle that decides whether you spend $30/month or $300/month on the exact same workload. And the choice of gateway — self-hosted vs. hosted, and which one — is the single biggest lever you have over that number.

---

## What an LLM Gateway Actually Does

Before we compare anything, let me make sure we're looking at the same thing, because "gateway" gets thrown around to mean three different products.

At its core, an LLM gateway does four jobs:

1. **Translation.** It exposes one OpenAI-compatible API (`/v1/chat/completions`) and translates that into calls to whatever backend you point it at — OpenAI, Anthropic, Azure, Bedrock, Google, Ollama, vLLM, and a few dozen others. Your code never changes; the backend does.

2. **Routing.** This is the part that's gotten interesting. The gateway decides *which* model gets your request. That can be a static mapping ("send everything to Claude"), or it can be **cost-first routing** — "send this to the cheapest model that passes this quality bar, and fail over if it's down."

3. **Key management.** The gateway holds all your provider keys in one place, so your apps only need one key. This is convenient, and — as I wrote a few weeks ago — it's also [the single biggest security risk in your stack](/blog/2026-10-22-ai-gateway-supply-chain-security/).

4. **Cost accounting.** Logging, token counting, per-key budgets, per-model spend. The gateway is the natural place to answer "how much did I actually spend on AI this month" — which is why it ties directly into the [cost-tracking tooling](/blog/2026-08-12-ai-coding-agent-cost-tracking-tools/) I've written about before.

That's the whole category. The differences between products are *where* it runs, *who* holds your keys, and *how smart* the routing is. Everything else is detail.

---

## The Two Big Incumbents: LiteLLM and OpenRouter

If you've only heard of two of these, they're the two that matter, and they sit on opposite ends of the self-hosted spectrum.

### LiteLLM: self-hosted, you hold the keys

**LiteLLM** is the open-source standard. You run it yourself — a container or a pip package — and it holds *your* keys, routing to *your* providers. It supports the most providers of anything in the space, has the biggest community, and is the thing most homelab guides point you to.

The trade-off is that you now own a piece of infrastructure. You're responsible for updating it, securing it (remember the [supply-chain attack](/blog/2026-10-22-ai-gateway-supply-chain-security/) that hit the front page), and running it 24/7. You're also responsible for the routing logic yourself — LiteLLM gives you the primitives (budgets, fallbacks, retries, load balancing across providers), but the "route to the cheapest good model" behavior is something you *configure*, not something it does out of the box.

### OpenRouter: hosted, they hold the keys (and the margin)

**OpenRouter** is the opposite. It's a hosted aggregator — you pay one bill, get one API, and it routes your requests across ~300 models from dozens of providers. You don't run anything, you don't hold any provider keys, and the routing (including automatic fallback and, now, fairly sophisticated model selection) is done for you.

The trade-off is that you're paying for that convenience. OpenRouter [joined Stripe for ~$7B](/blog/2026-08-20-openrouter-stripe-ai-api-costs/), and the price you pay per token includes their margin on top of the underlying provider's price. For a homelabber doing real volume, that margin is the difference between "cheap enough not to think about" and "a line item I should optimize."

The clean way to think about it: **LiteLLM is a tool you operate. OpenRouter is a service you subscribe to.** Same category, opposite ends of the spectrum, and the choice between them is really a question about how much you want to optimize vs. how much you want to delegate.

---

## The New Wave: antirion, llmbrake, and Everything Else

Here's the part that's genuinely new, and it's why this post exists *now* rather than a year ago.

In the last few months, a burst of new open-source gateways have appeared on GitHub, and they're all converging on the same insight: **cost-first routing is the product, not a feature.** The pitch is no longer "route your requests to any provider" — LiteLLM won that years ago. The pitch is now "route your requests to the *cheapest* provider that's good enough, automatically, and save 40–70% without thinking about it."

Two examples worth knowing:

- **antirion** — one of the newer entrants, positioning itself around automatic cost optimization and quality-aware routing. The idea: you define a quality bar or a budget, and it picks models dynamically so you're never paying GPT-5.6 prices for a task a 20B model could handle.

- **llmbrake** — the name tells you the pitch: it's a "brake" on your spend. Rate limiting, budget caps, and cost-aware routing baked in from day one. If you've ever had a runaway agent loop burn through $50 in an afternoon, the value proposition is self-evident.

There are more — Portkey has pushed hard into the open-core gateway space, and there are half a dozen smaller projects whose names I keep seeing in "what are you using to route LLM calls" threads. The common thread across all of them: **they assume you already have multiple providers or a mix of local and cloud models, and they exist to make sure you're using the cheap one whenever you can.**

This is the shift, and it's worth internalizing. The gateway category used to be about *compatibility* — "talk to any model through one API." Now it's about *cost*. The compatibility problem is solved. The cost problem is not, and the new wave is racing to own it.

---

## Why Cost-First Routing Matters for Homelabbers Specifically

I want to make the case for why this matters to *you*, the person running a Mac mini and a couple of LXC containers, rather than to a startup with real inference spend. Because the startup case is obvious and the homelab case is actually more interesting.

Here's the thing: **homelabbers have the weirdest cost profile in AI.** You're not paying nothing (you have a few API subscriptions), and you're not paying real money (you're not a company). You're in the middle — you have [local models you can run for free](/blog/2026-10-09-local-llms-mac-mini/), and you have cloud models you pay per token for, and *which one handles a given request* is currently a decision you make manually, if you make it at all.

That's exactly what cost-first routing automates. Consider the workflow most of us actually run:

- **Coding agent, quick edits** → local 20–70B model, free, good enough.
- **Coding agent, hard refactor** → cloud frontier model, pay for it, because the local model will flail.
- **Summarization, classification, extraction** → local or cheap cloud, almost always good enough.
- **The occasional "actually think hard" task** → the expensive model, deliberately.

Right now, most homelabbers route *all* of that through one provider or one local endpoint, because setting up per-task routing is a pain. The result is you either overpay (everything goes to the frontier model) or you underperform (everything goes to the local model, including the tasks it can't do).

A cost-first gateway fixes that. It's the difference between "I pay a flat rate for the smart model and waste most of it" and "I pay per-request for exactly the intelligence I need, and the cheap stuff is effectively free."

---

## How to Pick: A Decision Framework

I'm going to give you the framework I actually use, because "LiteLLM vs OpenRouter vs the rest" is not a one-winner question. It's a "what's your situation" question.

### Go OpenRouter if…

- You want zero operational overhead. No container to patch, no keys to rotate, no supply-chain anxiety. (That last one is real — I wrote a whole [hardening playbook](/blog/2026-10-22-ai-gateway-supply-chain-security/) because LiteLLM *is* a thing you have to secure.)
- Your volume is modest and the margin doesn't sting. If you're spending $20–50/month, the convenience is worth more than the savings from optimizing.
- You want the best model available at any given moment, and you're fine letting OpenRouter decide what "best" means.

### Go self-hosted (LiteLLM or the new wave) if…

- You're mixing **local and cloud models**, and you want a single endpoint that routes between them. This is the homelab sweet spot, and it's the thing hosted aggregators can't reach (OpenRouter can't route to your Mac mini).
- You have **privacy or data-sovereignty** requirements. A self-hosted gateway means your routing metadata — and potentially your prompt data — never leaves your network.
- Your volume is high enough that OpenRouter's margin is real money, and you want to cut it.
- You **enjoy the control** and are already running the rest of your stack this way.

### Go to the new wave (antirion, llmbrake, etc.) if…

- Your primary pain is **runaway spend or overpaying for the smart model**, and you want cost-first routing as a first-class feature rather than something you hand-configure.
- You're willing to bet on a younger project. The trade-off: less maturity, smaller community, more churn. The upside: the routing logic is the product, and it's often better than what you'd hand-roll on LiteLLM.

### The honest default

For most homelabbers reading this, the honest answer is: **start with a self-hosted gateway because you have local models, and pick LiteLLM unless your actual pain is spend, in which case look at the cost-first new wave.** OpenRouter is the right answer when you *don't* have local models and you *don't* want to run anything — which describes a lot of people, but not the person who read this far into a self-hosted blog.

---

## The Tool Idea: An LLM Cost/Routing Calculator

I've been sitting on a tool idea for a few weeks that this post finally gives me an excuse to share, and I'm going to share it openly because I think it's genuinely useful and I want to build it.

The gap: **nobody has a calculator that tells you which gateway setup saves you the most money, given *your* actual usage.** There are cost calculators for [AI coding agents](/blog/2026-08-12-ai-coding-agent-cost-tracking-tools/) and [token usage](/token-counter/), but nothing that takes your workload mix and answers the routing question.

The tool, concretely:

- You input your **monthly token volume**, split by task type (coding, summarization, classification, reasoning, chat).
- You input your **available backends** — local models and their throughput, plus which cloud providers you have keys for.
- It computes the **cost under different routing strategies**: everything-to-frontier, everything-to-local, static split, and cost-first routing.
- It outputs a **break-even and savings number**, plus a recommended gateway (self-hosted vs. hosted, and which one) based on your volume and your local hardware.

The monetization angle is straightforward: it's a lead magnet for exactly the audience that then needs a gateway, an affiliate link, or a consulting conversation. Calculators are the most effective thing on this site for a reason — they're genuinely useful *and* they capture the exact person who's about to spend money. This one sits at the intersection of three posts I've already written (local LLMs, API cost math, and gateway selection) and it would tie the whole cluster together.

If you're reading this and you want it built sooner, tell me. It's on my list.

---

## The Checklist

For people who scrolled:

- **You have local models and cloud APIs** → run a self-hosted gateway. It's the only way to route between them.
- **You want zero ops and modest spend** → OpenRouter. Pay the margin, enjoy the convenience.
- **Your pain is overpaying for the smart model** → look at the cost-first new wave (antirion, llmbrake).
- **Whatever you pick, pin it and secure it** — a gateway holds all your keys, and that's [exactly what attackers target](/blog/2026-10-22-ai-gateway-supply-chain-security/).
- **Route the cheap stuff to the cheap models.** The single biggest homelab win is not "better hardware," it's "stop sending summarization jobs to the frontier model."

---

## The Verdict

The LLM gateway category just grew up, and the story is the same one this site keeps telling about self-hosting generally: **the boring infrastructure in the middle is where the money (and the risk) actually lives.**

For two years the question was "which gateway," and the answer was LiteLLM, full stop. Now the question is "which *kind* of gateway" — self-hosted vs. hosted, compatibility-first vs. cost-first — and the answer depends on whether you have local models, whether you want to run anything, and whether your pain is *spend* or *setup*.

The people who win here are the ones who stop treating the gateway as a default and start treating it as a decision. Your workload has a mix of tasks that need very different levels of intelligence, and you're currently paying for the smartest one across the board. Fix that — with a gateway, with cost-first routing, with a calculator that tells you the real number — and you've optimized the single biggest lever in your AI spend.

That's the whole post. The rest is just config.

---

*Where do you land on gateway choice now that the category has split? Are you running LiteLLM, paying OpenRouter, or trying one of the new cost-first routers? I'm genuinely curious how the homelab crowd is settling this — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

*If you found this useful, you might also like my pieces on [the LiteLLM supply-chain attack and how to harden your gateway](/blog/2026-10-22-ai-gateway-supply-chain-security/), [OpenRouter joining Stripe and the API-vs-self-hosted math](/blog/2026-08-20-openrouter-stripe-ai-api-costs/), and [tracking your AI coding costs](/blog/2026-08-12-ai-coding-agent-cost-tracking-tools/).*
