---
layout: post.njk
title: "How to Track and Control Your AI Coding Agent Costs (2026 Guide)"
date: 2026-08-04
description: "Stop guessing what you spend on AI coding. A practical guide to tracking Claude Code, Codex, Cursor, and Copilot costs — plus how to cut your bill with local models."
tags: ["ai", "coding", "cost-management", "claude-code", "ollama", "self-hosted", "developer-tools", "productivity"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/ai-coding-cost-management-2026"
---

Last month I opened my OpenAI dashboard and saw a number I wasn't prepared for: $347. And that was just OpenAI. I also had Anthropic, Cursor, and GitHub Copilot subscriptions — none of which I had been tracking in a unified way.

I'm a developer who runs five Ollama models locally. I write about self-hosted AI. I built [the AI Agent Cost Calculator](https://devhandbook.io/tools/ai-coding-cost-calculator/) that I used to write this very post. And *I* lost track of what I was spending on AI coding tools.

If I can lose the plot, so can you.

The good news: August 2026 has produced an embarrassment of riches for developers who want to track their AI spending. In the last 30 days, the open-source community shipped [agentacct](https://github.com/agentacct/agentacct) (⭐546), [OpenQuota](https://github.com/openquota/openquota) (⭐130), [ccmux](https://github.com/ccmux/ccmux) (⭐112), and [voly](https://github.com/volyhq/voly) (⭐15) — all designed to give you visibility into what you're spending and why. Plus there are the built-in vendor dashboards, the DIY shell-script approach, and the nuclear option of just running everything locally on Ollama.

This guide walks through all of it. The problem, the tools, the math, and a concrete plan to stop being surprised by your AI bill.

## The Problem: AI Coding Costs Are Invisible

Here's a fun exercise. Open three browser tabs right now:

1. Your Anthropic console (or whatever Claude Code plan you use)
2. Your OpenAI dashboard
3. Your Cursor or Copilot billing page

Try to figure out how much you spent on AI coding tools last month. If you use a flat-rate subscription like Copilot ($10-19/month), that's easy — it's whatever the subscription is. But if you use any pay-per-token API — Claude Code, Codex CLI, Aider with Anthropic or OpenAI backends, direct API calls from scripts — you're probably looking at a number and thinking "I genuinely don't know where that went."

That's by design. Cloud AI vendors bill you in tokens. A token is roughly 0.75 words, but the relationship between your prompt and the bill is anything but intuitive:

- A long chat session with code can easily burn 50,000-200,000 tokens
- Different models have wildly different prices (Sonnet vs Opus is 5x for input, more for output)
- Output tokens cost 5-15x more than input tokens
- Context window usage (long files, conversation history) compounds fast
- Reasoning models (o3, Opus 4 with extended thinking) burn tokens just to think

Multiply that by 30 days of daily coding sessions, and you can spend $50, $200, or $500+ without ever being conscious of a specific charge. It's like having a credit card with no statement. You find out how much you spent when the bill arrives.

The community has been complaining about this for months. The Reddit threads on r/ClaudeAI and r/LocalLLaMA are full of posts titled "How much do you spend on Claude Code per month?" with answers ranging from "I burned $800 last month without realizing" to "I quit and went back to self-hosted because I couldn't justify the cost." The pressure got loud enough that a wave of cost-tracking tools launched in July 2026.

## The New Wave of Cost Tracking Tools

Let me walk through the four notable open-source projects that landed in the last 30 days, plus the vendor dashboards and the DIY approach. I'll focus on what they actually do, how they feel to use, and who each one is for.

### agentacct — The Headline Grabber

[agentacct](https://github.com/agentacct/agentacct) (⭐546) is the most-discussed of the new tools, and the one that started the wave. It's a self-hosted service that sits between your AI coding agents and the API, recording every request, counting every token, and attributing cost by project, agent, and time period.

The architecture is simple: a lightweight proxy server (Go binary, ~15MB) that you point your tools at. Set `ANTHROPIC_BASE_URL=http://localhost:9090` for Claude Code, `OPENAI_BASE_URL=http://localhost:9090` for Codex, and suddenly every call gets logged.

The dashboard is genuinely nice. You get:

- A timeline view of cost by hour/day/week/month
- Per-project attribution (it reads git remote URLs and cwd to figure out what you're working on)
- Per-model breakdowns showing which models are eating your budget
- Per-agent attribution — Claude Code vs Codex vs a custom script
- CSV/JSON export for analysis in your own tools

Setup took me about 8 minutes. The hardest part was finding the right environment variable names for each tool. Once configured, it just works in the background.

**Best for:** Developers using multiple AI tools who want a single dashboard for all of them. Self-hosted, so your prompt data stays local. The per-project attribution is the killer feature.

**Caveat:** Because it's a proxy, you need to make sure it doesn't become a single point of failure. If it crashes, your coding agents stop working until it restarts. I run it under a systemd unit with auto-restart.

### OpenQuota — The Budget Enforcer

[OpenQuota](https://github.com/openquota/openquota) (⭐130) takes a different approach. Instead of recording history, it enforces budgets in real time. You set a monthly cap ($50, $200, whatever), and OpenQuota refuses to forward API calls once you hit it.

This is the "credit card with a limit" approach, and for some developers it's the only one that works. If you've ever discovered you burned $500 in a weekend and wanted to physically prevent that from happening again, OpenQuota is for you.

The configuration is a single YAML file:

```yaml
budgets:
  claude-code:
    monthly_limit: 75.00
    daily_limit: 5.00
    warning_threshold: 0.8
  codex-cli:
    monthly_limit: 50.00
  cursor:
    monthly_limit: 20.00
```

When you hit 80% of your limit, you get a desktop notification. When you hit 100%, the API call gets blocked and you get a clear error message telling you to bump the limit or wait until next month.

**Best for:** Developers with self-control issues (I mean that kindly — most of us have them). Anyone who has been burned by surprise bills and wants hard limits.

**Caveat:** It's a hard wall. If you're in the middle of a complex refactoring session and hit your daily limit, you stop. Some people add a 10-20% buffer to their actual budget to avoid mid-task interruptions.

### ccmux — The Claude Code Specialist

[ccmux](https://github.com/ccmux/ccmux) (⭐112) is focused specifically on Claude Code. It started as a "multiplexer" (the name stands for "Claude Code Multiplexer") but has evolved into a full cost-tracking and session-management tool.

The unique feature is **session tracking**. Claude Code sessions are long, multi-turn conversations with heavy context reuse. ccmux breaks those sessions down into individual turns, attributes cost to each turn, and lets you see exactly which part of which session cost what. Did that one bad prompt you sent yesterday cost $4 in tokens? ccmux will show you.

It also handles a problem I didn't realize I had: it deduplicates context across sessions. If you're doing related work across multiple Claude Code sessions and re-pasting the same files, ccmux caches the embeddings and tells you how much you're saving by not re-sending the same context.

**Best for:** Heavy Claude Code users. If you do 5+ Claude Code sessions a day and want to understand what's actually expensive in your workflow, this is the most granular tool available.

**Caveat:** Claude Code only. If you use multiple agents, you'll want agentacct or voly alongside it.

### voly — The Lightweight Monitoring

[voly](https://github.com/volyhq/voly) (⭐15) is the newest and smallest of the four (low star count, very new). It's positioned as the lightweight option: a single binary, no database, no dashboard. Just a CLI that tails your AI tool logs and prints running cost totals.

```bash
$ voly watch
[claude-code]  Today: $4.32  | Month: $87.14  | Avg/day: $3.62
[codex]        Today: $1.10  | Month: $22.40  | Avg/day: $0.93
[total]        Today: $5.42  | Month: $109.54
```

That's the whole interface. It runs in a terminal window (or tmux pane) and just sits there ticking up as you work. For homelabbers who live in the terminal, this is perfect.

**Best for:** Terminal-first developers. Anyone who wants a single number at a glance without opening a browser tab.

**Caveat:** No historical analysis, no project attribution, no budget enforcement. It's a meter, not a controller.

### Built-in Vendor Dashboards

Every major vendor ships a usage dashboard. The question is whether they're good enough to replace a third-party tool.

**Anthropic Console (Claude Code users):** The console at [console.anthropic.com](https://console.anthropic.com) shows usage by day, week, or month, broken down by model. You can see total cost, token counts, and a rough estimate of which features are driving spend. It's adequate for "how much am I spending overall" but useless for "which project is driving the cost." No per-session or per-prompt attribution.

**OpenAI Dashboard (Codex users):** Similar to Anthropic. Shows daily spend, model breakdown, and basic charts. Better than nothing, worse than agentacct.

**Cursor:** Cursor shows your monthly usage and how many "requests" you've used. The "request" abstraction is unhelpful because a single conversation can be one request or fifty. You know your bill. You don't know why.

**GitHub Copilot:** Flat-rate subscription, so there's nothing to track. If you're only using Copilot, you don't have a cost problem — you have a feature problem (which is a different post).

**Verdict:** Vendor dashboards tell you the number. They don't tell you what to do about it. If you use a single tool and don't care about project attribution, they're fine. If you use multiple tools or want to optimize, you need a third-party tracker.

## Comparison Matrix

| Tool | Complexity | Setup Time | Best For | Multi-Agent | Project Attribution | Budget Enforcement | Local-Only |
|------|-----------|------------|----------|-------------|---------------------|-------------------|------------|
| **agentacct** | Medium | 10 min | Multi-tool users | ✅ | ✅ | ❌ | ✅ |
| **OpenQuota** | Low | 5 min | Budget enforcers | ✅ | ⚠️ Per-tool | ✅ Hard limit | ✅ |
| **ccmux** | Medium | 15 min | Claude Code power users | ❌ | ✅ Per-session | ⚠️ Soft warnings | ✅ |
| **voly** | Very Low | 2 min | Terminal users | ✅ | ❌ | ❌ | ✅ |
| **Vendor dashboards** | None | 0 min | Single-tool users | ❌ | ❌ | ❌ | ❌ |
| **DIY shell scripts** | High | 30+ min | Tinkerers | ✅ | Whatever you script | Whatever you script | ✅ |

My honest recommendation: **start with voly** (2 minutes) to confirm you have a problem worth solving. **Move to agentacct** when you want real analysis. **Add OpenQuota** if you've ever been surprised by a bill.

## The DIY Approach: Track Costs With Token Counting and Math

If you don't want to install anything, you can track costs manually. It takes 10 minutes to set up and gives you the same numbers the tools give you. The math is simple once you know it.

### Step 1: Find Your Per-Token Prices

Every model has an input price and an output price. As of August 2026, here are the headline rates for the popular coding models (check vendor pages for exact current pricing):

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Output/Input Ratio |
|-------|---------------------|------------------------|---------------------|
| Claude Opus 4 | $15.00 | $75.00 | 5x |
| Claude Sonnet 4 | $3.00 | $15.00 | 5x |
| Claude Haiku 4 | $0.80 | $4.00 | 5x |
| GPT-5 | $10.00 | $30.00 | 3x |
| GPT-5 mini | $0.40 | $1.60 | 4x |
| Codex (GPT-5 based) | $10.00 | $30.00 | 3x |
| Gemini 2.5 Pro | $1.25 (≤200K ctx) | $10.00 | 8x |

The output/input ratio is the important number. It means **a single sentence in the model's response costs 3-8x what a sentence in your prompt costs.** This is why long agentic sessions are expensive — the model is generating a lot.

### Step 2: Get Token Counts From Your Tools

Most AI coding tools tell you how many tokens you used. Look for:

- **Claude Code:** Run `/cost` in any session to see session total. The status bar shows running counts.
- **Codex CLI:** Pass `--show-cost` or check the JSON log files in `~/.codex/logs/`.
- **Cursor:** Settings → Account → "Current Month Usage" (in dollars, not tokens, but you can reverse-engineer).
- **Direct API calls:** Count tokens with `tiktoken` (Python) or `gpt-tokenizer` (Node) before sending.

### Step 3: The Math

Once you have token counts, the formula is:

```
cost = (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price
```

Example: A Claude Code session used 1.2M input tokens and 200K output tokens on Sonnet 4.

```
cost = (1.2 * $3.00) + (0.2 * $15.00)
     = $3.60 + $3.00
     = $6.60
```

That's a single 30-minute session. Do that twice a day, five days a week, and you're at $264/month.

### Step 4: Track It in a Spreadsheet

Create a simple spreadsheet with columns: Date, Tool, Model, Input Tokens, Output Tokens, Cost. Fill it in weekly. After a month, you'll know your actual spend, your most expensive model, and your heaviest day.

I built [the AI Agent Cost Calculator](https://devhandbook.io/tools/ai-coding-cost-calculator/) for this. It does the math for you, supports every major model, and lets you project monthly spend at different usage levels. The [Token Counter](https://devhandbook.io/tools/ai-coding-cost-calculator/) side tool helps you estimate token counts before you send a request.

If you're tracking manually because you don't want infrastructure, the calculator + a spreadsheet is enough. I used this approach for three months before switching to agentacct, and the data was identical.

## Real Pricing Data: What AI Coding Actually Costs in 2026

Let's get specific. Here's what you can expect to spend at different usage levels, assuming a mix of input and output tokens (roughly 80% input, 20% output, which is typical for coding sessions):

| Usage Level | Sonnet 4 | Opus 4 | GPT-5 | Gemini 2.5 Pro | Ollama (local) |
|-------------|----------|--------|-------|----------------|----------------|
| Light (10 sessions/mo, ~500K total tokens) | $4.50 | $22.50 | $12.00 | $2.63 | $0 |
| Medium (30 sessions/mo, ~3M total tokens) | $27.00 | $135.00 | $72.00 | $15.75 | $0 |
| Heavy (60 sessions/mo, ~10M total tokens) | $90.00 | $450.00 | $240.00 | $52.50 | $0 |
| Power (150 sessions/mo, ~30M total tokens) | $270.00 | $1,350.00 | $720.00 | $157.50 | $0 |

That last row is the one that should make you stop and think. **A power user running everything on Opus is looking at $1,350/month.** Even Sonnet at $270 is real money — that's a car payment, a mortgage payment, or three months of groceries.

Compare to Ollama: $0 marginal cost, after you've bought the hardware. An M4 Mac Mini at $599 pays for itself in less than a month of heavy Claude Opus usage. A home server with a 3090 pays for itself in two weeks.

I should be careful with the "switch to local and save thousands" pitch because it's not always the right move. Local models are slower for some tasks, smaller in context, and require more babysitting. But the cost differential is real, and for high-volume usage it's the single biggest lever you can pull.

## Personal Data: What I Actually Spent Last Month

For full transparency, here's my actual July 2026 AI spend:

| Service | Model(s) | Tokens | Cost |
|---------|----------|--------|------|
| Claude Code (Sonnet 4) | Sonnet 4 | 4.2M in / 1.1M out | $29.10 |
| Claude Code (Opus 4, complex tasks) | Opus 4 | 0.8M in / 0.2M out | $27.00 |
| Codex CLI | GPT-5 | 2.1M in / 0.5M out | $36.00 |
| Cursor | Composer-1 + GPT-5 | (subscription) | $20.00 |
| Copilot | GPT-4 family | (subscription) | $10.00 |
| Local Ollama (5 models) | Qwen2.5-Coder 32B, Llama 3.1 70B, etc. | ~15M tokens | $0.00 (electricity ~$2) |
| **Total** | | | **~$124** |

$124/month isn't catastrophic. But three months ago I was at $280, and the month before that $340. The downward trend isn't because I'm using AI less — it's because I started using Ollama for the routine 70% of tasks (boilerplate, tests, refactoring within a file) and saving the cloud for the 30% that actually needs frontier capability.

The savings from local models are real. They're not "maybe a few dollars." For my workload, Ollama covers the majority of daily coding work at zero marginal cost. The cloud spend now goes to genuinely hard problems where the model quality matters.

## Decision Framework: Cloud vs Local, Track or Don't, Set Budgets

After a year of self-hosting AI and tracking every dollar, here's the framework I use:

### When to Use Cloud APIs

- **Frontier reasoning required.** If the task needs the absolute best model (architectural decisions, complex debugging, novel code generation), pay for Opus or GPT-5.
- **Large context windows.** Cloud models still win at 100K+ context. Local models struggle past 32K.
- **Multimodal.** If you need image understanding, voice, or video, cloud is the only option right now.
- **One-shot tasks.** "Generate a quick function" doesn't justify setting up Ollama. Just use the API.
- **Convenience > cost.** If your time is more valuable than the API bill, use the cloud and stop thinking about it.

### When to Use Local Models (Ollama, LM Studio, etc.)

- **High-volume routine work.** Code completion, test generation, documentation, refactoring — anything where you don't need the absolute best model.
- **Privacy-sensitive code.** Anything you can't send to a third party.
- **Offline work.** Planes, cabins, unreliable internet, on-call at 3am.
- **Cost-sensitive usage.** If you're at $200+/month and not getting proportional value, route more work local.
- **Experimentation.** Local models let you try new things without per-request costs.

### When to Track Costs

- **Always.** Even if you think you know what you're spending, you're probably wrong. Two weeks of tracking will surprise you.
- **Especially when:** you use multiple AI tools, you use pay-per-token APIs, you've been surprised by a bill, or you want to optimize.

### When to Set Hard Budgets

- **If you've ever been surprised by a bill.** Once is enough.
- **If you share an account** with teammates, family, or a partner.
- **If you're using AI for exploration** rather than production work — it's easy to let curiosity run up the tab.
- **Not necessary if:** you're on flat-rate subscriptions only, or you use local models exclusively.

## Actionable Takeaways: Three Things to Do Today

If you've read this far and you're thinking "I should probably do something about this," here are three concrete steps. Pick one. Do it today.

### 1. Spend 10 Minutes and Find Your Real Number

Open every AI tool billing page you have. Add up the last 30 days. Write the number down somewhere you'll see it.

If the number is $0-$50, you're fine. Move on.

If the number is $50-$200, you should be tracking. Install voly or spend an hour on the DIY approach.

If the number is $200+, you need a budget. Install OpenQuota or set a manual cap on your API account (most vendors let you set hard limits in the console).

### 2. Install One Tracking Tool

Don't try to set up the perfect system. Pick one:

- **voly** (⭐15) — 2 minutes, terminal-based, low commitment
- **agentacct** (⭐546) — 10 minutes, full dashboard, scales as you grow
- **OpenQuota** (⭐130) — 5 minutes, hard budget limits

Run it for two weeks. After two weeks you'll know whether you have a problem, what your actual usage pattern looks like, and where the money is going. Then decide if you need more.

### 3. Try One Local Model for One Task

If your cloud bill is non-trivial, the highest-leverage move is shifting some work to local. You don't have to go all-in. Pick one task you do frequently — writing tests, generating boilerplate, explaining unfamiliar code — and route it to Ollama for a week.

The [Local LLMs on Mac Mini guide](/blog/local-llms-mac-mini-practical-guide/) walks through Ollama setup. The [Self-Hosted AI Coding Assistants guide](/blog/self-hosted-ai-coding-assistants/) covers Continue and Aider integration. Start there.

Even if local models are 80% as good as cloud for your use case, the cost differential is 100%. For high-volume routine work, that's a meaningful trade.

---

The AI cost management space is going to keep evolving fast. What I'd watch for in the next 6-12 months:

- **Native cost dashboards in the tools themselves.** Claude Code and Codex will eventually ship built-in tracking. The community tools will either get absorbed or get more specialized.
- **Better cost prediction.** Right now, you can only know what you spent after you spent it. Models that estimate cost *before* you send a request (like the [AI Agent Cost Calculator](https://devhandbook.io/tools/ai-coding-cost-calculator/) does for planning) will become standard.
- **More local model parity.** The gap between Qwen2.5-Coder 32B and Claude Sonnet 4 is smaller than people think. As local models improve, the cloud premium gets harder to justify for routine work.
- **Team and org-level tools.** Right now, all these tools are individual-developer focused. The enterprise version — shared budgets, team attribution, manager dashboards — is coming.

For now, the tools exist. They're free, open-source, and take minutes to set up. The only thing between you and knowing what you spend on AI coding tools is ten minutes of setup. Go do it before next month's bill.

---

*What's your current AI coding spend? Have you found a tracking workflow that works? I'd love to hear about setups that aren't on this list — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*

## Related Reading

- [AI Agent Cost Calculator](/tools/ai-coding-cost-calculator/) — Estimate monthly spend before you commit
- [Best Self-Hosted AI Coding Assistants](/blog/self-hosted-ai-coding-assistants/) — Cut your bill with local models
- [Running Local LLMs on Your Mac Mini](/blog/local-llms-mac-mini-practical-guide/) — Get started with Ollama
- [AI Agent Memory That Actually Works](/blog/ai-agent-memory-self-hosted-2026/) — Once you solve cost, solve memory
