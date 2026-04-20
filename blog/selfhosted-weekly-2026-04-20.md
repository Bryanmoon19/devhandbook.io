---
layout: post.njk
title: "Self-Hosted This Week: AI Agents, Memory Databases, and the Self-Hosted Netflix — April 13–20, 2026"
date: 2026-04-20
description: "A memory database that forgets on purpose, a self-hosted Netflix streaming at 60 Mbps, AI agent security frameworks, a new note-taking paradigm, and Docker Headscale make this a week of genuine innovation in the self-hosted world."
tags: ["selfhosted", "weekly", "homelab", "roundup"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-04-20"
---

This week felt different. Instead of the usual CVE panic and corporate drama, we got genuinely interesting new projects — tools that rethink how software should work rather than just reimplementing what already exists. A database that forgets. A streaming stack that beats Netflix on quality. Security frameworks built specifically for AI agents. And a few quality-of-life improvements for the infrastructure we already run.

Let's dig in.

---

## 1. YantrikDB — A Memory Database That Forgets, Consolidates, and Detects Contradictions

**What it is:** [YantrikDB](https://github.com/yantrikos/yantrikdb-server) is a new open-source database designed for AI agent memory. Instead of storing everything forever like a traditional database, it actively forgets irrelevant information, consolidates related memories, and — most interestingly — flags when an agent's memory contains contradictions. It surfaced on Hacker News this week with 47 points and genuine technical discussion.

**Why it matters:** Every self-hoster running local LLMs (Ollama, LM Studio, etc.) hits the same wall: context windows are tiny, and agents don't remember anything between sessions. Vector databases like Chroma or Weaviate store embeddings, but they don't *think* about what they store. YantrikDB adds a layer of cognitive hygiene — forgetting stale data, merging related concepts, and catching when the agent has learned two contradictory things. If you're building personal AI assistants or automation agents on your own hardware, this is the kind of infrastructure that makes them actually useful long-term.

**→ [YantrikDB on GitHub](https://github.com/yantrikos/yantrikdb-server)**

---

## 2. Uncompressed — Self-Hosted Streaming at 60 Mbps (Because 15 Isn't Enough)

**What it is:** [Uncompressed](https://uncompressed.media) is a self-hosted media streaming solution that delivers video at 60 Mbps instead of the ~15 Mbps cap you'll hit on Netflix, Disney+, or pretty much any commercial streaming service. It surfaced on Hacker News with 11 points this week, and the technical approach is genuinely clever — not just "self-host Jellyfin," but a stack optimized for bitrate quality that commercial services can't match because of their bandwidth costs.

**Why it matters:** If you've ever watched a dark scene in a movie and seen it turn into a blocky mess, you've hit the bitrate wall. Commercial streaming services compress aggressively to serve millions of users cheaply. A self-hosted solution doesn't have that constraint — your server, your bandwidth, your quality. Uncompressed is built for people who have the infrastructure (decent upload speed, local storage) and care about fidelity. It's a niche within a niche, but it's exactly the kind of project that reminds you why self-hosting matters: not just privacy or control, but *better quality than the commercial alternative*.

**→ [Uncompressed.media](https://uncompressed.media)**

---

## 3. AgentArmor — An 8-Layer Security Framework for AI Agents

**What it is:** [AgentArmor](https://github.com/Agastya910/agentarmor) is an open-source security framework that wraps AI agents in eight defensive layers: input sanitization, prompt injection detection, output filtering, sandboxed execution, audit logging, rate limiting, secret rotation, and behavioral anomaly detection. It got 10 points on Hacker News this week and represents one of the first systematic attempts to secure autonomous AI agents.

**Why it matters:** Self-hosters are increasingly running AI agents that can actually *do* things — query APIs, modify files, send messages, trigger automations. That's powerful and terrifying. Most local LLM setups have zero security model beyond "it's on my LAN." AgentArmor gives you a framework to reason about agent security systematically. If you're running anything agentic with tool access (OpenClaw agents, custom automation scripts, MCP-connected tools), this deserves a look. The project is early but the architecture is sound.

**→ [AgentArmor on GitHub](https://github.com/Agastya910/agentarmor)**

---

## 4. Docker Headscale — Self-Hosted Tailscale Control Server, Now Actually Easy

**What it is:** A [Docker setup for Headscale](https://github.com/hwdsl2/docker-headscale) surfaced on Hacker News this week, packaging the self-hosted Tailscale control server into a properly configured, one-command Docker deployment. Headscale lets you run your own Tailscale coordination server instead of relying on Tailscale's cloud infrastructure — full mesh VPN with your own control plane.

**Why it matters:** Tailscale is already the default answer for "how do I access my homelab remotely" in most self-hosted communities. But the control plane lives on Tailscale's servers, which is fine for most people but not ideal if you're fully committed to self-sovereignty. Headscale has existed for a while, but setup was manual and finicky. A clean Docker compose with proper configuration makes it accessible to anyone already comfortable with Docker. If you're running a fully air-gapped or privacy-maximal setup, this is the missing piece.

**→ [Docker Headscale on GitHub](https://github.com/hwdsl2/docker-headscale)**

---

## 5. Joonote — Notes on Your Lock Screen and Notification Panel

**What it is:** [Joonote](https://joonote.com/) is a note-taking app that lives on your phone's lock screen and notification panel — no unlock, no app launch, just pull down and write. It got 54 points on Hacker News and sparked a real discussion about friction in productivity tools.

**Why it matters:** Self-hosters love obsessing over the server side, but the client side matters just as much. The best self-hosted note/wiki/second-brain setup in the world is useless if capturing an idea takes six taps and three loading screens. Joonote's approach — zero-friction capture at the OS level — is a pattern worth stealing. If you're running SilverBullet, Obsidian with Self-hosted LiveSync, or any other note system, the lesson is: optimize the capture path, not just the storage path.

**→ [Joonote](https://joonote.com/)**

---

## 6. Kodama — A Self-Hosted Autonomous Daemon for Claude Code and Codex

**What it is:** [Kodama](https://github.com/FratteFlorian/kodama) is a self-hosted daemon that manages persistent AI coding agents (Claude Code, Codex) with scheduling, context persistence, and tool orchestration. It got modest attention on Hacker News but solves a real problem: AI coding sessions that lose all context when you close the terminal.

**Why it matters:** If you're using Claude Code or Codex for development work, you've felt the pain — start a session, make progress, close your laptop, and the next session starts from zero. Kodama keeps agents alive, manages their context windows, and schedules tasks. For self-hosters already running local AI infrastructure, this is a logical next step: not just chat-with-LLM, but *persistent agent infrastructure* that remembers what it was doing.

**→ [Kodama on GitHub](https://github.com/FratteFlorian/kodama)**

---

## 7. LaReview — A Local, Open-Source CodeRabbit Alternative

**What it is:** [LaReview](https://github.com/puemos/lareview) is an open-source alternative to CodeRabbit (the AI code review service) that runs entirely locally. It analyzes pull requests, suggests improvements, catches bugs, and explains changes — all without sending your code to a third-party API. It surfaced quietly on Hacker News with 3 points but deserves more attention.

**Why it matters:** Code review is one of the last workflows that still forces you to ship proprietary code to cloud AI services. LaReview keeps everything local — your code, your LLM (Ollama-compatible), your review history. For self-hosters running Gitea or GitLab, this fills a genuine gap. The project is early but the concept is exactly right: AI-assisted development without the privacy trade-off.

**→ [LaReview on GitHub](https://github.com/puemos/lareview)**

---

## Closing Thought

This week's theme was *infrastructure for the next phase of self-hosting*. We're past the "run a Plex server and call it a day" era. The interesting projects now are about AI agents that remember, security frameworks that protect them, streaming quality that beats commercial services, and capture tools that remove friction.

The self-hosted world is maturing. The question isn't "can I run this myself?" anymore — it's "can I run it *better* than the commercial alternative?" This week, the answer was yes more often than usual.

---

*Self-Hosted This Week is a weekly roundup published every Monday. Got a tip or project worth featuring? The best finds come from the community.*
