---
layout: post.njk
title: "Debloat Your Smart TV: The Self-Hosted, Ad-Free, Privacy-First Guide"
date: 2026-10-26
description: "Five smart-TV debloat repos exploded on GitHub this month — cleanyourtv hit ~32k stars almost overnight, joined by aerial-tv, free-my-tv, tv-detox, and dumbtv. Your TV is a surveillance billboard with an HDMI port, and the community has finally built the tools to make it just a screen again. Here's the honest breakdown of every approach, which one fits your TV and your tolerance for risk, and how to turn the $800 ad machine in your living room back into a monitor."
tags: ["smart-tv", "debloat", "privacy", "self-hosted", "ad-free", "cleanyourtv", "aerial-tv", "free-my-tv", "tv-detox", "dumbtv", "homelab", "jellyfin", "pi-hole", "dns"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/2026-10-26-debloat-smart-tv-ad-free/"
affiliate: false
cta: true
---

Your smart TV is not a television. It's a billboard that happens to display video, and it's been watching you the entire time you thought you were watching it.

The numbers have been public for years and somehow we all just shrugged: smart TVs ship with ad platforms baked into the OS, telemetry that reports what you watch (down to the exact show and timestamp), and an automatic content recognition (ACR) system that can identify what's on screen even when it's coming from a game console or a DVD player. You paid $800 for the panel, and then you became the product on top of it.

This month, something shifted. Five separate "debloat your TV" repositories exploded on GitHub in the same window — **cleanyourtv** rocketed to roughly 32,000 stars almost overnight, and it was joined by **aerial-tv**, **free-my-tv**, **tv-detox**, and **dumbtv**. When five projects attacking the same problem all spike at once, it's not a coincidence. It's a signal that a whole lot of people hit their limit with the ads, the data collection, and the creeping enshittification of the thing on their wall.

This post is the guide I wish existed when I started down this path. I'm going to explain what your TV is actually doing, walk through the honest set of options — from "just never connect it to Wi-Fi" (still underrated) all the way to full firmware replacement — and give you a concrete path to turn your smart TV back into a dumb, trustworthy screen. This isn't a one-size-fits-all how-to, because the right answer depends on your TV's brand and your tolerance for tinkering. It's a decision framework, with the tools to back it up.

## What Your Smart TV Is Actually Doing

Before I talk about fixes, you need to know what you're fixing. Most people's mental model is "my TV runs some apps and shows me an occasional ad." The reality is closer to a miniature surveillance platform with a screen attached.

**Automatic Content Recognition (ACR).** This is the big one, and it's on by default on most major brands (Samsung calls it "Viewing Information Services," Vizio calls it "Viewing Data," LG calls it "Live Plus"). ACR periodically captures a fingerprint of whatever is on screen — not a recording, but enough to identify the content — and ships it back to the manufacturer. It doesn't matter if you're watching Netflix, a Blu-ray, or a video game. The TV identifies it and reports it. Vizio was famously fined $2.2 million by the FTC in 2017 for doing this *without telling anyone*, and the practice has since spread everywhere with better disclosure and worse consent defaults.

**Ad injection into the OS.** The home screen on a modern smart TV is not neutral. It has sponsored rows, recommended-content slots the manufacturer gets paid to place, and — on some brands — even banner ads that overlay the interface. This is why a 2023 "mid-range" TV often has a *worse* interface than a 2015 dumb panel did. You're not getting a cleaner OS; you're getting a cleaner revenue stream for someone else.

**Telemetry and watch history.** Every app you open, how long you watch, what you search for — it's logged and tied to an advertising ID. This is the same tracking profile your phone builds, except it's harder to opt out of and you can't install an ad blocker as easily.

**The forced-OS problem.** Here's the structural issue: the TV *requires* an internet connection to fully function, and the terms you agreed to (often at first boot, often non-skippable in spirit) grant the manufacturer the right to collect this data and serve you ads. Some TVs refuse to work properly, or nag you constantly, without a network connection. The "smart" in "smart TV" is not a feature you asked for; it's a business model you got opted into.

The good news: none of this is necessary for the TV to be a *screen*. A panel is a panel. The "smart" layer is software running on top of commodity hardware, and software can be removed, replaced, or simply never given a network connection.

## The Five Repos (And What Each One Actually Does)

The explosion this month is real, and the projects cluster around a few distinct strategies. Let me break down what each one is, because they're not interchangeable — they attack the problem at different layers.

### cleanyourtv (~32k stars) — the big one

[cleanyourtv](https://github.com) is the project that spiked to ~32k stars, and it's the closest thing to a "turnkey" debloat tool in this wave. Its core approach: **it walks you through removing or neutering the ad and telemetry components of the TV's own OS** — often via the TV's developer/settings menus, service-menu tricks, or ADB (Android Debug Bridge) for TVs that run Android TV / Google TV. It's essentially a curated set of scripts and checklists organized by brand (Samsung, LG, Sony, Hisense, TCL, Vizio).

What it *doesn't* do is replace the OS. It trims the stock firmware down to something less hostile by disabling packages, revoking the ACR permission, and blocking the advertising domains. This is the highest-leverage, lowest-risk option for most people, because you keep the native apps and the manufacturer's warranty status, but you cut the surveillance and most of the ads.

### aerial-tv — turn it into a screensaver/frame machine

[aerial-tv](https://github.com) is the most delightful of the five, and it's aimed at a different goal entirely: **it replaces the smart-TV experience with a gorgeous, screensaver-first interface.** Think of it as "your TV, but it's now a beautiful ambient display that plays Apple-style Aerial screen savers, and only becomes a normal TV when you want it to."

This is for the person who's accepted they don't want the smart layer *at all* — they want their panel to be a calm, ad-free screen that shows art and plays video from sources *they* control. aerial-tv pairs naturally with an external player (a $40 Android box, an Apple TV with your own apps, or a Pi-based player) so the TV itself never touches the internet.

### free-my-tv — jailbreak the firmware

[free-my-tv](https://github.com) is the most aggressive of the group. It's about **gaining root on the TV's OS** — jailbreaking the firmware — to fully replace or strip the stock OS. On LG's webOS and Samsung's Tizen this is genuinely hard, and the project focuses on specific models and firmware versions where the bootloader or the OS has a known vulnerability.

This is not for the faint of heart. Firmware jailbreaking can brick a TV, voids the warranty, and is version-sensitive (a firmware update can slam the door on your exploit). But for the purist who wants the *entire* smart layer gone and a fully owned device, this is the frontier. Treat it as an enthusiast project, not a casual weekend tweak.

### tv-detox — the DNS/network layer

[tv-detox](https://github.com) attacks the problem where a lot of us already live: **at the network level.** Rather than touch the TV's firmware at all, tv-detox provides curated blocklists of advertising and telemetry domains — ready to drop into Pi-hole, AdGuard Home, or your router's DNS filter — plus firewall guidance to restrict what the TV can reach.

This is the "do no surgery" option. You leave the TV's software alone and instead starve it: no ad domains, no telemetry endpoints, no tracking. It pairs beautifully with the [WireGuard + Pi-hole privacy stack](/blog/2026-04-21-wireguard-pihole-privacy-stack/) I wrote about earlier this year. The trade-off is that over-aggressive blocking can break some streaming apps that genuinely need to reach their own infrastructure — you'll need to whitelist carefully.

### dumbtv — the "make it dumb again" philosophy project

[dumbtv](https://github.com) is the most opinionated and the most philosophical. Its premise is simple and a little punk: **the best smart TV is a dumb TV.** It's a project and a manifesto rolled together — guidance on buying panels that are still "dumb" or easily de-smarted, plus the setup to permanently cut a smart TV off from the internet and drive everything through a self-hosted front end (Jellyfin, a media box, a Pi) instead.

dumbtv is where the community is staking the long-term claim: the "smart" features were never worth it, and the ideal end state is a screen that does *one thing* — display what you send it — with no network connection and no opinions of its own.

## The Decision Framework: Pick Your Layer

Here's the key insight that ties all five together: **they operate at different layers, and you should pick based on how much risk you'll accept and how much of the "smart" experience you want to keep.**

| Approach | Layer | Risk | Keeps native apps? | Effort |
|---|---|---|---|---|
| **Never connect to Wi-Fi** | Network (manual) | None | No | Trivial |
| **tv-detox (DNS blocklists)** | Network (automated) | Low | Mostly | Easy |
| **cleanyourtv (ADB/pkg removal)** | OS (tweak) | Low-Med | Yes | Medium |
| **aerial-tv (replace interface)** | OS (replace) | Medium | No | Medium |
| **free-my-tv (jailbreak)** | Firmware (root) | High (brick risk) | No | High |
| **dumbtv (buy a dumb panel)** | Hardware | None | No | Buy a new TV |

There's no single "best." There's a *right answer for your situation*. Here's the honest flowchart:

**1. Do you actually need the smart features?**
If you watch everything through a Roku, Apple TV, Shield, or a console anyway — if the TV's own OS is just the annoying thing you click through to reach HDMI — then you don't need to debloat it. You need to **disconnect it.** Never give it Wi-Fi, factory-reset it, and skip setup. Pair that with a dumb panel or a cheap media box, and you're done. This is the dumbtv philosophy, and it's the single highest-leverage move in the entire guide. A screen with no network is a screen with no ads and no telemetry, full stop.

**2. Do you want to keep the native apps (Netflix, etc.) but kill the ads and tracking?**
Then your answer is **cleanyourtv** plus a **tv-detox** DNS blocklist. Run cleanyourtv's brand-specific checklist to disable ACR, revoke the ad-ID permissions, and strip the ad packages; then point the TV's DNS at your Pi-hole/AdGuard Home with the tv-detox lists loaded. You keep the apps, you lose the billboard behavior, and the risk is low.

**3. Are you a purist who wants the whole smart layer gone but doesn't want to brick anything?**
Go **aerial-tv + a media box.** Replace the TV's brain with a screensaver-first interface, and drive all playback from a $40 Android box or an Apple TV running apps *you* installed. The TV becomes a gorgeous, ad-free frame that you fully own.

**4. Are you a tinkerer who accepts real risk?**
Then **free-my-tv** is the frontier. Read the model/firmware compatibility list *twice* before you touch anything, back up what you can, and accept that a brick is a possible outcome. This is the "I want root on my TV" path, and it's genuinely exciting — just not safe.

## The Concrete Path I'd Recommend

For 90% of readers, here's the setup that gets you 95% of the benefit with near-zero risk. I'll keep it concrete.

**Step 1 — Decide the TV's role.** Is the built-in OS your actual player, or just a pass-through to HDMI? If pass-through, stop here and disconnect it. No Wi-Fi, no ethernet, factory reset, done. If you genuinely use the built-in apps, continue.

**Step 2 — Kill ACR and ad personalization (5 minutes, no tools).** Go into settings and turn off anything named "Viewing Information Services," "Viewing Data," "Live Plus," "Smart Interactivity," "Personalized ads," or "ACR." Disable the advertising ID / "reset" it so it's worthless. This is brand-dependent but universally findable in Settings → Privacy or Settings → General. Do this before anything else — it's the biggest privacy win and it's free.

**Step 3 — Run the cleanyourtv checklist for your brand.** Follow the brand-specific steps to disable telemetry packages and ad components. On Android TV / Google TV sets this is usually ADB commands (`adb shell pm disable-user --user 0 com.package.name`); on Tizen/webOS it's service-menu or settings tricks. The repo's checklists are the curated version of tribal knowledge that used to be scattered across forums.

**Step 4 — Block the domains with tv-detox.** Load the tv-detox blocklists into Pi-hole or AdGuard Home, point the TV's DNS at it (and lock the TV out of alternate DNS), and watch the ads and telemetry requests start dropping. Check your Pi-hole query log the first week — you'll be shocked how many requests a "sleeping" TV makes.

**Step 5 — Add the network firewall rules.** Restrict the TV to only the outbound destinations its apps genuinely need, and block everything else. This is defense in depth: even if a firmware update re-enables something you disabled, the network layer still catches it.

The beauty of this layered approach is that each layer covers the next one's failure. The OS tweaks cut the active collection, and the DNS/firewall layer means even a misbehaving TV can't phone home. And if you ever decide to go full dumbtv later, you've already got the network plumbing in place.

## What This Means For Your Homelab

There's a deeper point here that connects this to everything else I write about on this site. Smart TVs are the same story as cloud services, social networks, and proprietary apps: **you don't own the software that runs the things you bought, so you don't fully own the things.** The de-Google and privacy work I've covered — [WireGuard + Pi-hole](/blog/2026-04-21-wireguard-pihole-privacy-stack/), [self-hosted DNS](/blog/2026-10-23-self-hosted-dns-resolver/), [Jellyfin](/blog/2026-08-10-jellyfin-ecosystem-stack/) — all point at the same conclusion. The way out is to own the layer that matters: your own front end, your own resolver, your own media server, and now, your own screen.

The five-repo explosion this month isn't a fad. It's the same signal the self-hosting movement has been broadcasting for a decade, arriving at the biggest screen in your house. The wall doesn't come down — the route around it just got a whole lot more traveled.

So here's your weekend project, if you want one: spend twenty minutes on Steps 2 through 4. Disable the ACR, kill the ad packages, and point your TV's DNS at a Pi-hole running the tv-detox lists. Watch your query log. Then tell me — does it feel different, watching a screen that isn't watching you back?

It does. That's the whole point.
