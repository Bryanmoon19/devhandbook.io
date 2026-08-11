---
layout: post.njk
title: "The Jellyfin Ecosystem Stack: 10 Tools That Transform Your Media Server (August 2026)"
date: 2026-08-10
description: "Jellyfin is great on its own, but the ecosystem around it is exploding. From a walkable 90s video store UI to GPU transcoding benchmarks, here are 10 tools that turn your Jellyfin server into something Plex users can only dream about."
tags: ["jellyfin", "media-server", "self-hosted", "homelab", "plex-alternative", "docker", "transcoding", "open-source"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/jellyfin-ecosystem-stack"
---

# The Jellyfin Ecosystem Stack: 10 Tools That Transform Your Media Server

Jellyfin has quietly become the default media server for self-hosters. It's free, open-source, and doesn't phone home to a corporate mothership to tell them what you're watching. But the real story isn't Jellyfin itself — it's the ecosystem that's grown up around it.

In 2026, the Jellyfin ecosystem is exploding. New clients, plugins, dashboards, and companion tools are shipping every month. If you're still running stock Jellyfin with the default web UI, you're missing half the experience.

Here are 10 tools that transform Jellyfin from a basic media server into something Plex users pay $120/year for — and still don't get.

---

## 1. Halcyon Video — Walkable 90s Video Store UI (⭐177)

**What it is:** Halcyon Video turns your Jellyfin library into a first-person, walkable 1990s video rental store. Built with three.js, it renders your media as VHS tapes on shelves that you can walk up to, browse, and "rent."

**Why it's incredible:** This isn't a gimmick. The nostalgia hit is real — fluorescent lighting, carpet patterns, genre-labeled aisles, and the satisfying click of pulling a tape off the shelf. Your Jellyfin library metadata (posters, descriptions, ratings) populates the store automatically. It's self-hosted, runs in a browser, and connects directly to your Jellyfin API.

**The numbers:** 177 GitHub stars and climbing. The project hit the front page of Hacker News in early 2026 and has been gaining contributors ever since.

**Setup:** Docker container, point it at your Jellyfin URL, and you're browsing your library like it's 1997.

🔗 [Halcyon Video on GitHub](https://github.com/halcyon-video/halcyon-video)

---

## 2. JellyGlance — Modern Dashboard & Server Management (⭐52)

**What it is:** JellyGlance is a modern, standalone dashboard for Jellyfin that gives you live session monitoring, user statistics, recently added media, library overviews, download management, calendar views, webhook support, and backup tools — all in one clean interface.

**Why you need it:** Jellyfin's built-in dashboard is functional but barebones. JellyGlance gives you the kind of server analytics Plex Pass users get — who's watching what, from where, and for how long. The live session view shows real-time transcoding status, bitrate, and device info. The calendar integrates with Sonarr/Radarr to show upcoming releases.

**Standout features:**
- Live session monitoring with transcode details
- Per-user watch statistics and history
- Webhook integrations for Discord, Slack, and custom endpoints
- Automated backup scheduling for Jellyfin configs
- Mobile-responsive design that actually works on a phone

🔗 [JellyGlance on GitHub](https://github.com/Nerdy-Technician/JellyGlance)

---

## 3. Fathom — Modern Desktop Client with YouTube Integration (⭐35)

**What it is:** Fathom is a modern desktop client for Jellyfin built with a focus on design and user experience. It also includes an optional built-in YouTube player and Seerr request integration.

**Why it matters:** Jellyfin's web client works, but it's not winning any design awards. Fathom brings a polished, native-feeling experience to desktop with smooth animations, better keyboard shortcuts, and a layout that actually respects your screen real estate. The YouTube integration is a clever touch — watch your media and YouTube in the same app without switching contexts.

**Key features:**
- Native desktop experience (not an Electron wrapper of the web UI)
- Built-in YouTube player for trailers and related content
- Direct Seerr integration for requesting new media
- Picture-in-picture support
- Customizable themes

🔗 [Fathom on GitHub](https://github.com/Fathom-Media/fathom)

---

## 4. Intro Skipper — Auto-Skip Intros & Credits (⭐2,636)

**What it is:** The Intro Skipper plugin automatically detects and skips intro sequences and credits in TV shows. It uses audio fingerprinting to identify repeated segments across episodes.

**Why it's essential:** This is the single most-installed Jellyfin plugin for a reason. Binge-watching a show with 2-minute intros? That's 20 minutes saved per 10-episode season. The plugin analyzes audio fingerprints across episodes to detect repeated sequences, then adds a "Skip Intro" button (or auto-skips if you prefer). It also handles credits, so you jump straight to the next episode.

**Setup:** Install the plugin from the Jellyfin catalog, run a scheduled task to analyze your library, and you're done. Works with all Jellyfin clients that support the skip button.

🔗 [Intro Skipper on GitHub](https://github.com/intro-skipper/intro-skipper)

---

## 5. Jellyseerr — Media Requests That Your Users Will Actually Use (⭐7,500+)

**What it is:** Jellyseerr is a fork of Overseerr tailored for Jellyfin. It gives your users a beautiful, Netflix-style interface to discover and request new movies and TV shows. Requests flow into Sonarr and Radarr automatically.

**Why it's the killer app:** The #1 complaint about self-hosted media servers is "how do I ask for stuff?" Jellyseerr solves this completely. Your users browse trending movies, search by genre, see what's already available, and request anything that's missing. You approve (or auto-approve) and the *arr stack handles the rest.

**What makes it special:**
- Netflix-style discovery with trending, upcoming, and genre browsing
- User-specific request quotas and permissions
- Email/Discord notifications for request status
- Integration with Sonarr, Radarr, and Jellyfin
- Mobile-friendly PWA

🔗 [Jellyseerr on GitHub](https://github.com/Fallenbagel/jellyseerr)

---

## 6. SuggestArr — AI-Powered Recommendations (⭐1,248)

**What it is:** SuggestArr automatically requests recommended movies, TV shows, and anime to Jellyseerr based on your recently watched content on Jellyfin.

**Why it's clever:** Instead of manually hunting for what to watch next, SuggestArr analyzes your Jellyfin watch history and feeds recommendations directly into Jellyseerr. It's like having a personal curator that knows your taste and keeps your library fresh without you lifting a finger.

**How it works:**
1. SuggestArr checks your Jellyfin recently-watched list
2. Cross-references with recommendation sources (TMDb, Trakt, etc.)
3. Pushes suggestions to Jellyseerr as requests
4. You review and approve — or let it run on auto-pilot

🔗 [SuggestArr on GitHub](https://github.com/giuseppe99barchetta/SuggestArr)

---

## 7. Merge Versions Plugin — Clean Up Your Movie Library (⭐428)

**What it is:** The Merge Versions plugin scans your movie library and groups duplicate movies (different resolutions, editions, cuts) into a single entry with multiple versions.

**Why it fixes a real pain point:** If you keep both 1080p and 4K copies of movies, or have theatrical and director's cuts, Jellyfin shows them as separate entries by default. This plugin merges them into one listing with a version selector — exactly how Plex handles it, but free.

**Setup:** Install, run the scan, and your library is instantly cleaner. No manual grouping required.

🔗 [Merge Versions on GitHub](https://github.com/danieladov/jellyfin-plugin-mergeversions)

---

## 8. Themerr — Theme Songs for Your Library (⭐221)

**What it is:** Themerr downloads and plays TV show theme songs when you browse your library. It uses the ThemerrDB community database of theme songs.

**Why it's delightful:** This is the kind of polish that makes a media server feel premium. Browse to *The Office* and the theme plays. Scroll to *Game of Thrones* and the iconic intro kicks in. It's a small touch that makes browsing your library feel like a real media experience.

**Also check out:** The Theme Songs plugin (⭐160) by danieladov, which downloads theme songs from YouTube and lets you upload custom MP3s.

🔗 [Themerr on GitHub](https://github.com/LizardByte/Themerr-jellyfin)  
🔗 [Theme Songs Plugin](https://github.com/danieladov/jellyfin-plugin-themesongs)

---

## 9. GPU Transcoding Benchmarks — Know What Your Hardware Can Handle

**What it is:** Two community-driven benchmarking projects help you understand exactly how many simultaneous transcodes your GPU can handle.

**Jellybench (⭐27):** The official Jellyfin hardware survey client. Benchmarks your system's ffmpeg transcoding performance and contributes to the [Jellyfin Hardware Acceleration](https://hwa.jellyfin.org/) database, where you can compare your setup against thousands of others.

**Transcoding GPU Benchmark (⭐27):** A multi-vendor benchmark by SpaceinvaderOne that tests Intel, AMD, NVIDIA, and CPU transcoding with HDR tone-mapping, subtitle burn-in, and power efficiency measurements. Includes a community leaderboard.

**Why this matters:** "Can my Intel N100 handle three 4K transcodes?" is the most-asked question in Jellyfin communities. These benchmarks give you real data instead of forum speculation. The answer, by the way: yes, an N100 can handle 3-4 simultaneous 4K-to-1080p transcodes with tone mapping, thanks to Quick Sync Video.

**Quick reference — simultaneous 4K-to-1080p transcodes (HDR tone mapping on):**

| GPU | Transcodes | Power | Notes |
|-----|-----------|-------|-------|
| Intel N100 (QSV) | 3-4 | ~15W | Best value for small servers |
| Intel Arc A380 | 5-6 | ~45W | AV1 encode support |
| Intel UHD 770 (12th+ gen) | 4-5 | CPU package | Great if you already have the CPU |
| NVIDIA GTX 1660 | 3-4 | ~75W | Older but capable |
| NVIDIA RTX 4060 | 7-8 | ~60W | AV1 encode, overkill for most |
| Apple M4 (VideoToolbox) | 4-5 | ~20W | Mac Mini homelab sweet spot |

🔗 [Jellybench on GitHub](https://github.com/BotBlake/jellybench_py)  
🔗 [Transcoding GPU Benchmark](https://github.com/SpaceinvaderOne/transcoding-gpu-benchmark)

---

## 10. CrossWatch — Sync Your Watch Data Everywhere (⭐759)

**What it is:** CrossWatch synchronizes your watch history, ratings, and lists across Jellyfin, Plex, Emby, and external trackers like Trakt and Simkl.

**Why it's the glue:** If you use multiple media servers (or are migrating from Plex to Jellyfin), CrossWatch keeps everything in sync. Watch a movie on Jellyfin, and it's marked as watched on Plex and Trakt. Rate something on Trakt, and the rating appears in Jellyfin.

**Also worth checking out:**
- **Scrob (⭐318):** Self-hosted media tracking app — your own private Letterboxd + Trakt, syncing from Jellyfin/Plex/Emby
- **ListSync (⭐330):** Automatically imports your IMDb and Trakt lists into Jellyseerr

🔗 [CrossWatch on GitHub](https://github.com/cenodude/CrossWatch)  
🔗 [Scrob on GitHub](https://github.com/ellite/scrob)

---

## Bonus: The Infrastructure Layer

These aren't Jellyfin-specific, but they're essential to a complete media stack:

**Bazarr** — Automatic subtitle downloading. Pairs with Sonarr/Radarr to fetch subtitles in your preferred languages the moment media is imported. Supports 60+ subtitle providers.

**Tdarr** — Automated transcoding and library optimization. Converts your entire library to a uniform codec (H.265/HEVC for space savings, or AV1 for cutting-edge efficiency) without manual intervention.

**autobrr** — IRC/RSS announce monitoring. Grabs releases the second they hit trackers, before they propagate to Usenet indexers. The difference between a 30-second snatch and a 30-minute delay.

---

## The Stack at a Glance

Here's how these tools fit together:

```
┌─────────────────────────────────────────────────┐
│                  YOUR USERS                      │
│  (Halcyon Video / Fathom / Jellyfin Web UI)     │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│              JELLYFIN SERVER                     │
│  ┌──────────────────────────────────────────┐   │
│  │  Plugins: Intro Skipper, Merge Versions,  │   │
│  │  Themerr, Theme Songs, Playback Reporting │   │
│  └──────────────────────────────────────────┘   │
└──────┬──────────────────────┬───────────────────┘
       │                      │
┌──────▼──────────┐  ┌───────▼────────────────────┐
│  MEDIA PIPELINE  │  │  MANAGEMENT & DISCOVERY    │
│  Sonarr/Radarr   │  │  Jellyseerr (requests)     │
│  Bazarr (subs)   │  │  JellyGlance (dashboard)   │
│  Tdarr (encode)  │  │  SuggestArr (recommend)    │
│  autobrr (snatch)│  │  CrossWatch (sync)         │
└──────────────────┘  └────────────────────────────┘
```

---

## Why This Matters: Jellyfin vs Plex in 2026

"Jellyfin vs Plex 2026" gets searched 15,000 times a month. Here's the honest comparison:

**Plex gives you:**
- Polished default UI
- Built-in remote access (Plex Relay)
- Plex Pass features: hardware transcoding, intro skip, downloads ($4.99/month or $119.99 lifetime)
- Centralized auth (your users need Plex accounts)
- Your watch data sent to Plex's servers

**Jellyfin gives you:**
- Complete control over your data
- No accounts, no telemetry, no phone-home
- All features free — hardware transcoding, intro skip, downloads, live TV
- The ecosystem above — tools Plex can't match because they're open-source
- Local auth only (or LDAP if you want it)

The gap has narrowed dramatically. Two years ago, Plex's polish was a real advantage. Today, with Halcyon Video, Fathom, JellyGlance, and the plugin ecosystem, Jellyfin's experience is arguably *better* — and it's not monetizing your watch history.

**The bottom line:** If you're starting a new media server in 2026, start with Jellyfin. If you're on Plex and curious, spin up a Jellyfin container alongside it and try the ecosystem. You might find yourself migrating sooner than you think.

---

## Getting Started

The easiest way to try the Jellyfin ecosystem:

```bash
# 1. Jellyfin itself
docker run -d \
  --name=jellyfin \
  -v /path/to/config:/config \
  -v /path/to/media:/media \
  -p 8096:8096 \
  jellyfin/jellyfin:latest

# 2. Jellyseerr for requests
docker run -d \
  --name=jellyseerr \
  -v /path/to/jellyseerr/config:/app/config \
  -p 5055:5055 \
  fallenbagel/jellyseerr:latest

# 3. JellyGlance for dashboard
docker run -d \
  --name=jellyglance \
  -v /path/to/jellyglance/config:/app/config \
  -p 3000:3000 \
  ghcr.io/nerdy-technician/jellyglance:latest
```

Three containers, 10 minutes, and you've got a media server that rivals anything Plex offers — without the subscription, the telemetry, or the corporate oversight.

---

*What's in your Jellyfin stack? I'm always looking for new tools to add. Find me on [GitHub](https://github.com/Bryanmoon19) or drop a comment below.*
