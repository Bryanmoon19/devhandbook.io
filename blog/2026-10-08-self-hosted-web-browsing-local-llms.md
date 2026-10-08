---
layout: post.njk
title: "Give Your AI Agent Eyes: Self-Hosted Web Browsing & Search for Local LLMs"
date: 2026-10-08
description: "Your local LLM can reason, but it's blind — it can't look anything up. Here's how to give an Ollama model real eyes: Agent-Reach, NVIDIA OpenShell, browser-use, and Playwright MCP, mapped to which local stacks can browse safely, with the Mac mini setup to bolt web access onto your homelab."
tags: ["local-llm", "ollama", "ai-agents", "agent-reach", "openshell", "nvidia", "browser-use", "playwright", "mcp", "web-scraping", "self-hosted", "homelab", "mac-mini"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-08-self-hosted-web-browsing-local-llms/"
affiliate: true
cta: true
---

There's a moment every self-hoster hits, usually about a week after they get Ollama running, when they realize their local model has a brain but no body.

You've got a capable LLM sitting on your own hardware. It can reason, summarize, write code, hold a conversation. But the second you ask it a question that requires *looking something up* — "what's the latest release of X?", "find me the docs for Y", "compare these three products for me" — it stalls. It can't browse. It can't search. It has no eyes.

The cloud models don't have this problem. ChatGPT, Claude, Gemini, Perplexity — they all ship with a built-in web layer that reaches out, fetches a page, reads it, and feeds it back into the model. That's the single biggest capability gap between "AI in the cloud" and "AI in my basement," and it's the reason so many people quietly keep a cloud subscription for the *one* thing their homelab can't do.

This week that gap started closing, and it's worth paying attention because it's the exact shape of the AI-agent wave that's coming. A cluster of tools — **Agent-Reach**, **NVIDIA OpenShell**, **browser-use**, and **Playwright MCP** — have each solved a different slice of the "give your local model a browser" problem. Together they form the browser layer for local LLM stacks.

This post maps that layer. What each tool is, what it's actually good at, which local stacks it fits, and how to bolt web access onto a Mac mini running Ollama — safely.

*(I'm deliberately not covering sandboxing here. The isolation model for these agents — how you keep a browsing agent from wrecking your machine — is its own deep topic, and I've written about it separately. This post is about the access layer: getting eyes onto your model in the first place.)*

## The Blind Spot, Defined

Let me be precise about what "your model can't browse" actually means, because it's easy to hand-wave.

A local LLM is a function from text to text. It has a knowledge cutoff. It has no network access, no memory beyond its context window, and no way to act on the world. When you ask it something that isn't in its weights, it does the thing you've probably watched it do a hundred times: it *guesses*, confidently, in a plausible voice, with details it just made up.

Web access fixes this in a specific way. Instead of generating an answer from memory, the model gets a loop:

1. A question needs fresh information.
2. The model decides it should look something up.
3. A tool fetches a web page or runs a search.
4. The text of that page gets injected into the context.
5. The model reads it and answers from *that*, not from its weights.

That's it. That's the whole trick — retrieval-augmented generation, the thing everyone calls "RAG," except the retrieval source is the live web instead of a vector database. And the entire category of tools in this post is just different ways to build step 3, with different tradeoffs on safety, control, and how much of a "browser" you actually want.

The reason this matters now and not a year ago is that step 2 — *the model deciding to look something up and knowing how to use the tool* — is the part that required a frontier model. Small models couldn't reliably drive a browser. That changed. Function-calling and tool-use are now table stakes for even modest local models, and the agent wave is pushing every framework to make "call this tool, read the result" as natural as "generate text."

## The Four Ways to Give a Model Eyes

There are really only four architectures for web access, and every tool in this space is one of them. Understanding the four shapes is more useful than memorizing a list of GitHub repos.

### 1. The Search-and-Read Layer (Agent-Reach)

**Agent-Reach** is the newest and, honestly, the most interesting entry — a self-hosted web search and browsing layer built specifically for AI agents. The pitch is right in the name: it's the *reach* your agent is missing.

What it does is collapse the whole "search, then fetch, then extract the useful text" pipeline into a single API. You point your agent at it, and it handles the parts that are genuinely hard to do well: running a web search across multiple engines, fetching the top results, stripping out the nav bars and cookie banners and JavaScript cruft, and returning clean, readable text that an LLM can actually digest.

The killer feature for local models is that it returns *text*, not a DOM tree. A 7B or 14B model doesn't want raw HTML — it wants paragraphs. Agent-Reach does the extraction so your model doesn't have to fight with `div` soup. And because it's self-hosted, your search queries and your browsing history stay on your machine instead of getting piped to a search vendor's API.

It's the tool I'd point a homelabber toward first, because it matches the shape of the problem: you don't need a full browser, you need *search plus readable results*. Most of what you ask an AI to look up is exactly that.

### 2. The Safe Runtime (NVIDIA OpenShell)

**NVIDIA OpenShell** is a different animal. It's a runtime for autonomous AI agents — the "safe and private" one, positioned as the open, self-hostable alternative to cloud agent platforms. NVIDIA is the name to notice here: they're investing hard in the "agents that do real work" story, and OpenShell is their bet that the runtime — the thing that *supervises* an agent — should be open and run on your own hardware.

For the browsing question specifically, OpenShell matters because it gives an agent a managed environment to act in. The browsing isn't just "fetch this URL" — it's an agent that can navigate, click, fill forms, and take multi-step actions, with OpenShell providing the supervision layer that checks each step. It's the difference between *reading* the web and *operating* the web, and it's aimed at the agent wave's deeper end: agents that don't just look things up but actually do tasks.

The tradeoff is weight. OpenShell is a real runtime with real infrastructure requirements — it's not a five-minute Docker pull. For a homelab, it's the "I'm serious about autonomous agents" option, not the "I want my Ollama model to answer a question" option.

### 3. The Scriptable Browser (browser-use)

**browser-use** is the tool that most people in the agent space will recognize, because it rode the "AI agents browse the web" wave to the top of GitHub's trending charts. It's a Python library that wraps a real browser (Chromium, via Playwright under the hood) and lets an LLM drive it.

The mental model is: you give the model a task in plain English — "find the cheapest flight from New York to London next Tuesday and tell me the airline" — and browser-use gives the model a live browser to click through the results with. It extracts the page state into a form the model can understand, lets the model decide the next action (click this, type that, scroll), executes it, and reads the new state. Loop until done.

It's the most "agentic" of the four, and the most powerful in the sense that it can do anything a human with a browser can do. The flip side is that it's also the most likely to do something you didn't intend — the "autonomous agent with a real browser" safety question, which is exactly the sandboxing topic I'm deliberately sidestepping here.

### 4. The Minimal Connector (Playwright MCP)

**Playwright MCP** is the smallest and most surgical option: an MCP server that exposes browser automation as a set of tools your model can call. It's the same Playwright engine that powers browser-use, but stripped down and packaged as a Model Context Protocol server instead of an agent framework.

This is the "bolt-on" option for people already running an MCP stack. If your setup is Claude Desktop, or Cursor, or an MCP client pointed at a local Ollama model, you add Playwright MCP as one more tool, and suddenly your model has `browser_navigate`, `browser_click`, `browser_snapshot`, and friends. No new framework, no new runtime — just one more tool in the toolbox, doing one job: driving a browser.

It's the right choice when you want browsing to be *a capability among many* rather than *the whole point*. And it pairs naturally with the MCP ecosystem I've written about here before — it slots right into the same server list as a bank connector or a filesystem tool.

## Mapping Stacks to Browsers

So which tool goes with which stack? Here's the map, because the useful question isn't "which is best" but "which fits what I'm already running."

**Ollama on a Mac mini (or any single box):** Start with **Agent-Reach**. It's the lowest-friction way to give a local model search-plus-readable-text, it's self-hosted so your queries stay home, and it doesn't demand a heavy browser or an agent runtime. Add **Playwright MCP** when you need actual navigation — form-filling, logging in, clicking through a flow — rather than just lookup.

**An existing MCP stack** (Claude Desktop, Cursor, an MCP client): **Playwright MCP** is the obvious fit. It's one more server, one more set of tools, and it respects the architecture you already have. You're not adopting a framework; you're adding a capability.

**A real agent framework** (you're building agents that do multi-step tasks, not just answer questions): **browser-use** if you want to stay lean and scriptable in Python, **OpenShell** if you want a supervised, managed runtime for agents that are going to roam.

**The frontier-agent home lab:** **OpenShell** is where the NVIDIA bet lives. If you're running a GPU box and building agents that operate the web autonomously, that's the runtime to watch — it's the one with a serious vendor throwing weight behind the "safe, private, open" story.

Here's the thing I keep coming back to: **there is no single best tool, because "browsing" isn't one capability.** It's a spectrum, from *search-and-read* (Agent-Reach) at one end to *operate-a-full-browser* (browser-use, OpenShell) at the other, with Playwright MCP in the middle. The skill is matching where you sit on that spectrum to the tool that lives there.

## Bolting Web Access Onto a Mac mini + Ollama

Let me make it concrete, because the Mac mini is exactly the machine this site's readers keep asking about. Here's the shortest path from "Ollama runs models" to "Ollama can browse."

**Step 0: Make sure Ollama's API is up.** If you can hit `http://localhost:11434` and get a model to respond, you're set. The browser layer bolts on in front of or beside this, not in place of it.

**Step 1: Spin up Agent-Reach for search-and-read.** It's a Docker container, and it sits as its own HTTP endpoint:

```bash
docker run -d --name agent-reach \
  -p 8010:8010 \
  --restart unless-stopped \
  agentreach/agent-reach:latest
```

Point your agent client at `http://localhost:8010`, and your model can now ask for a web search and get back clean, readable text. No cloud search API, no vendor seeing your queries — the search runs through your own box.

**Step 2: Add Playwright MCP for real navigation.** When lookup isn't enough and you need the model to *drive* a browser, add Playwright MCP to your MCP client config:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

Now your model has `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, and the rest of the automation toolkit, all locally.

**Step 3: Wire it together in the client.** Whatever you use to talk to Ollama — Open WebUI, a custom script, an MCP client — becomes the "brain" that decides when to call the browser tools. The tools are just HTTP endpoints or MCP servers on localhost; the model is the one choosing which to invoke.

The whole thing is maybe fifteen minutes of Docker and config, and the result is a local model that can finally answer the questions that used to force you back to a cloud subscription.

## The Honest Catch

I said at the top I wasn't going to cover sandboxing, and I'll hold that line, but I can't end without flagging the thing that every single one of these tools makes more urgent, not less.

**Giving a model eyes means giving it an input channel you don't fully control.** The web is full of text written for humans, and some of that text is adversarial. When your model browses, it's reading content that may contain instructions — the prompt-injection problem I've written about at length. A browsing agent is *by definition* ingesting untrusted text from the entire internet, and that's a real, structural risk that no amount of "but it's local" hand-waving makes disappear. Local keeps your data off someone's server; it does not make the web trustworthy.

The tools themselves know this — it's why OpenShell leads with "safe," why Agent-Reach strips pages down to text, why the browser tools all ship with some notion of a sandbox or allowlist. But the responsibility for the *final* safety decision sits with you, the operator, same as always.

That's the deal, and it's the same deal every self-hoster accepts when they open a port: you get capability, and you get the consequences of the capability. The good news is that for web access specifically, the consequences are now a lot more manageable than they were a year ago — because the tools are finally catching up to the ambition.

## The Bottom Line

Your local LLM has been blind for as long as you've been running it, and that single fact has been the quiet excuse for a cloud subscription you thought you'd given up. This week the blind spot started closing from four directions at once: **Agent-Reach** for self-hosted search-and-read, **NVIDIA OpenShell** for a safe agent runtime, **browser-use** for a scriptable browser, and **Playwright MCP** for the minimal bolt-on.

None of them is the whole answer, because "browsing" is a spectrum, not a feature. But together they cover that spectrum end to end, and for a Mac mini running Ollama, the path is short: Agent-Reach for lookup, Playwright MCP for navigation, and a client smart enough to decide between them.

The AI-agent wave is real, and it's coming whether or not you're on it. The difference between watching it and riding it is whether your model has eyes. Now it can.

---

*Want the rest of the stack? See my [local LLM hardware guide](/blog/local-llms-homelab-hardware-guide/) for matching models to Mac minis and N100s, the post on [running a 125B frontier model on consumer hardware](/blog/run-125b-frontier-model-on-consumer-hardware/), and my [MCP attack surface](/blog/2026-08-16-mcp-servers-attack-surface/) writeup for the security half of giving your agent eyes.*
