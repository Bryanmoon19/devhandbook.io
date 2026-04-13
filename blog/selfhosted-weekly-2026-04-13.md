---
layout: post.njk
title: "Self-Hosted This Week: Forks, Backups, and 23-Year-Old Bugs — April 6–13, 2026"
date: 2026-04-13
description: "Immich plots encrypted backups, the open-source office suite world descends into fork wars, Tailscale gets more generous, Claude Code finds a vintage Linux kernel bug, and a hardened *arr stack shows us how Docker Compose should actually look."
tags: ["selfhosted", "weekly", "homelab", "roundup"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/selfhosted-weekly-2026-04-13"
---

This week had a little bit of everything: corporate drama between open-source foundations, a beloved media tool shutting down, AI uncovering ancient vulnerabilities, and some genuinely good news for hobbyists running Tailscale and Pushover. Oh, and someone finally built an *arr stack that doesn't make security engineers wince.

Let's get into it.

---

## 1. Immich Is Building a Managed Backup Service (With Real E2E Encryption)

**What it is:** The Immich team announced they're working on FUTO Backups — a managed, end-to-end encrypted backup service for Immich libraries. The pitch is simple: encrypted copies of your photos and videos sit in a remote datacenter, but only you hold the keys. They're running a short community survey to gauge storage sizes, hardware, and pricing tolerance.

**Why it matters:** Photo backups are the achilles heel of most self-hosted setups. RAID isn't a backup, and rotating USB drives is a plan that fails quietly. A purpose-built, zero-knowledge backup layer built directly into Immich could solve the "what if my house burns down" problem without forcing users back into Google Photos. If the pricing is reasonable, this could become the default offsite safety net for the self-hosted photo crowd.

**→ [Take the survey](https://futo-backups-survey.immich.app/)**

---

## 2. The Document Wars: Euro-Office vs. OnlyOffice vs. LibreOffice

**What it is:** The open-source office suite ecosystem is eating itself. A few weeks ago, Nextcloud, IONOS, and Proton launched [Euro-Office](https://github.com/Euro-Office) — a fork of OnlyOffice aimed at European digital sovereignty. OnlyOffice responded by suspending its 8-year partnership with Nextcloud and accusing the fork of licensing violations. This week, the drama doubled: The Document Foundation (LibreOffice) expelled Collabora — the company behind most of LibreOffice's web-based development — from its membership. Collabora is now planning its own lighter fork.

**Why it matters:** Self-hosters rely heavily on Nextcloud + OnlyOffice/Collabora Online for document editing. If these projects fragment further, expect compatibility headaches, slower security patches, and a whole lot of confusion about which fork to run. For now, nothing is breaking overnight — but if you're running a Nextcloud office suite setup, this is worth monitoring closely. The real winner here might be Microsoft and Google, watching the open-source world fight itself instead of them.

**→ [The Register on Euro-Office](https://www.theregister.com/2026/04/02/eurooffice_forks_onlyoffice/)**
**→ [Collabora's response](https://www.collaboraonline.com/blog/tdf-ejects-its-core-developers/)**

---

## 3. ErsatzTV Is Archived — But a Reboot May Be Coming

**What it is:** ErsatzTV, the clever tool that turned your personal media libraries into live, schedule-driven TV channels, was officially archived on April 10. The maintainer stepped away in February, citing scope creep and burnout. The good news: there's already a "next" repository with early work toward a streamlined reboot.

**Why it matters:** ErsatzTV filled a genuinely unique niche — there isn't a mature alternative for creating curated live channels from your own media. If you depended on it, your existing setup should keep working, but don't expect updates. The potential reboot is promising, but it's early days. For now, keep an eye on the project's GitHub org and maybe send the maintainer some encouragement. Burnout is real, and this is exactly what it looks like.

**→ [ErsatzTV legacy archive](https://github.com/ErsatzTV/ErsatzTV-legacy)**

---

## 4. Claude Code Found a 23-Year-Old Linux Kernel Vulnerability

**What it is:** Nicholas Carlini, a research scientist at Anthropic, revealed that he used Claude Code to find multiple remotely exploitable heap buffer overflows in the Linux kernel — including one in the NFS driver that went undiscovered for 23 years. The bug allows an attacker to overwrite kernel memory using a malformed NFS lock request. He essentially pointed Claude at the kernel source, asked it to play CTF, and iterated through every file.

**Why it matters:** This isn't a novelty stunt — it's a signal that AI-assisted security research is getting *very* real. If you're running NFS on a Linux server (which includes a lot of homelab NAS setups), patch your kernel. More broadly, this raises an uncomfortable question: if an AI can find 23-year-old kernel bugs in a weekend scan, how many more are lurking in codebases that *don't* get that kind of attention? Keep your systems updated. The bar for finding exploits just got lower.

**→ [Michael Lynch's writeup](https://mtlynch.io/claude-code-found-linux-vulnerability/)**

---

## 5. Tailscale Expands Its Free Plan to 6 Users

**What it is:** Tailscale updated its pricing this week, bumping the free personal plan from 3 users to 6 users per tailnet. The change is live now and applies to existing accounts.

**Why it matters:** Tailscale is the de facto standard for secure remote access in self-hosted setups. The jump from 3 to 6 users is meaningful — it covers most small families or friend groups without forcing a paid upgrade. It's also just nice to see a company make its free tier *more* generous instead of less. If you've been juggling shared accounts or leaving family members off your tailnet, now's a good time to fix that.

**→ [Tailscale pricing blog post](https://tailscale.com/blog/pricing-v4)**

---

## 6. A Hardened *arr Stack That Actually Takes Security Seriously

**What it is:** Developer Przemek Mroczek open-sourced [`uncompressed`](https://github.com/Lackoftactics/uncompressed) — a Docker Compose-based *arr stack (Jellyfin, Sonarr, Radarr, Prowlarr, qBittorrent, etc.) built with network isolation, namespace-based VPN routing, and zero internet-facing ports. Instead of the usual "flat Docker network + iptables kill switch" approach, qBittorrent runs inside the VPN container's network namespace with no independent interface. If the VPN drops, there is literally no network path — not just a blocked one.

**Why it matters:** Most *arr setup guides on YouTube and Reddit copy-paste the same insecure patterns: everything on one bridge, ports blasted to 0.0.0.0, fake kill switches, no health checks. This stack is a practical blueprint for doing it right. If you're running a media server pipeline and care even a little about security or architecture, read the whole article and borrow the patterns.

**→ [Read the deep dive](https://mroczek.dev/articles/hardened-arr-stack/)**

---

## 7. Pushover Moves to App Pools for API Limits

**What it is:** Pushover, the popular notification service used in countless homelab automations, updated its pricing model. Starting May 1, API message limits will be pooled per-account rather than locked to individual applications. You can increase quota via application pools instead of buying upgrades for each app token separately.

**Why it matters:** If you're like most self-hosters, you have a half-dozen services all shouting through Pushover — Home Assistant, *arr apps, Uptime Kuma, maybe a custom script or two. The old per-app limit was annoying to manage and easy to accidentally blow through on a noisy service. Pooling simplifies the math and makes Pushover more reasonable for multi-service homelabs.

**→ [Pushover app limits announcement](https://blog.pushover.net/posts/2026/4/app-limits)**

---

## Closing Thought

This week reminded me that self-hosting isn't just about running cool software — it's about paying attention to the seams. The office suite world is fracturing because of governance failures, not technical ones. ErsatzTV went dark because a single maintainer hit a wall. And a 23-year-old kernel bug was hiding in plain sight until an AI happened to look.

The best self-hosters I know aren't the ones with the most services. They're the ones who keep an eye on the news, patch promptly, and know when to simplify. This is a good week to do all three.

---

*Self-Hosted This Week is a weekly roundup published every Monday. Got a tip or project worth featuring? The best finds come from the community.*
