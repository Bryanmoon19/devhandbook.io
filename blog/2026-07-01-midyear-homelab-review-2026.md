---
layout: post.njk
title: "Mid-Year Homelab Review: What's Working, What's Not, and What's Next"
date: 2026-07-01
description: "Six months into 2026, I'm taking honest stock of my homelab. What's delivering value? What's collecting dust? And what am I actually paying for that I barely use? This is the real review I wish I'd read before building half of this stuff."
tags: ["homelab", "self-hosted", "review", "proxmox", "docker", "2026", "productivity", "cost-analysis"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-07-01-midyear-homelab-review-2026"
---

It's July 1st. We're halfway through 2026. And I just got my electricity bill.

That single envelope (well, PDF notification) prompted me to actually look at what I've built over the past six months and ask a question I should've been asking all along: **Is this thing actually worth it?**

Not "does it work?" — most of it works fine. But does it deliver enough value to justify the time I spent setting it up, the money I spend keeping it running, and the mental overhead of maintaining it?

Here's my honest mid-year review. No affiliate links, no sponsorships, just a guy who likes tinkering taking stock of his digital workshop.

---

## The Stack at a Glance

Before we dive in, here's what I'm actually running as of today:

| Service | Purpose | Host | Monthly Cost |
|---------|---------|------|-------------|
| Proxmox VE | Hypervisor | Dell OptiPlex (i5, 32GB RAM) | ~$8 electricity |
| Home Assistant | Smart home hub | Proxmox LXC | $0 |
| Plex | Media server | Proxmox LXC (VMID 1002) | $0 |
| TeslaMate | Tesla data logging | Proxmox LXC (VMID 1002) | $0 |
| Audiobookshelf | Audiobook server | Proxmox LXC | $0 |
| Navidrome + Soulseek | Music streaming | Proxmox LXC (VMID 1003) | $0 |
| Immich | Photo backup | Proxmox LXC | $0 |
| Uptime Kuma | Monitoring | Proxmox LXC | $0 |
| WireGuard + Pi-hole | VPN + DNS filtering | Proxmox LXC | $0 |
| Vaultwarden | Password manager | Proxmox LXC | $0 |
| Autobrr + *arr stack | Media automation | Proxmox LXC (VMID 1003) | $0 |
| OpenClaw (Moon) | AI assistant | Mac mini (192.168.1.165) | ~$3 electricity |
| GPU VM (LLMs) | Local AI inference | Proxmox VM (RTX 3060) | ~$15 electricity |
| Cloudflare Pages | Static hosting | Cloudflare | $0 |
| Various Workers | Automation, APIs | Cloudflare | $0 |

**Total estimated monthly cost: ~$26** (mostly electricity for the Proxmox host and GPU VM)

That doesn't sound like much, but let's be real — the *time* investment is where the real cost lives. I've probably spent 100+ hours on this stack in six months. At that rate, I'm "paying" myself about $0.26/hour for the privilege of maintaining my own infrastructure.

So what's actually worth it?

---

## 🟢 What's Working (Really Well)

### 1. Home Assistant — The Unsung Hero

I don't think about Home Assistant much, which is exactly why it's successful. It just runs. My lights turn on at sunset. The 3D printer enclosure fan kicks on when the temperature hits 35°C. The Tesla charger starts when electricity rates drop. My wife can control everything from her phone without asking me for help.

**The unexpected win:** I built a Plex invite system that ties into Home Assistant's MQTT broker. When someone accepts a Plex invite, a notification pops up on our living room TV. Small thing, but it makes the whole system feel connected.

**Verdict:** Keeper. This is the backbone I'd rebuild around if everything else broke.

### 2. Plex + *arr Stack — The Entertainment Engine

This is why most people get into homelabbing, and honestly? It delivers. I have a 210-gallon aquarium in my living room, and the ambient noise of a movie playing on the TV behind it is genuinely part of the vibe. My wife watches her shows. I catch up on anime. My brother streams when he visits.

The *arr stack (Sonarr, Radarr, Lidarr, Prowlarr) with autobrr feeding it releases from trackers? That's the automation dream. New episode airs → autobrr snatches it → Sonarr grabs it → Plex indexes it → I get a notification. I don't touch anything.

**The honest cost:** Yes, I pay for Real-Debrid. Yes, there's a moral gray area. I've written about this before — I'm not pretending it's pure open-source righteousness. It's a pragmatic solution that works.

**Verdict:** Keeper, but I'm watching the legal landscape. If things shift significantly, I have my DRM-free library (Audiobookshelf, Navidrome) as the escape hatch.

### 3. TeslaMate — Data Nerd Paradise

I didn't expect to love this as much as I do. Every drive, every charge, every preconditioning session — logged, graphed, queryable. I can see exactly how much my 2016 Model S has degraded over time. I can prove that the battery heater actually matters in Pennsylvania winters.

**The unexpected win:** My brother (who also has a Tesla) now asks me for battery health reports before road trips. I've become the family Tesla data guy.

**Verdict:** Keeper, but niche. If you don't own a Tesla, this is irrelevant.

### 4. Audiobookshelf — The Audible Escape Hatch

I wrote a whole guide about this (published today, actually), but the short version: I got tired of Audible's app breaking and not owning my purchases. Audiobookshelf fixed that. I buy DRM-free from Libro.fm, rip my own CDs, and download public domain classics from LibriVox.

**The unexpected win:** My wife, who was skeptical of "another self-hosted thing," now uses it daily. The mobile app is actually good. The offline sync works. The sleep timer is better than Audible's.

**Verdict:** Keeper. This is the model for what self-hosting should be: better than the commercial alternative, not just "free."

### 5. WireGuard + Pi-hole — The Privacy Foundation

DNS-level ad blocking on every device in my house. VPN access from anywhere. My phone automatically connects when I leave the house. My parents' Roku stops showing ads (mostly).

**The unexpected win:** When my ISP had a DNS outage last month, I didn't even notice. Everything just kept working through my Pi-hole.

**Verdict:** Keeper. This is table stakes for any homelab.

---

## 🟡 What's Working (But Barely)

### 6. Immich — The Photo Backup That Could

I want to love Immich. The interface is beautiful. The AI tagging is impressive. The mobile sync is fast. But here's the thing: I still pay for iCloud. My wife still uses Google Photos. Immich is my "backup of a backup," which means I'm maintaining two photo systems for redundancy I probably don't need.

**The problem:** The social features aren't there yet. I can't easily share an album with my family without creating accounts for everyone. The partner sharing works, but it's clunky compared to "text me that photo."

**Verdict:** Keeping for now, but watching closely. If Google Photos gets truly unbearable, this is my exit ramp.

### 7. Uptime Kuma — Monitoring for Things That Don't Break

I have beautiful dashboards showing that my services are up. They are almost always up. When they're down, I usually know before Uptime Kuma tells me because I'm actively tinkering with the thing that broke it.

**The problem:** It's monitoring I set up because "you should monitor things," not because I actually needed it. The one time it was genuinely useful was when my ISP went down while I was at work — I got the notification, texted my wife "internet's out, reset the router," and saved her 20 minutes of confusion.

**Verdict:** Keeping, but I've stopped adding new monitors. It's good enough.

### 8. Navidrome + Soulseek — The Music Stack

This works, but it's a two-system solution where I'd prefer one. Navidrome is great for streaming my owned music. Soulseek (via slskd) is great for finding obscure stuff. But they don't talk to each other. I can't search my Navidrome library and Soulseek at the same time. I can't add a Soulseek download to a Navidrome playlist automatically.

**The problem:** It's functional but fragmented. I still use Spotify for discovery and playlist sharing with friends. The self-hosted music stack is for "me time," not social listening.

**Verdict:** Keeping, but I'd love a unified solution. Maybe that's a future project.

---

## 🔴 What's Not Working (Or Barely Used)

### 9. GPU VM for Local LLMs — The Expensive Hobby

This hurts to admit. I have a Proxmox VM with an RTX 3060 running 13 local LLM models via Ollama. It works. I can query them. The Mac mini can route to them. But here's the truth: **I use Claude Code for 95% of my AI work.**

The local models are slower, less capable, and require more prompting finesse. When I'm trying to get something done, I reach for the API. When I'm tinkering on a Saturday, I play with the local models. That's not a business case — that's a hobby.

**The math:** ~$15/month in electricity. That's $180/year for something I use maybe 2 hours a month. I could get a lot of Claude API calls for $180.

**The plan:** I'm going to downsize. Keep 2-3 models for privacy-sensitive tasks (financial data, personal documents) and offload the rest. The GPU VM isn't going away, but it's becoming a specialty tool, not a daily driver.

**Verdict:** Scaling back, not shutting down. There's value in local inference for privacy, but 13 models is overkill.

### 10. Autobrr — The Automation I Don't Trust

Autobrr works. It snatches releases. It pushes to Sonarr. But I find myself checking it constantly — did it catch the new episode? Did the filter work? Is the indexer still connected? The automation creates anxiety instead of relieving it.

**The problem:** It's a black box that does important things, and I don't fully trust black boxes. I'm always waiting for the "it missed a release" moment.

**Verdict:** Keeping, but I'm simplifying. Fewer indexers, broader filters, less micromanagement.

---

## 💰 The Honest Cost Breakdown

Let's talk money. Here's what this actually costs me per month:

| Category | Monthly Cost | Annual Cost |
|----------|-------------|-------------|
| Electricity (Proxmox host) | ~$8 | $96 |
| Electricity (GPU VM) | ~$15 | $180 |
| Electricity (Mac mini) | ~$3 | $36 |
| Real-Debrid | ~$4 | $48 |
| Domain (devhandbook.io) | ~$1 | $12 |
| iCloud (wife's photos) | $3 | $36 |
| **Total** | **~$34/month** | **~$408/year** |

Now, what do I get for $408/year?

- Unlimited media streaming (Plex)
- Ad-free DNS for my whole network (Pi-hole)
- Password management (Vaultwarden)
- Audiobook ownership (Audiobookshelf)
- Music streaming (Navidrome)
- Photo backup (Immich)
- Tesla data logging (TeslaMate)
- Smart home automation (Home Assistant)
- VPN access (WireGuard)
- AI assistant (OpenClaw/Moon)

Is that worth $408? Honestly, yes. A Netflix + Spotify + Audible + Google One subscription stack would cost me $50-60/month. I'm paying less for more control.

But the *time* cost is the real kicker. If I valued my time at even $20/hour, this stack has cost me $2,000+ in maintenance, troubleshooting, and tinkering. That's the hidden tax of self-hosting, and it's one I willingly pay because I enjoy it.

---

## 🎯 What's Next for H2 2026

Based on this review, here are my priorities for the second half of the year:

### 1. Consolidate the GPU VM

Downsize from 13 models to 3. Keep a coding model, a general chat model, and a long-context model. Route everything else to APIs. Save ~$10/month in electricity and free up VRAM for actual tasks.

### 2. Finish the Finance Tracker Launch

I've had a complete small business finance tracker template ready since April. It's polished, tested, and documented. The only thing stopping it from being on Gumroad is... me. July goal: publish it.

### 3. Write More, Build Less

I have 10 blog posts on devhandbook.io and tools that get traffic but generate $0. The content is good — I need to add monetization (affiliate links for tools I actually use, maybe a "Pro" template tier) or accept that it's a hobby and focus on the digital products that can actually revenue.

### 4. Fix the Custom Domain Issue

The devhandbook.io domain is currently serving a Cloudflare challenge page instead of the actual blog. The preview URLs work fine, so it's a DNS/WAF configuration issue. I need to sort this out — it's embarrassing and blocks organic traffic.

### 5. Evaluate Immich vs. iCloud

Make a real decision: commit to Immich as the primary photo solution (and migrate my wife), or accept that iCloud is good enough and shut down Immich. The "backup of a backup" middle ground isn't serving anyone.

---

## The Bottom Line

Six months into 2026, my homelab is... fine. It's not the revolutionary productivity boost I imagined when I started. It's not paying for itself. But it's *mine*. I control it. I understand it. When something breaks, I fix it. When something works, I know exactly why.

That ownership has value, even if it's hard to put a dollar amount on it.

The key insight from this review: **I need to stop adding new services and start optimizing what I have.** The stack is deep enough. The marginal utility of "one more container" is near zero. The marginal utility of "make existing things better" is high.

So here's my challenge to you, if you're reading this and also have a homelab: Do your own mid-year review. Actually look at what you're running. Be honest about what you use. Turn off the stuff you don't. Optimize the stuff you do.

Your future self (and your electricity bill) will thank you.

---

*What's your homelab stack? What's working and what's collecting dust? I'd genuinely love to hear — the best part of this community is learning from each other's setups and mistakes.*
