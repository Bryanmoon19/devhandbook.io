---
layout: post.njk
title: "Self-Hosted Live TV & IPTV: Your Own Channels From M3U/Xtream (No Sketchy Box Required)"
date: 2026-11-11
description: "You already self-host your movies — now self-host the channel guide. Turn M3U and Xtream Codes playlists into a legitimate DVR-style live TV grid with an EPG, on your own hardware, without touching gray-market resellers."
tags: ["iptv", "live-tv", "self-hosted", "homelab", "jellyfin", "epg", "m3u", "xtream", "media-server", "docker"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-live-tv-iptv"
---

# Self-Hosted Live TV & IPTV: Your Own Channels From M3U/Xtream

Most self-hosters have cracked the on-demand part. Movies on Jellyfin. Shows on Sonarr. Music on Navidrome. The one layer that's still missing from almost every media cluster is **live TV** — the channel grid you flip through, the guide that tells you what's on *right now*, and the DVR that records something while you're asleep.

That layer is actually the easiest one to build, and you don't need a "sketchy box," a dodgy Amazon device, or a gray-market reseller to do it. You need three things: an **M3U playlist** (or Xtream Codes login), a **tuner/proxy layer** that turns it into something your media server understands, and an **EPG** (electronic program guide) so the whole thing looks like the TV you grew up with.

The angle is simple: **you already self-host your movies — now self-host the channel guide.**

---

## Why Live TV Is the Missing Layer

Think about what a complete media stack looks like in 2026:

- **On-demand video** → Jellyfin / Plex / Emby
- **Requests** → Jellyseerr / Overseerr
- **Downloads** → Sonarr / Radarr / autobrr
- **Music** → Navidrome / Jellyfin
- **Audiobooks** → Audiobookshelf
- **Photos** → Immich

And then... live TV. A gaping hole. Everyone still has a separate Roku, an Apple TV app, or an antenna that only catches three channels. Meanwhile, your server is sitting there, perfectly capable of streaming a live feed, showing a grid, and recording to disk.

Live TV is genuinely useful too — not just a novelty. Local news, live sports, weather emergencies, background noise while you work. It's the one media format where *timing* matters, and where "on-demand" fundamentally can't replace the experience.

The good news: the entire live-TV layer is built on open formats (M3U) and open tools, and it runs entirely on your own hardware.

---

## The Legitimate vs. Gray-Market Line (Important)

Let's get this out of the way, because "IPTV" has a bad reputation for a reason.

**Legitimate sources of M3U/Xtream playlists:**

- **Your own media library** — turned into a 24/7 "channel" via tools like WBTV (more below)
- **Free-to-air (FTA) streams** — many broadcasters publish direct .m3u8 links
- **Free IPTV lists** — community-maintained lists of freely broadcast, legally available channels (i.e., [iptv-org](https://github.com/iptv-org/iptv))
- **Your cable/satellite provider** — if you already pay for TV, many providers expose an IPTV feed you're entitled to access
- **Local antenna + HDHomeRun** — real OTA channels fed into the same stack

**Gray market (avoid):** "IPTV subscriptions" sold for $10/month with 10,000 channels, resold on Discord and Telegram, that clearly aren't licensed. Those break the law, fund sketchy operations, and disappear overnight. Nothing in this guide requires one.

The entire stack below works beautifully with *free, legal* sources. If you choose to plug in other playlists, that's between you and your conscience — but the tools are 100% legitimate.

---

## The Tools: An Overview

Here's the complete toolkit, then we'll build the stack piece by piece.

| Tool | What it does | Role in the stack |
|------|-------------|-------------------|
| **[silirim/VodMax](https://github.com/silirim/VodMax)** | Self-hosted media center for live TV (M3U + Xtream) | Drop-in Jellyfin/Plex alternative focused on live TV |
| **[WB2024/WBTV](https://github.com/WB2024/WBTV)** | Turns your own media library into a live TV channel guide | Make your own "channels" from local files |
| **xTeVe** | M3U/Xtream proxy + EPG muxer | Bridges playlists into Jellyfin/Emby/Plex |
| **Jellyfin Live TV + IPTV plugin** | Native tuner/DVR frontend | The grid, the guide, the recording |
| **EPG sources** | XMLTV program guides | "What's on now" for every channel |
| **ffmpeg** | Transcoding | Normalize codecs so every channel plays everywhere |

Let's look at each.

---

## 1. VodMax — The Live-TV-First Media Center

**What it is:** VodMax is a self-hosted media center built specifically around live TV. Unlike Jellyfin (which bolts live TV onto an on-demand core), VodMax treats the channel grid and the EPG as the primary interface. It supports **both M3U playlists and Xtream Codes** natively.

**Why it matters:** If your main goal is "I want a TV guide on my TV," VodMax is arguably a better fit than Jellyfin. It's lighter, its live-TV UI is more polished, and it doesn't carry the on-demand library baggage. Think of it as the Kodi-style "what's on right now" experience, but server/client over the network.

**Key features:**
- Native M3U + Xtream Codes support (no proxy required)
- EPG integration (XMLTV)
- Multi-client: web, Android TV, iOS
- Channel grouping, favorites, and search
- Clean, TV-first interface

**Setup (Docker):**

```bash
docker run -d \
  --name=vodmax \
  -v /path/to/vodmax/config:/config \
  -p 8443:8443 \
  --restart unless-stopped \
  silirim/vodmax:latest
```

🔗 [VodMax on GitHub](https://github.com/silirim/VodMax)

---

## 2. WBTV — Turn Your Own Library Into Live TV

**What it is:** WBTV is the cleverest idea in this space. Instead of ingesting someone else's channels, it **generates a live TV experience from your own media library**. Point it at your movies and shows, and it builds an EPG-style guide with "channels" like "Action Movies," "Comedy," "Sci-Fi Marathon," each playing continuously on a schedule.

**Why it's brilliant:** This is the missing link between "I have 500 movies" and "I want to flip channels and stumble onto something." It recreates the *serendipity* of cable TV — the reason people used to watch things they'd never search for — using content you already legally own.

**How it works:**
1. Point WBTV at your media folders
2. It builds a channel lineup (or you curate your own)
3. It generates an M3U playlist + XMLTV EPG for those channels
4. Feed that M3U into any player (Jellyfin, VodMax, VLC)

The output is a standard M3U, so it composes with everything else in this guide.

🔗 [WBTV on GitHub](https://github.com/WB2024/WBTV)

---

## 3. xTeVe — The M3U/Xtream Proxy & EPG Muxer

**What it is:** xTeVe is the glue that makes *any* M3U or Xtream source work with *any* media server. It sits between your playlists and your tuner (Jellyfin/Emby/Plex), normalizing everything into a single clean feed.

**Why you need it (even with Jellyfin's native support):**

- **Deduplication** — collapse hundreds of channels into a curated list
- **EPG muxing** — combine multiple XMLTV sources into one guide
- **Filtering** — strip out channels you don't want (or that are broken)
- **Xtream → M3U conversion** — turn an Xtream Codes login into a plain M3U
- **Buffering & re-streaming** — stabilize flaky upstream sources

**Setup (Docker):**

```bash
docker run -d \
  --name=xteve \
  -v /path/to/xteve/config:/config \
  -p 34400:34400 \
  --restart unless-stopped \
  alturismo/xteve
```

Then browse to `http://localhost:34400/web/`, add your M3U URL, map your EPG, and xTeVe exposes a clean `http://localhost:34400/xteve.m3u` + `xteve.xml` that Jellyfin consumes as a "M3U Tuner."

🔗 [xTeVe on GitHub](https://github.com/xteve-project/xTeVe)  
🔗 [xTeVe Docker](https://hub.docker.com/r/alturismo/xteve)

---

## 4. Jellyfin Live TV + IPTV Plugin — The DVR Frontend

**What it is:** Jellyfin has a first-class Live TV feature with DVR recording, and its **IPTV plugin** lets you add M3U playlists as tuners directly — no xTeVe required for simple cases.

**Why Jellyfin wins here:** If you're already a Jellyfin household, this is the path of least resistance. Live TV channels show up in the same app as your movies, the guide is integrated, and recording drops straight into your existing library. Your family doesn't need a *new* app to learn.

**Two ways to add live TV to Jellyfin:**

**Option A — Direct M3U (simple):**
1. Install the **IPTV plugin** from the plugin catalog
2. Dashboard → Live TV → Add Tuner → "M3U Tuner"
3. Paste your M3U URL
4. Optionally add an XMLTV EPG URL

**Option B — xTeVe (advanced, recommended):**
1. Run xTeVe as above to curate/filter/mux your channels
2. Add `http://xteve:34400/xteve.m3u` as the tuner
3. Add `http://xteve:34400/xteve.xml` as the EPG

Option B gives you deduplication, filtering, and a stable feed — worth the extra container once your playlist has more than a few dozen channels.

**DVR recording:** Once channels are in, Jellyfin's built-in DVR lets you schedule recordings from the guide, with series scheduling, retention policies, and hardware-transcoded recordings. This is the part that turns "live TV" into "live TV + TiVo."

🔗 [Jellyfin Live TV docs](https://jellyfin.org/docs/general/server/live-tv/)

---

## 5. EPG Sources — The "What's On Now" Layer

An M3U without an EPG is just a list of raw streams. The EPG (Electronic Program Guide) is what makes it feel like *TV* — the grid, the program titles, the "starts in 5 minutes" notices.

**Free, legal EPG sources:**

- **[iptv-org/epg](https://github.com/iptv-org/epg)** — a massive community-maintained XMLTV guide covering free-to-air channels worldwide
- **[EPG.best](https://epg.best)** — free XMLTV for many regions (paid tier for more)
- **WebGrab+Plus** — scrapes program listings from official broadcaster sites into XMLTV (the most legit option, since it uses first-party data)
- **Your provider's own EPG** — many IPTV providers publish an XMLTV URL you're already entitled to use

**Mapping:** Most of these tools auto-map channels by name. For anything that doesn't map, xTeVe's channel editor lets you manually assign the right guide entry — a one-time task that's worth it.

🔗 [iptv-org EPG](https://github.com/iptv-org/epg)  
🔗 [WebGrab+Plus](http://webgrabplus.com/)

---

## 6. Transcoding — Make Every Channel Play Everywhere

Here's the unglamorous reality: free IPTV streams come in a zoo of codecs and containers. Some are H.264 in MPEG-TS, some are H.265, some are 720p, some are 1080i. Your TV might not handle all of them.

**ffmpeg is the answer.** Every tool in this stack leans on it:

- **Jellyfin** transcodes live streams on-the-fly using your GPU (Quick Sync, NVENC, VideoToolbox)
- **xTeVe** can buffer and re-stream to normalize format
- **VodMax** handles transcode settings per-client

**The hardware rule of thumb** (from the Jellyfin ecosystem benchmark post): an Intel N100 with Quick Sync handles 3–4 simultaneous 4K-to-1080p transcodes at ~15W. Live TV is mostly 1080i or 720p, so even a modest server can transcode several channels simultaneously without breaking a sweat.

If you're serving live TV to multiple screens, make sure hardware acceleration is enabled in whatever frontend you choose — software transcoding live streams will peg your CPU.

---

## The Complete Stack at a Glance

Here's how the pieces fit together:

```
┌──────────────────────────────────────────────────┐
│              YOUR SCREENS (TV / Web / Mobile)     │
│    Jellyfin app  |  VodMax client  |  VLC/IPTVnator│
└─────────────────────┬────────────────────────────┘
                      │
┌─────────────────────▼────────────────────────────┐
│          FRONTEND (pick one or run both)          │
│   Jellyfin (Live TV + IPTV plugin + DVR)          │
│   VodMax (live-TV-first media center)             │
└──────┬─────────────────────────────┬──────────────┘
       │                             │
┌──────▼──────────┐        ┌─────────▼──────────────┐
│   PROXY LAYER   │        │   YOUR OWN "CHANNELS"  │
│   xTeVe (mux)   │        │   WBTV (library→TV)    │
│   dedupe/filter │        │   generates M3U+EPG    │
└──────┬──────────┘        └─────────┬──────────────┘
       │                             │
┌──────▼─────────────────────────────▼──────────────┐
│              SOURCES (all free & legal)            │
│   iptv-org free lists  |  FTA broadcasters        │
│   iptv-org EPG        |  WebGrab+Plus EPG         │
│   Local antenna/HDHomeRun |  Your own media       │
└───────────────────────────────────────────────────┘
```

---

## A Minimal Getting-Started Path

If you want to be watching a legal channel grid in under 30 minutes:

```bash
# 1. Jellyfin (if you don't already have it)
docker run -d \
  --name=jellyfin \
  -v /path/to/jellyfin/config:/config \
  -v /path/to/media:/media \
  -p 8096:8096 \
  jellyfin/jellyfin:latest

# 2. xTeVe as the proxy/muxer
docker run -d \
  --name=xteve \
  -v /path/to/xteve/config:/config \
  -p 34400:34400 \
  alturismo/xteve

# 3. (Optional) WBTV to make channels from your own library
#    → generates an M3U you feed into xTeVe
```

Then, in the Jellyfin dashboard:

1. Install the **IPTV plugin**
2. **Live TV → Add Tuner → M3U Tuner**
3. URL: `http://xteve:34400/xteve.m3u`
4. EPG: `http://xteve:34400/xteve.xml`
5. Refresh the guide and start flipping channels

Add an iptv-org free list as your source in xTeVe, map the iptv-org EPG, and you'll have a real, working, *legal* channel grid — no sketchy box, no gray-market subscription.

---

## Why This Matters

The self-hosting community spent a decade perfecting the on-demand pipeline. Movies, shows, music, books, photos — all solved, all better than the commercial alternatives. Live TV was the one format that still made people keep a cable box or a streaming subscription "just in case."

It doesn't have to anymore. M3U is an open format. XMLTV is an open format. The tools are open-source, the free sources are legal, and your hardware can already do the transcoding. The only thing missing was someone connecting the dots — and now the dots are connected.

**The bottom line:** You already self-host your movies. Now self-host the channel guide. It's the last piece of the media puzzle, and it's easier than you think.

---

*Got a live-TV setup you're proud of? Building your own "channels" with WBTV? Find me on [GitHub](https://github.com/Bryanmoon19) or drop a comment below.*
