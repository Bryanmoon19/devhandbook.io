---
layout: post.njk
title: "Self-Hosted This Week: Monitoring Wars & AI Gateways — August 18-24, 2026"
date: 2026-08-24
description: "Beszel hits 24k stars, Glance dominates dashboards, Kroma challenges Plex with direct-play HEVC, and the self-hosted AI gateway space heats up. Plus: why Slovakia's speed camera backdoor matters for your homelab."
tags: ["selfhosted", "weekly", "homelab", "roundup", "monitoring", "ai", "media-server", "security"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-08-24"
---

Another week, another wave of self-hosted projects hitting maturity. This week's theme: **infrastructure wars**. Monitoring tools are battling for your dashboard real estate, media servers are getting leaner, and everyone's building AI gateways. Let's dive in.

---

## 1. Beszel Surges Past 24k Stars — The Lightweight Monitoring Winner?

**What it is:** [Beszel](https://github.com/henrygd/beszel) is a lightweight server monitoring hub with historical data, Docker stats, and alerts. Think of it as a self-hosted Datadog that doesn't need a PhD to configure.

**Why it matters:** At 24.5k stars and climbing, Beszel is eating the lunch of heavier alternatives. The appeal is simple: it works out of the box, uses minimal resources, and doesn't require you to spin up a separate database just to track CPU usage. For homelabbers running on Proxmox LXCs or Raspberry Pis, every megabyte counts.

**The verdict:** If you're still running a complex monitoring stack and just want to know "is my server alive and how much RAM is Docker using," Beszel is worth a look.

---

## 2. Glance Hits 36k Stars — The Dashboard King Consolidates

**What it is:** [Glance](https://github.com/glanceapp/glance) is a self-hosted dashboard that aggregates all your feeds, widgets, and services into one place.

**Why it matters:** Glance isn't new, but hitting 36k stars this week shows the consolidation trend in self-hosted dashboards. While Dashy (26k stars) added more features, Glance doubled down on speed and simplicity. The community is voting with their stars: people want dashboards that load fast and stay out of the way.

**The verdict:** Dashboard fatigue is real. If you've got three different homepages fighting for your browser's start page, Glance might be the one to keep.

---

## 3. Kroma: A Rust-Based Plex Challenger with Direct-Play HEVC

**What it is:** [Kroma](https://github.com/maxscharwath/kroma) is a new self-hosted media streaming server written in Rust, focused on direct-play HEVC streaming with native Samsung Tizen and LG webOS TV clients.

**Why it matters:** Plex and Jellyfin are great, but they're also massive. Kroma is betting that a lean, purpose-built server can outperform them for specific use cases. The HEVC-first approach is smart — it's the most efficient codec for self-hosters with limited bandwidth, and native TV client support means no more transcoding headaches.

**The verdict:** Too early to call it a Plex killer, but if you're running a NAS and mostly watch on Samsung/LG TVs, Kroma's direct-play focus could save you CPU cycles and bandwidth. Worth watching.

---

## 4. The Self-Hosted AI Gateway Gold Rush

**What it is:** Three projects launched this week alone: [SRouter](https://github.com/seaavey/SRouter), [Marbor](https://github.com/Anirudhx7/marbor), and [QwenPaw](https://github.com/agentscope-ai/QwenPaw) all position themselves as self-hosted AI gateways — unified `/v1` APIs that route requests to Ollama, vLLM, llama.cpp, or cloud providers.

**Why it matters:** Everyone's running local LLMs now, but managing multiple models across different runtimes is a pain. SRouter offers a single Go binary. Marbor adds warm-state GPU routing. QwenPaw focuses on easy deployment. This is the natural evolution of the self-hosted AI stack: first we ran models, now we need infrastructure to manage them.

**The verdict:** If you're running more than two local models or mixing local + cloud, an AI gateway is becoming table stakes. SRouter's simplicity makes it the easiest starting point.

---

## 5. Dawarich Crosses 10k Stars — Google Timeline Alternative Matures

**What it is:** [Dawarich](https://github.com/Freika/dawarich) is a self-hosted Google Timeline alternative that imports your Location History and provides maps, statistics, and export tools.

**Why it matters:** At 10k stars, Dawarich is proving that privacy-focused alternatives to Google services have real demand. The project hit a milestone this week with improved map rendering and faster imports. For anyone who exported their Google Location History before the shutdown deadline, this is where it lives now.

**The verdict:** If you've got a Google Location History JSON file sitting in a folder somewhere, Dawarich gives it a second life.

---

## 6. Security Spotlight: Slovakia's Speed Camera Backdoor

**What it is:** Slovakian authorities discovered a Russian backdoor in traffic speed cameras, reported on [Hacker News](https://news.ycombinator.com/item?id=49409200) this week.

**Why it matters:** This isn't just a government IT problem. The attack vector? Unpatched IoT devices with default credentials and no network segmentation. That's your homelab too. If a speed camera can be remotely compromised, so can your exposed Home Assistant instance or unpatched Docker container.

**The verdict:** Weekend homework: audit your exposed ports, update your containers, and make sure your IoT VLAN can't reach your main network.

---

## 7. Documenso Hits 14.7k Stars — E-Signature Without the Subscription

**What it is:** [Documenso](https://github.com/documenso/documenso) is the open-source DocuSign alternative, and it crossed 14k stars this week.

**Why it matters:** E-signature tools are one of those "I need it once a month but won't pay $15/month" use cases. Documenso lets you self-host the entire workflow — templates, signing, audit trails — without the subscription fatigue.

**The verdict:** If you've ever paid for DocuSign just to sign one document, self-hosting Documenso pays for itself in a year.

---

## Closing Thoughts

This week's trends tell a clear story: **self-hosted infrastructure is maturing**. We're past the "look, I can run a container" phase and into the "which tool actually solves my problem without becoming the problem" phase.

Monitoring tools are getting leaner. Media servers are specializing. AI infrastructure is consolidating. That's the sign of a healthy ecosystem — not endless novelty, but steady refinement.

What's landing in your homelab this week?

---

**Links:**

- [Beszel](https://github.com/henrygd/beszel)
- [Glance](https://github.com/glanceapp/glance)
- [Kroma](https://github.com/maxscharwath/kroma)
- [SRouter](https://github.com/seaavey/SRouter)
- [Dawarich](https://github.com/Freika/dawarich)
- [Documenso](https://github.com/documenso/documenso)
- [Slovakia Speed Camera Backdoor (HN)](https://news.ycombinator.com/item?id=49409200)
