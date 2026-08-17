---
layout: post.njk
title: 'Self-Hosted This Week: 1990s Video Stores, Server Monitoring, and AI Budget Analysis'
description: 'A weekly roundup of the most interesting self-hosted tools and stories from the homelab world, featuring halcyon-video nostalgia, Beszel monitoring, Immich fixes, and Actual Budget AI features.'
tags: [selfhosted, weekly, homelab, roundup]
date: 2026-08-17
author: Bryan
---

# Self-Hosted This Week: 1990s Video Stores, Server Monitoring, and AI Budget Analysis

August 10 – August 17, 2026

This week in self-hosted land brought **nostalgia**, **monitoring innovations**, and **AI-powered features**. From a Jellyfin frontend that recreates the 1990s video rental store experience to Beszel crossing 24K stars as the lightweight server monitoring darling, the community continues to build tools that are both practical and delightful.

Meanwhile, Actual Budget is pushing AI features into personal finance management, and Immich keeps shipping fixes at a blistering pace.

Whether you're monitoring your homelab, managing your budget, or just want to walk through your media library like it's Blockbuster 1995, this week has something for you.

Let's dive in.

---

## 1. halcyon-video: Your Jellyfin Library as a 1990s Video Rental Store

**What happened:** A new project called halcyon-video launched this week, turning your Jellyfin or Plex library into a walkable 1990s video rental store using three.js and first-person navigation.

**Why it matters:** This is the kind of creative frontend that reminds us why self-hosting is fun. It's not just about functionality — it's about making your digital life feel personal and nostalgic. The project hit 373 stars in its first week, showing there's appetite for playful interfaces.

**The tech stack:**
- three.js for 3D rendering
- First-person navigation (WASD + mouse look)
- Integrates with Jellyfin/Plex APIs
- Self-hosted, runs in your browser

**The vibe:** Imagine walking through aisles of VHS boxes, pulling titles off the shelf to read the back cover. That's halcyon-video. It's impractical in the best possible way.

**Try it:** The project is fresh, so expect rough edges. But if you've ever wanted to gamify your media browsing, this is it.

