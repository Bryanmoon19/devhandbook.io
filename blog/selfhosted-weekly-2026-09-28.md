---
layout: post.njk
title: "Self-Hosted This Week: Digital Sovereignty Goes Mainstream — September 21–28, 2026"
date: 2026-09-28
description: "F-Droid ships its biggest update in a decade, the Dutch government goes all-in on NixOS, Immich gets a serious fork, and self-hosted AI keeps finding new niches. This week's roundup."
tags: ["selfhosted", "weekly", "homelab", "roundup", "f-droid", "nixos", "immich", "federation", "ai"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-09-28"
---

This week the self-hosting story stopped being a hobbyist niche and started showing up in headlines normally reserved for enterprise IT. A government betting on open-source infrastructure, a major app store hitting a milestone release, and a media server fork that proves the ecosystem's health — it all points one direction: **owning your stack is no longer a fringe position.**

Here's what caught my eye from September 21–28, 2026.

---

## 1. The Dutch Government Is Building a Microsoft Alternative on NixOS

**What it is:** [DAWO](https://www.dawo.community/en/) ("Digitally Autonomous Workplace") is an open community of government, industry, and civil society building a digitally autonomous workplace for the Dutch government — and it's built on NixOS.

**Why it matters:** This is the single most important signal in the self-hosting space this week, and it landed on the front page of Hacker News with over 1,000 points. The Netherlands isn't just complaining about vendor lock-in; they're building a replacement out of "replaceable building blocks" — separate, inspectable components for the operating system, AI, identity, and collaboration. When a national government treats infrastructure the way homelabbers treat their Proxmox nodes, it validates the entire philosophy. Reproducible builds, declarative config, verifiable systems — the same tools you run in your basement are now being vetted for public administration.

**The takeaway:** NixOS's declarative, reproducible model just got a massive institutional endorsement. If you've been curious about Nix, there's never been a better argument to try it.

[**DAWO →**](https://www.dawo.community/en/)

---

## 2. F-Droid 2.0 Ships Its Biggest Update in a Decade

**What it is:** [F-Droid](https://f-droid.org/) is the open-source Android app store — the self-hosted mindset applied to your phone, where every app is free and auditable rather than tracked and telemetry-laden.

**Why it matters:** F-Droid 2.0 landed September 24, billed as "the largest app update in 10 years" — a complete redesign with a modern interface, better discovery, improved search, and a smoother experience. It comes at a critical moment: the project is openly warning that Google is changing how apps get installed on Android, and it's asking the community to fight back. F-Droid has always been the canary in the coal mine for mobile freedom, and this release is both a usability leap forward and a shot across the bow of the walled garden.

**The takeaway:** If you've bounced off F-Droid's dated UI before, 2.0 is worth a second look — the polish finally matches the principles.

[**F-Droid 2.0 announcement →**](https://f-droid.org/2026/09/24/f-droid-2.0-a-new-chapter-for-android-freedom.html)

---

## 3. Noodle Gallery: A Fork of Immich That Shows the Ecosystem's Health

**What it is:** [Noodle Gallery](https://digitalescapetools.com/tools/noodlegallery.html) is a self-hosted photo and video manager forked from Immich, trending on Hacker News this week.

**Why it matters:** Forks get a bad rap, but they're actually the strongest signal a project can send. Immich's success — and its permissive enough structure that someone can fork it and push in a different direction — is proof the self-hosted photo space has matured beyond a single project. When a tool is good enough that people want to build variants of it, you know it's won the category. Noodle Gallery is early, but it's worth watching as an indicator of where Immich's rapid iteration leaves room for alternative takes.

**The takeaway:** Immich remains the default, but competition in the self-hosted photo space is now a real thing — and that's good for everyone's photo library.

---

## 4. Conversations Breaks Up With Google Play and Goes Free

**What it is:** [Conversations](https://gultsch.de/posts/breaking-up-with-google-play/) is the federated XMPP instant-messaging client for Android, maintained by Daniel Gultsch since 2014.

**Why it matters:** Gultsch published a candid retrospective this week explaining why he's making Conversations free — twelve and a half years after starting it, the "sell the compiled binary, give away the source" model no longer makes sense when Google Play's grip makes it harder to reach people who value the alternative. It's a small post with big implications for federated messaging: XMPP's flagship client choosing reach over revenue is a bet that the fediverse's messaging side can actually grow. For self-hosters running their own XMPP server, a free, actively-maintained flagship client removes one more barrier for friends and family.

**The takeaway:** If you've been hosting Prosody or ejabberd and struggling to get people on board, the "it costs money" objection just disappeared.

[**Read the post →**](https://gultsch.de/posts/breaking-up-with-google-play/)

---

## 5. PipePipe: A NewPipe Fork That Adds SponsorBlock

**What it is:** [PipePipe](https://github.com/InfinityLoop1308/PipePipe) is a hard fork of NewPipe — the open-source YouTube frontend — that integrates SponsorBlock to skip sponsored segments, with 6,600+ stars and active development this week.

**Why it matters:** NewPipe already let you browse YouTube without the app, the ads, or the account. PipePipe layers SponsorBlock on top, which is the missing piece for a lot of people — skipping baked-in sponsor reads is arguably as valuable as skipping the ads themselves. The project's rapid ascent (it's pushing commits daily) shows how much demand there is for a YouTube experience where *you* control what you watch. It's also a reminder that the entire "alternative frontend" movement — Invidious, NewPipe, PipePipe, and friends — is a form of self-hosting, just for the biggest streaming platform on earth.

**The takeaway:** If NewPipe's lack of SponsorBlock was your dealbreaker, this fork closes the gap.

[**GitHub →**](https://github.com/InfinityLoop1308/PipePipe)

---

## 6. Paperclip: Building a Self-Hosted AI IT Department

**What it is:** [Paperclip](https://github.com/theNetworkChuck/paperclip-guide) is a framework for standing up a personal AI "IT department" — an agent stack you run yourself — popularized this week through NetworkChuck's guide and a 100-star companion repo.

**Why it matters:** The self-hosted AI story has moved from "run a chatbot locally" to "run an agent workforce locally." Paperclip frames it as spinning up your own AI IT department — agents that handle the repetitive, scriptable, on-call-adjacent work of keeping a homelab alive. The guide is notable because it's aimed squarely at the NetworkChuck audience: people who want the power of an agentic setup without assembling a dozen pieces by hand. Whether you adopt it or not, it's a clear sign of where the self-hosted AI conversation is heading — from models to *teams of models*.

**The takeaway:** If you've been running Ollama for chat, the next step is orchestrating agents that actually do things on your server. Paperclip is one of the more approachable on-ramps.

[**Companion guide →**](https://github.com/theNetworkChuck/paperclip-guide)

---

## 7. Ollaya: Run Decision Models Locally, on Your Own Hardware

**What it is:** [Ollaya](https://ollaya.dev/) is a self-described "Ollama for Jev-style decision models" — a local, open-source tool for running structured decision models that return calibrated answers (with probabilities) to typed questions about text or JSON.

**Why it matters:** We've spent a year running generative LLMs locally. Ollaya points at the quieter frontier: *decision* models — smaller, faster, purpose-built tools that answer "is this refund request legit?" or "is this email urgent?" with a confidence score, in milliseconds, without a GPU. It's a different shape of local AI that fits the self-hosted ethos perfectly: private, on your own hardware, no cloud dependency. At 700+ stars in its early days and explicitly positioned as independent from Ollama, it's a signal that the local AI ecosystem is branching into specialized niches rather than one big model to rule them all.

**The takeaway:** Not every local-AI job needs a 70B model. Small, calibrated decision models might be the more practical tool for a lot of automation.

[**Ollaya →**](https://ollaya.dev/)

---

## Honorable Mentions

- **awesome-selfhosted** quietly crossed **322K stars** on GitHub — the canonical list keeps growing, and its mere existence is a census of how big this space has become.
- **Relay** (Show HN) is a self-hosted LLM gateway with smart routing and request pacing — another entry in the increasingly crowded "manage your local models" category.
- **Unsloth** (76K stars) keeps pushing its local UI for running and training LLMs, now supporting GGUF, MLX, and the latest Qwen/MiniMax models on consumer hardware.
- **HomelabFest 2027** was announced for St. Louis in September 2027 — the in-person homelab community keeps growing too.

---

## Closing Thought

The through-line this week is impossible to miss: **self-hosting has stopped being a protest and started being a plan.** A government builds its workplace on NixOS. A phone's app store ships a mature release while warning about platform lock-in. A messaging client goes free to grow the fediverse. These aren't hobbyists tinkering in a basement anymore — they're institutions and maintainers making long-term bets on the same values you've been running on your own hardware for years.

The tools got better. The arguments got stronger. And somewhere between a Dutch government document and your own docker-compose file, "why self-host?" quietly became "why wouldn't you?"

What's landing in your homelab this week? Drop a comment if something caught your eye.

---

_This is a weekly series covering trending self-hosted projects, homelab tools, and open-source infrastructure. Subscribe via RSS or follow devhandbook.io for more._
