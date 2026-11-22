---
layout: post.njk
title: "Run an AI Agent on Your Phone: Mika and the On-Device Agent Wave That Finally Arrived"
date: 2026-11-22
description: "Mika (~9,500★) puts a real AI agent on your Android phone — it taps, types, scrolls, and browses on a hidden background screen using your own model key. DeepSeek's superagent prototype (~24,000★) points at where autonomous agents are heading. The mobile/on-device gap this site never covered is closing fast. Here's what on-device agents actually are, what Mika does (and how it works), and why your homelab is about to meet your pocket."
tags: ["ai-agent", "on-device", "android", "mobile", "local-llm", "deepseek", "mika", "automation", "self-hosted", "homelab", "llm-agents", "open-source"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-11-22-on-device-ai-agents-mika-deepseek-superagent/"
affiliate: false
cta: true
---

# Run an AI Agent on Your Phone: Mika and the On-Device Agent Wave That Finally Arrived

devhandbook.io has written a lot about AI agents over the last two years — coding agents, MCP servers, SKILL.md procedures, sandboxing, cost tracking, local LLMs on a Mac mini. But there's been a glaring hole in that coverage, and I'll own it: **almost everything I've written assumes your agent lives on a server or a laptop, behind a terminal or a browser tab.**

That assumption quietly died this month.

Two repositories exploded out of nowhere in the last three weeks, and together they mark a genuine inflection point. One of them puts an autonomous agent *on your phone* — not a thin client to a cloud API, but something that actually operates the apps and websites on your device. The other is DeepSeek's reference implementation of a "more autonomous agent system," and it's a roadmap for where the whole category is heading. Between them, the "on-device agent" stopped being a research-adjacent novelty and became something you can install tonight.

Let me show you what changed, why it matters for self-hosters in particular, and how to actually run one of these things.

---

## Two Repos, Three Weeks, ~34,000 Stars

The raw numbers first, because the velocity is the story:

| Repo | What it is | Stars | Created | Language | License |
|------|-----------|-------|---------|----------|---------|
| [**Mika**](https://github.com/wangzan101/Mika) | On-device AI agent for Android that operates apps and the web | **~9,500** | Oct 29, 2026 | Kotlin | Apache-2.0 |
| [**dsh-superagent**](https://github.com/deepseek-ai/dsh-superagent-prototype) | DeepSeek's proactive coding agent / autonomous-agent prototype | **~24,000** | Oct 31, 2026 | TypeScript | MIT |

Mika hit ~9,500 stars and 2,100+ forks in a little over three weeks, with the `#1 Kotlin repository of the day` and `#5 repository of the day` badges on Trendshift to show for it. dsh-superagent went from zero to ~24,000 stars and 3,000 forks in the same window. These are not slow-burn homelab tools grinding out a star a week. These are events.

But here's the thing worth noticing: **they're signals of the same underlying shift, from opposite ends.**

- **Mika** is the *surface* story — the agent moved to the device you carry, and it drives real apps with screen taps instead of API calls.
- **dsh-superagent** is the *architecture* story — DeepSeek published the design of an agent that takes minimal human attention and gives maximum value, acting only when asked or when rules allow.

One tells you *where* agents now live. The other tells you *how* they should behave. Both matter.

---

## What Mika Actually Is

Mika's one-liner from its README is deceptively simple:

> **An AI assistant on your phone: say what you need, and it works your apps and the web until it's done.**

The part that separates it from Siri, Gemini, or a chatbot app is the mechanism. Mika does **not** talk to app APIs. There's no per-app integration layer. It **looks at the screen and finds buttons the way a person does** — using Android's accessibility and UI-automation primitives to tap, type, scroll, and read. And it does all of this on a **hidden background screen**, so you keep using your phone while it works.

That last detail is the big one. Every "agent" demo I've seen for the last two years either took over your screen (blocking you) or ran somewhere else (not on your device). Mika threads the needle: it drives a *separate virtual display*, so the agent and the human use the phone at the same time. There's a small floating capsule you can tap to watch the live view — and double-tap to hand it the screen you're currently looking at.

### What it can actually do

The feature set is broader than "taps buttons":

- **Operate apps** — reads long lists and chat histories, taps, types, shares text into apps. Hands logins, verification codes, and payments back to *you* rather than doing them itself.
- **Browse the web** — a built-in desktop-class browser that stays signed in, reads pages, downloads, uploads, and paces itself; hands CAPTCHA/block pages to you.
- **Current screen** — double-tap the capsule to send whatever you're looking at: "how should I reply?", "note this down."
- **Schedules and conditions** — "Remind me at 9 tomorrow," "do this every Friday," "check the weather at 8 every morning and tell me only if it'll rain." It runs on time inside the original conversation.
- **Files and computing** — a per-conversation Linux sandbox that runs Python, Node, and shell on the files you send (arm64).
- **From your computer** — AI tools on your machine can hand Mika tasks through a CLI + Skill or MCP. Your homelab agent can *delegate to your phone.*

The README demos run the full spectrum: "send a message to File Transfer" (opens WeChat on the background screen, finds the contact, sends the message), "what did the group talk about today?" (scrolls a group chat and summarizes it), "a charger under $30, rated 4.5 stars or more" (picks one on Amazon and adds it to cart, stopping before checkout), "greet recruiters for these 3 jobs," "find the cheapest nonstop from SFO to NYC."

### The self-hoster hook: there is no Mika server

This is where it becomes a devhandbook.io story rather than just a cool app:

> **"There is no Mika server; use your own model API key, or sign in with a ChatGPT, xAI or OpenRouter account."**

You point it at whatever model you want. If you run Ollama, vLLM, or anything OpenAI-compatible in your homelab — or you route through OpenRouter — Mika will use it. Your phone becomes a thin *device* with a full *agent runtime*, and the model behind it is yours to choose. For the self-hosting crowd that has spent two years building local inference stacks, this is the missing endpoint: an agent that runs on the device but can talk to *your* models, *your* MCP servers, *your* skills.

The privacy framing is the same logic homelab folks already live by: your data stays on your phone (no vendor server), and you control the API key.

### The two modes

By default Mika runs in **Ask mode**: it checks with you only before spending money (placing orders, paying) and just does everything else. You can flip to **Autonomous mode**. That's a sane default — the agent acts, but the irreversible, wallet-affecting actions still route through you.

---

## What dsh-superagent Tells Us About Where This Is Heading

DeepSeek's `dsh-superagent` is a different beast and deserves its own honest caveat up front: it's a **research prototype**, explicitly *not* an official product, and the README says so in the first paragraph. It's a proactive coding agent for a single GitHub repository, packaged as a bundle for [DeepSeek Harness](https://www.deepseek.com/en/harness/). It listens to GitHub (and optionally Feishu), and when someone who's allowed asks for work, it opens a work item, works in its own session and directory, and replies in the original conversation — often with a pull request.

What makes it important isn't the GitHub glue. It's the **philosophy** it codifies, and it's worth quoting directly:

> **"Take as little human attention as possible, and give as much value as possible."**

> "An agent that can act for a whole team can also waste a whole team's attention, so it acts only when asked or when a rule the team wrote allows it, and speaks only when someone must act or can use a result."

That is the mature version of the agent dream. The last two years of agent hype assumed *more autonomy is better.* DeepSeek's design assumes the opposite — **autonomy is a liability you carefully meter.** The agent should act when authorized, stay silent when it can, and surface only what a human actually needs to see. There's an authorization model, a domain model, an execution model, and a web panel that shows "what needs a person."

That's the missing piece Mika *also* gets right with its Ask/Autonomous split: the future of agents isn't "do everything for me," it's "do the reversible things, ask before the irreversible ones, and tell me when you need me." The on-device wave and the autonomy-philosophy wave are the same wave.

---

## Why This Matters for Self-Hosters

I've spent two years writing about agents that live in your homelab. Mika flips the polarity and it's worth stating plainly: **the most personal device you own was the one agents couldn't reach.** Your phone is where your messages, your calendar, your photos, your 2FA, your shopping, your group chats all live — and until now, the only way to "automate" it was fragile per-app integrations or a cloud assistant that owns your data.

Mika changes the calculus:

1. **The agent runs where the data already is.** No exporting your chat history to a cloud, no giving a vendor your credentials. It operates the apps on the device.
2. **You keep the model.** Point it at your own key or your own homelab inference stack. The agent is open source; the brain is yours.
3. **Your homelab can drive your phone.** The CLI + Skill / MCP bridge means the agent on your server — the one that already watches your git repos and runs your cron — can hand a task to the agent in your pocket and get a result back.

That last point is the one that excites me most as someone who's built a whole self-hosted agent stack. The device I ignored for two years is now just another node I can route work to.

### The honest caveats

Because I'd rather you not install this and be surprised:

- **It's Android-only, Android 11+, and you sideload the APK.** No Play Store. iOS is out (Apple's lockdown makes this class of UI automation basically impossible). If you're an iPhone house, this is a spectator event for now.
- **It uses accessibility/UI-automation, not APIs.** That's the whole point, but it also means it's only as reliable as the screen state it reads. Complex flows, app updates, and weird layouts will occasionally flake. The README ships a growing list of apps with "built-in knowledge" (WeChat, WhatsApp, Telegram, Gmail, Google Calendar, Amazon, Uber, Reddit, Spotify, etc.), and anything else still works — just less reliably.
- **You're responsible for the model cost** if you use a hosted key — and you're responsible for *what you let it do* in Autonomous mode. Ask mode is the sane default for a reason.
- **dsh-superagent is research code.** Don't wire it into production. Read its philosophy docs, mine the ideas, adapt the patterns. It's a lighthouse, not a foundation.

---

## How to Actually Run Mika (Three Steps)

If you have an Android phone handy, this is genuinely quick:

1. **Install** — grab the APK from [Releases](https://github.com/wangzan101/Mika/releases/latest).
2. **Connect a model** — Settings › Model, pick a provider and paste an API key, or sign in with ChatGPT/xAI/OpenRouter. (For a homelab stack, point it at your Ollama/vLLM OpenAI-compatible endpoint.)
3. **Enable phone control** — follow the "Set up phone control" wizard in Settings and pair wireless debugging once. Skip this step if you only want chat, web, and files.

Then say something like *"Set alarms for 9:40 and 10:00 tomorrow morning"* or *"Check the weather at 8 every morning and tell me only if it will rain."* The README even ships an agent-on-your-computer path: it can set Mika up *for you* over USB via a documented install flow.

---

## The Bottom Line

The on-device agent gap — the one devhandbook.io has never covered, and the one I quietly assumed would stay open for years — closed in three weeks.

**Mika** (~9,500★) proves an agent can live on your phone, drive real apps through the screen, stay out of your way, and keep your data local while talking to *your* models. **dsh-superagent** (~24,000★) proves the community is converging on the *right* autonomy model — act when asked, speak when needed, meter the rest. Put them together and you get the real headline: **agents are leaving the server rack and landing in the pocket, and they're finally learning some manners on the way down.**

For the self-hosters reading this: the device you've ignored is now a node you can route to. Your homelab just got a phone number. I'm installing it this week and I'll report back on how it plays with an Ollama-backed local stack — because that's the experiment that actually tells us whether on-device agents are a gimmick or the next surface in your stack.

---

**Related posts:**
- [Agent Skills (SKILL.md): The Missing Bridge in Your AI-Coding Cluster](/blog/2026-11-21-agent-skills-skill-md-guide/) — The reusable-procedure layer your agents need
- [Local LLMs on a Mac mini: A Practical Guide](/blog/local-llms-mac-mini-practical-guide/) — The homelab inference stack Mika can talk to
- [AI Agent Sandboxes: Isolation Patterns for the Homelab](/blog/ai-agent-sandboxes-homelab/) — Why you sandbox an agent before you let it tap buttons

*Star counts checked against the GitHub API as of November 22, 2026. Both repos are moving fast — the numbers will be stale within days. Found another on-device agent worth covering? [Open an issue](https://github.com/Bryanmoon19/devhandbook.io/issues) or find me on [GitHub](https://github.com/bryanmoon19).*