**[halcyon-video GitHub](https://github.com/homelab-halcyon/halcyon-video)** (373 stars, trending)

---

## 2. Beszel: Lightweight Server Monitoring Hits 24K Stars

**What happened:** Beszel crossed 24,000 GitHub stars this week, cementing its position as the go-to lightweight server monitoring tool for homelabs.

**Why it matters:** In a world of heavy monitoring stacks (looking at you, Prometheus + Grafana + Alertmanager), Beszel offers something different: historical data, Docker stats, and alerts without the complexity. It's the monitoring tool for people who want visibility, not a second job managing the monitoring system.

**What Beszel does:**
- Historical metrics with clean charts
- Docker container stats at a glance
- Alerting when things go wrong
- Lightweight agent (minimal resource overhead)
- Single binary deployment

**The monitoring landscape:** Beszel sits between simple uptime monitors and full APM platforms. It's perfect for homelabs and small deployments where you need to know what's happening without running a monitoring cluster.

**Deployment:** Single binary or Docker. No database to manage separately.

**[Beszel GitHub](https://github.com/heyimbeszel/beszel)** (24K+ stars)

---

## 3. Actual Budget: AI-Powered Budget Analysis and Monte Carlo Simulations

**What happened:** Actual Budget shipped a wave of AI features this week, including budget analysis reports with future month selection, Monte Carlo simulation explanations, and category autocomplete improvements.

**Why it matters:** Personal finance apps rarely innovate on the AI front. Actual Budget is showing how AI can enhance (not replace) envelope budgeting: analyzing spending patterns, explaining simulation results, and making category selection frictionless.

**This week's AI features:**
- **Budget analysis reports** — Select future months in date ranges for projections
- **Monte Carlo explanation** — AI explains fees and taxes in simulation results
- **Category autocomplete** — Keyboard selection fixed for faster entry
- **Side-nav design competition** — Community voting on new UI designs

**The self-hosted finance angle:** Actual Budget is one of the few self-hosted options that feels polished enough for daily use. The AI features are opt-in and enhance the core envelope budgeting model rather than trying to replace it.

**Try it:** `docker pull actualbudget/actual:latest` or update via your existing deployment.

**[Actual Budget GitHub](https://github.com/actualbudget/actual)** (15K+ stars)

---

## 4. Immich: Flutter Lints, Migration Fixes, and Shared Link Validation

**What happened:** Immich continued its rapid development pace with commits landing daily. This week's highlights include Flutter lint updates, migration order fixes, and shared link creation validation.

**Why it matters:** Immich is the self-hosted Google Photos alternative that's actually ready for daily use. The team's shipping cadence is impressive — multiple merges per day with clear commit messages and active issue triage.

**This week's commits:**
- `chore: pump flutter_lints to 6.0` — Keeping mobile code quality high
- `fix(server): migration order` — Database migration reliability
- `fix: shared link create validation` — Better security on shared albums
- `fix(mobile): prevent snapping to center on pinch-to-zoom release` — UX polish
- `chore(web): remove unused code` — Cleanup for faster loads

**Deployment tip:** If you're running Immich, stick to release tags, not `main`. The project moves fast, and `main` can have breaking changes between releases.

**[Immich GitHub](https://github.com/immich-app/immich)** (50K+ stars)

---

## 5. Jellyfin: Large Playlist Persistence Fix

**What happened:** Jellyfin merged a fix for large playlist persistence this week, addressing an issue where playlists with many items would fail to save properly.

**Why it matters:** If you've ever built a massive playlist (think: complete discography, multi-season TV soundtracks), you've hit the SQL variable limit. The fix ensures playlists persist correctly regardless of size.

**Also this week:**
- Translations updated (Italian, Portuguese)
- .NET dependencies bumped via Renovate
- Continued Weblate translation contributions

**The media server wars:** Jellyfin vs. Plex vs. Emby continues, but Jellyfin's community-driven development and commitment to being truly free (no premium tier, no phone-home) keeps it competitive.

**Update now:** If you're running Jellyfin from source or nightly builds, this fix landed this week.

**[Jellyfin GitHub](https://github.com/jellyfin/jellyfin)**

---

## 6. Coolify: UI Polish and Version Display

**What happened:** Coolify shipped a series of UI improvements this week, including table dropdown positioning, Coolify version display in the mobile sidebar, and backup execution table scrolling fixes.

**Why it matters:** Coolify is becoming the Vercel/Netlify alternative for self-hosters who want to deploy apps without wrestling with Docker Compose files. The UI polish shows the project is maturing beyond "it works" to "it feels good."

**This week's changes:**
- Table dropdowns positioned outside overflowing containers (no more clipped menus)
- Coolify version visible in mobile sidebar (easier debugging)
- Backup execution table scrolling and borders refined
- Breadcrumb search icon and header border tweaks
- Admin navigation link for root users

**The deployment platform landscape:** Coolify vs. CapRover vs. Dokku vs. Portainer. Coolify's developer experience focus (Vercel-like workflows) is its differentiator.

**[Coolify GitHub](https://github.com/coollabsio/coolify)** (25K+ stars)

---

## 7. dawarich: Google Timeline Alternative Hits 10K Stars

**What happened:** dawarich, the self-hosted Google Timeline alternative, crossed 10,000 GitHub stars this week.

**Why it matters:** Google shut down Timeline for most users, leaving a gap for location history tracking. dawarich fills that gap with a self-hosted solution that imports existing Google Takeout data and continues tracking from there.

**What dawarich does:**
- Import your Google Location History Takeout
- Continue tracking via mobile app or API
- Visualize your movements on maps
- Export data anytime (no vendor lock-in)
- Self-hosted, so your location data stays yours

**The privacy angle:** Location history is deeply personal. Self-hosting dawarich means you control where that data lives and who can access it.

**[dawarich GitHub](https://github.com/Freika/dawarich)** (10K+ stars)

---

## 8. Pulse: AI-Powered Infrastructure Monitoring

**What happened:** Pulse, the AI-powered monitoring tool for Proxmox, Docker, Kubernetes, TrueNAS, and vSphere, continues to gain traction at 6.5K stars.

**Why it matters:** Pulse isn't just another dashboard — it's a monitoring tool with AI-powered failure detection. It watches for "silent failures" and provides verified fixes. That's a step up from "here's a red status indicator, good luck."

**What makes Pulse different:**
- AI patrols your infrastructure continuously
- Detects silent failures (things that break without alerts)
- Provides verified fixes, not just error messages
- Supports Proxmox, Docker, K8s, TrueNAS, vSphere
- Self-hosted, so your infrastructure data stays local

**The trend:** Dashboards are evolving from static link pages to intelligent monitoring hubs. Pulse is leading that charge.

**[Pulse GitHub](https://github.com/rcourtman/Pulse)** (6.5K stars)

---

## 9. rakazo: Open-Source Grok Bot Alternative

**What happened:** rakazo launched this week as an open-source Grok Bot alternative, letting you choose your own model and sandbox. It hit 581 stars quickly.

**Why it matters:** As AI bots proliferate, having self-hosted alternatives to proprietary options (Grok, Claude, etc.) becomes important. rakazo gives you control over the model, the sandbox, and the data.

**What rakazo offers:**
- Choose your own LLM (local or API-based)
- Configurable sandbox for tool execution
- Self-hosted, so your conversations stay private
- Extensible with custom tools and integrations

**The AI bot landscape:** rakazo joins a growing field of self-hosted AI assistants. The differentiator is flexibility — bring your own model, run it your way.

**[rakazo GitHub](https://github.com/rakazo-ai/rakazo)** (581 stars, new)

---

## 10. scanopy: Network Diagrams That Update Themselves

**What happened:** scanopy, the self-hosted network diagram tool that auto-discovers and updates your network topology, hit 5,321 stars this week.

**Why it matters:** Keeping network diagrams current is a pain. scanopy automates that by discovering devices, mapping connections, and updating diagrams as your network changes.

**What scanopy does:**
- Auto-discovers network devices
- Maps connections and topology
- Updates diagrams as things change
- Self-hosted, so your network map stays private
- Export to common diagram formats

**The homelab reality:** If you're like most homelabbers, your network diagram is outdated the moment you finish drawing it. scanopy solves that.

**[scanopy GitHub](https://github.com/scanopy/scanopy)** (5.3K stars)

---

## What's Next

This week's theme: **innovation across the stack**. From nostalgic frontends (halcyon-video) to AI-powered monitoring (Pulse, Actual Budget), the self-hosted ecosystem is maturing while staying fun.

A few observations:

1. **Nostalgia sells** — halcyon-video's 373 stars in a week shows people want playful interfaces, not just functional ones.
2. **Lightweight monitoring wins** — Beszel's 24K stars prove there's demand for simple, effective monitoring without the Prometheus complexity tax.
3. **AI is here to stay** — Actual Budget's AI features show that AI can enhance existing workflows without replacing them.
4. **Privacy matters** — dawarich's growth (10K stars) reflects demand for self-hosted alternatives to Google services.
5. **Network documentation is hard** — scanopy's success shows that automation for tedious tasks (like updating network diagrams) is valuable.

The self-hosted ecosystem isn't slowing down — it's diversifying. And that's good news for everyone running services at home.

---

*This weekly roundup is published every Saturday. Catch the next one when new tools make waves in the homelab world.*

<div class="post-tags">
  <span class="post-tag">#selfhosted</span>
  <span class="post-tag">#homelab</span>
  <span class="post-tag">#devops</span>
  <span class="post-tag">#open-source</span>
  <span class="post-tag">#monitoring</span>
</div>
