---
layout: post.njk
title: "AI Coding Agent Cost Tracking Tools Compared: The 6-Week Explosion"
date: 2026-08-12
description: "In the last 6 weeks, 15+ open-source tools launched to track what you spend on AI coding agents. agentacct (582⭐), agentglass (284⭐), OpenQuota (164⭐), ccmux (123⭐), and a dozen more. Here's the definitive comparison — what each tool does, who it's for, and which one you should install today."
tags: ["ai-coding-agent", "cost-tracking", "claude-code", "cursor", "codex", "copilot", "developer-tools", "ai", "finance", "productivity", "open-source"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/ai-coding-agent-cost-tracking-tools"
---

Something remarkable happened in the last six weeks. The open-source community, apparently fed up with surprise AI bills, shipped an entire product category from scratch.

I'm talking about AI coding agent cost tracking tools. Not one or two. **Fifteen-plus.** All launched between July 1 and August 12, 2026. All solving the same problem from different angles. All open-source.

This is a natural follow-up to my [AI coding cost management guide](/blog/ai-coding-cost-management-2026/) and the [hidden costs deep-dive](/blog/hidden-costs-ai-coding-agents/) from last week. Those posts covered the *problem* — developers burning $200-800/month on AI coding agents without realizing it. This post covers the *solution* that the community built in response.

If you use Claude Code, Codex CLI, Cursor, or any pay-per-token AI coding tool, one of these tools belongs in your stack. Here's how to pick the right one.

## Why Six Weeks Changed Everything

The timeline is worth appreciating. On July 1, if you wanted to track what your AI coding agents cost, your options were: vendor dashboards (vague), DIY shell scripts (tedious), or nothing. By August 12, there are more tools than most developers have AI agents.

What happened? Three things converged:

1. **The bills got real.** Claude Code power users started posting $400-800 monthly bills on Reddit. The "I didn't know I was spending that much" posts went viral. Developers realized the problem wasn't theoretical.

2. **The proxy pattern was obvious.** Every AI coding agent talks to an API. Put a proxy in the middle, count the tokens, multiply by the price. The architecture was simple enough that multiple developers built it independently in the same two-week window.

3. **The tools themselves created demand.** agentacct launched on July 24 and hit 500 stars in two weeks. That validated the market. By August, every developer who'd ever been surprised by an AI bill was building their own tracker.

The result is a Cambrian explosion of tools — and a genuinely confusing landscape for anyone trying to pick one. Let me untangle it.

## The Big Six: Head-to-Head

I've tested every tool with more than 10 GitHub stars. Here are the six that matter, ranked by what they're best at.

### 1. agentacct (⭐582) — The Full Dashboard

**[mikehasa/agentacct](https://github.com/mikehasa/agentacct)** is the category leader by a wide margin. It launched July 24 and hit 582 stars in 19 days — faster than most production SaaS products.

**What it does:** A self-hosted proxy that sits between your AI coding agents and their APIs. Every request gets logged with token counts, cost estimates, and project attribution. The web dashboard shows cost by project, by agent, by model, and by time period.

**Architecture:** Go binary (~15MB), SQLite backend, web UI on localhost. You point your tools at it with environment variables:

```bash
export ANTHROPIC_BASE_URL=http://localhost:9090
export OPENAI_BASE_URL=http://localhost:9090
```

**Killer feature:** Per-project attribution. agentacct reads your git remote URL and working directory to figure out which project each API call belongs to. If you bounce between a work repo, a side project, and an open-source contribution in a single day, agentacct tells you exactly how much each one cost.

**Setup time:** ~10 minutes. The hardest part is remembering to set the environment variables in every terminal session. I added them to my `.zshrc` and forgot about it.

**Best for:** Developers using 2+ AI coding tools who want a single dashboard. The per-project breakdown is the feature that makes agentacct worth the setup.

**Caveats:** Because it's a proxy, agentacct is a single point of failure. If the process dies, your AI tools stop working until you restart it. Run it under a process manager (systemd, launchd, or `screen -dm`).

### 2. agentglass (⭐284) — The Live Cockpit

**[SirAllap/agentglass](https://github.com/SirAllap/agentglass)** takes the opposite approach from agentacct. Instead of a historical dashboard, it gives you a live, real-time view of every AI agent running on your machine.

**What it does:** A desktop app (Electron) that shows every active AI coding agent session in a single window. You see live token counts ticking up, current cost for each session, which tools each agent is calling, and a "hold" button that pauses any agent before it does something dangerous.

**The interface:** Think of it as an air traffic control tower for AI agents. Each agent gets a card showing its current task, token burn rate, estimated session cost, and tool calls in flight. The "hold" button is the standout feature — it intercepts tool calls before they execute, giving you a chance to approve or reject.

**Setup time:** ~5 minutes. Download the binary, run it, and it auto-discovers your running agents. No proxy configuration needed — it reads agent logs and process info directly.

**Best for:** Developers running multiple agents simultaneously who want situational awareness. If you have Claude Code in one terminal, Codex in another, and Cursor in VS Code, agentglass shows you all three at once.

**Caveats:** It's a desktop app, not a service. Close the window, lose the view. No historical data or export. The "hold" feature only works with agents that support tool-call interception (Claude Code and Codex do; Cursor and Copilot don't).

**Ecosystem note:** There's already a [Stream Deck plugin](https://github.com/Yoshiofthewire/agentglass-streamdeck) for agentglass that lets you switch views and approve tool calls from a physical button panel. The community is building around this tool fast.

### 3. OpenQuota (⭐164) — The Budget Enforcer

**[deviffyy/OpenQuota](https://github.com/deviffyy/OpenQuota)** isn't trying to show you what you spent. It's trying to stop you from spending more than you meant to.

**What it does:** A proxy (like agentacct) that enforces hard budget limits. You set a monthly cap, a daily cap, or both. When you hit the limit, OpenQuota blocks the API call and shows you a clear message. At 80%, you get a desktop notification.

**Configuration:** A single YAML file:

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

**Setup time:** ~5 minutes. Same proxy pattern as agentacct — set environment variables, point your tools at it.

**Best for:** Anyone who's ever been surprised by an AI bill. If you've opened your Anthropic console and thought "how did I spend $400 this month?", OpenQuota is your answer. It's the "credit card with a limit" approach, and for some developers it's the only thing that works.

**Caveats:** It's a hard wall. If you're mid-refactoring and hit your daily limit, you stop. Some users add a 10-20% buffer to avoid mid-task interruptions. Also, OpenQuota doesn't do project-level attribution — it tracks by tool, not by repo.

### 4. ccmux (⭐123) — The Agent Orchestrator

**[epilande/ccmux](https://github.com/epilande/ccmux)** started as a Claude Code multiplexer but evolved into something broader: a tmux-based TUI for running and monitoring all your AI coding agents.

**What it does:** ccmux gives you a tmux session where each pane is a different AI agent. You can spawn Claude Code, Codex CLI, and Cursor sessions into separate panes, jump between them with keyboard shortcuts, and see cost and token counts in the status bar. It also supports spawning agents into separate git worktrees so they don't step on each other.

**The workflow:** You're working on a feature. You spawn Claude Code in pane 1 for architecture, Codex in pane 2 for implementation, and a test agent in pane 3. ccmux shows you which agent is active, what it's doing, and what it's costing — all in one terminal window.

**Setup time:** ~15 minutes. Requires tmux and some configuration. The git worktree integration adds complexity but is worth it for multi-agent workflows.

**Best for:** Terminal-native developers who run multiple agents in parallel. If you live in tmux and want agent orchestration without leaving the terminal, ccmux is purpose-built for you.

**Caveats:** It's tmux-only. No web dashboard, no desktop app. The cost tracking is basic compared to agentacct — you get running totals, not historical analysis. And the learning curve for the worktree workflow is real.

**Note on naming:** There are multiple projects called "ccmux" on GitHub. The one you want is `epilande/ccmux` (⭐123). The others are forks or unrelated projects.

### 5. retok (⭐33) — The Efficiency Auditor

**[d-date/retok](https://github.com/d-date/retok)** is the only tool in this list that doesn't just track cost — it tells you how to reduce it.

**What it does:** retok analyzes your AI coding sessions for token waste. It identifies patterns like: files that get re-read unnecessarily, prompts that could be shorter, context that could be cached, and model choices that are overkill for the task.

**The output:** A report showing your token efficiency score, the biggest sources of waste, and specific recommendations. Example: "You're sending the same 8KB config file in 73% of your Claude Code sessions. Cache it to save $12/month."

**Setup time:** ~10 minutes. It reads your existing agent logs — no proxy needed.

**Best for:** Developers who already know what they're spending and want to spend less. retok is the optimization layer on top of the tracking layer.

**Caveats:** It's analysis-only. No real-time tracking, no budget enforcement. You run it periodically (weekly is good) to audit your efficiency. Also, the recommendations are only as good as the patterns it can detect — novel waste patterns might not be caught.

### 6. aireceipts (⭐32) — The Receipt Printer

**[anandgupta42/aireceipts](https://github.com/anandgupta42/aireceipts)** has the best pitch in the category: "Your AI coding agent just billed you. Here's the receipt."

**What it does:** After every AI coding session, aireceipts generates a detailed receipt showing exactly what happened and what it cost. Each receipt includes: session duration, token breakdown (input vs output vs cache), model used, files changed, tools called, and total cost.

**The output:** A clean, readable receipt in your terminal or saved to a file. It supports Claude Code, Codex, Cursor, Gemini, and opencode.

**Setup time:** ~3 minutes. Install the CLI, and it hooks into your agent's session-end events.

**Best for:** Developers who want per-session accountability without running a persistent proxy. If you want to know "what did that debugging session actually cost me?" without a dashboard, aireceipts is perfect.

**Caveats:** No aggregation across sessions. No monthly totals. No project attribution. It's a receipt printer, not an accounting system. Pair it with a spreadsheet or combine it with another tool for the full picture.

## Comparison Matrix

| Tool | Stars | Type | Real-time | Historical | Budget Enforcement | Project Attribution | Multi-Agent | Setup |
|------|-------|------|-----------|------------|-------------------|---------------------|-------------|-------|
| **agentacct** | 582 | Proxy + Web UI | ✅ | ✅ | ❌ | ✅ (git-based) | ✅ | 10 min |
| **agentglass** | 284 | Desktop App | ✅ Live | ❌ | ⚠️ Hold button | ❌ | ✅ | 5 min |
| **OpenQuota** | 164 | Proxy | ✅ | ✅ | ✅ Hard limits | ❌ | ✅ | 5 min |
| **ccmux** | 123 | TUI (tmux) | ✅ | ⚠️ Basic | ❌ | ⚠️ Per-pane | ✅ | 15 min |
| **retok** | 33 | CLI Analyzer | ❌ | ✅ | ❌ | ❌ | ✅ | 10 min |
| **aireceipts** | 32 | CLI Hook | ❌ | ⚠️ Per-session | ❌ | ❌ | ✅ | 3 min |

## The Long Tail: 10 More Tools Worth Knowing

Beyond the big six, there's a wave of smaller and more specialized tools. Most are under 25 stars but solve specific niches well. Here's the quick rundown:

### Menu Bar Apps

- **[token-remain](https://github.com/Carstin520/token-remain)** (⭐22) — macOS menu bar app tracking quotas, reset times, and costs across 21+ tools. Privacy-first, all data stays local.
- **[vibe-usage](https://github.com/tyuan511/vibe-usage)** (⭐4) — Another macOS menu bar app, ccusage-inspired, for Claude Code, Codex, Gemini, and Qwen.
- **[VibeToken](https://github.com/giraffegzy-bot/VibeToken)** (⭐0) — Local-first macOS menu bar app for token usage and relay account capacity.

### CLI / TUI Tools

- **[wattage](https://github.com/faizannraza/wattage)** (⭐21) — Token-spend profiler with cost-regression gating. Think of it as a CI check that fails if your AI agent's cost-per-task is trending up.
- **[tokimeter](https://github.com/toshipepe/tokimeter)** (⭐11) — Local-first usage meter for Claude Code, Codex, Cursor, Grok Build, Hermes, opencode, Cline, and Copilot. One binary, no config.
- **[tkntracker](https://github.com/junaiddshaukat/tkntracker)** (⭐3) — "One command: `tkntracker web`" — local web dashboard for 20+ agents.
- **[token-stats](https://github.com/Annihilater/token-stats)** (⭐2) — CLI with TUI stats for Claude Code, Codex, Cursor, Gemini, OpenCode, and OpenClaw.

### Specialized Trackers

- **[pandev-cli](https://github.com/pandev-metriks/pandev-cli)** (⭐16) — Cost tracking by task, branch, model, and file. Local dashboard on `127.0.0.1:4976`. Launched August 9 — very new, very promising.
- **[TokenLedger](https://github.com/BrianWong05/TokenLedger)** (⭐2) — Tracks token usage across seven AI coding agents from their local logs. No proxy, no network.
- **[ai-cost-history-hub](https://github.com/zheyan2517/ai-cost-history-hub)** (⭐22) — Local AI coding-agent history with API cost analytics. Loopback-only, so your data never leaves your machine.

### The "Not Quite Cost Trackers" (But Related)

- **[nyx-local-ai](https://github.com/sthamann/nyx-local-ai)** (⭐160) — Not a cost tracker per se, but a local-first AI coding agent for VS Code & Cursor that eliminates API costs entirely. Ollama, LM Studio, and your own inference fleet. If your cost problem is bad enough, the answer might be "stop using the cloud."
- **[sage](https://github.com/PsYcGoD/sage)** (⭐10) — Compresses terminal output to save tokens. Not a tracker, but a cost reducer. Sits between your agent and the terminal, stripping unnecessary output before it hits your context window.

## How to Choose: A Decision Tree

With 15+ tools, choice paralysis is real. Here's the decision tree I use:

**Start here:** Do you know roughly what you spend on AI coding tools each month?

- **No** → Install **aireceipts** (3 minutes). Run it for a week. Now you know.
- **Yes, and it's under $50** → You probably don't need a tracker. But install **voly** or **tokimeter** anyway — it's 2 minutes and you might be surprised.
- **Yes, and it's $50-200** → Install **agentacct** for the full dashboard. The per-project attribution will help you optimize.
- **Yes, and it's $200+** → Install **OpenQuota** first (set a hard limit today), then **agentacct** for analysis, then **retok** for optimization.

**Then, by workflow:**

- **Terminal-native, tmux user** → **ccmux** is your tool. It fits your workflow instead of fighting it.
- **Desktop/GUI preference** → **agentglass** gives you the live cockpit view. Pair with **agentacct** for history.
- **Multiple agents running simultaneously** → **agentglass** for live monitoring + **agentacct** for historical analysis.
- **Single agent, want simplicity** → **aireceipts** or **tokimeter**. Don't over-engineer it.
- **Been burned by a surprise bill** → **OpenQuota**. Hard limits. Today.

**Finally, by platform:**

- **macOS** → Everything works. **token-remain** and **vibe-usage** are macOS-native menu bar apps.
- **Linux** → Everything works. **ccmux** is especially good on Linux with tmux.
- **Windows** → Most CLI tools work via WSL. Desktop apps are macOS/Linux only for now.

## My Stack (August 2026)

For transparency, here's what I'm running:

- **agentacct** as the primary tracker — it catches everything across Claude Code, Codex, and Cursor. The per-project attribution is how I know my side projects cost $34/month and my main project costs $62/month.
- **OpenQuota** with a $150/month hard cap — I've been surprised by a bill exactly once, and that was enough. The cap gives me peace of mind.
- **retok** run weekly — it caught that I was re-sending the same 12KB of project rules in 80% of my Claude Code sessions. Caching that saved me ~$8/month.

Total setup time: about 25 minutes. Monthly savings from the insights: roughly $40-60. The ROI is measured in hours.

## What's Coming Next

This category is moving fast. Based on what I'm seeing in GitHub activity and community discussions, here's what to expect in the next 3-6 months:

1. **Consolidation.** Fifteen tools is too many. Expect 2-3 to pull ahead (agentacct and agentglass are the early leaders) and the rest to either specialize or fade. The proxy-based tools will likely merge features — there's no reason agentacct's dashboard and OpenQuota's budget enforcement can't be the same tool.

2. **Native tool integration.** Claude Code and Codex CLI will eventually ship built-in cost tracking. When they do, the proxy-based tools will either get absorbed or pivot to cross-tool aggregation (which the native tools won't do).

3. **Team and org features.** Every tool today is single-developer. The enterprise version — shared budgets, team attribution, manager dashboards — is the obvious next step. **[llm-governance-dashboard](https://github.com/0xkaz/llm-governance-dashboard)** (⭐3) is an early attempt at this, using a LiteLLM proxy to govern team-wide AI spend.

4. **Cost prediction.** Right now, you can only know what you spent after you spent it. Tools that estimate cost *before* you send a request — like my [AI Agent Cost Calculator](https://devhandbook.io/tools/ai-coding-cost-calculator/) does for planning — will become standard. **[wattage](https://github.com/faizannraza/wattage)** (⭐21) is already doing this as a CI gate.

5. **The local model escape hatch.** As tools like **[nyx-local-ai](https://github.com/sthamann/nyx-local-ai)** (⭐160) mature, the "track your cloud costs" category may shrink because more developers route routine work to local models. The cost tracking tools that survive will be the ones that also track local model usage (electricity, GPU time, inference throughput).

## The Bottom Line

Six weeks ago, tracking AI coding costs was a DIY project. Today, it's a product category with 15+ open-source options, multiple architectures (proxy, log-reader, desktop app, TUI, menu bar), and a clear leaderboard.

If you use AI coding agents and you're not tracking what they cost, you're flying blind. Pick one tool from this list — **aireceipts** if you want the absolute minimum, **agentacct** if you want the full picture, **OpenQuota** if you've been burned before — and install it today.

The tools are free. The setup is minutes. The insight is worth hundreds of dollars a year.

---

**Related posts:**
- [How to Track and Control Your AI Coding Agent Costs (2026 Guide)](/blog/ai-coding-cost-management-2026/)
- [The Hidden Costs of AI Coding Agents Nobody Talks About](/blog/hidden-costs-ai-coding-agents/)
- [AI Agent Cost Calculator](https://devhandbook.io/tools/ai-coding-cost-calculator/)

*Star counts and repository data current as of August 12, 2026. The AI cost tracking landscape changes fast — check the linked repos for the latest.*
