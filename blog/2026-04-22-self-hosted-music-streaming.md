---
layout: post.njk
title: "Own Your Music: The Complete Self-Hosted Streaming Setup for 2026"
date: 2026-04-22
description: "Ditch Spotify and Apple Music for good. Build your own music streaming server with Plex Amp, Navidrome, or Jellyfin — and keep your library forever."
tags: ["self-hosted", "music", "plex", "navidrome", "jellyfin", "streaming", "homelab", "docker", "privacy"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-music-streaming-2026"
---

Spotify just raised prices again. Your "liked songs" playlist is buried under three new UI redesigns. And that album you saved last year? Gone — pulled by a licensing dispute you never heard about.

This isn't a bug. It's the business model. You don't own anything on streaming services. You're renting access to a catalog that shrinks, shifts, and disappears based on contracts you'll never see.

The alternative isn't buying CDs or dusting off an iPod (though you can). It's running your own music server — a Spotify replacement that lives on your hardware, streams to any device, and keeps your library intact for as long as you want.

I've been self-hosting music for three years. My server holds 12,000 tracks, syncs to my phone, streams in my car via CarPlay, and costs nothing beyond the electricity to run a single container. This guide covers the complete stack: server setup, library management, streaming clients, and the workflow for actually discovering new music without an algorithm doing it for you.

## What You're Building

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Your Phone    │◄────│   Plex Amp /    │◄────│  Your Music     │
│   (CarPlay)     │     │   Navidrome     │     │  Library        │
├─────────────────┤     │   (Docker)      │     │  (NAS/Local)    │
│   Laptop        │◄────├─────────────────┤     └─────────────────┘
├─────────────────┤     │   Reverse Proxy │            │
│   Work Desktop  │◄────│   (SSL + Auth)  │◄───────────┘
└─────────────────┘     └─────────────────┘
```

Three components:
- **Music library** stored locally (NAS, server drive, or external storage)
- **Streaming server** (Plex, Navidrome, or Jellyfin) to serve it
- **Clients** on every device for playback and offline sync

Total time to set up: about an hour. Total cost: $0 if you already have a server.

## Step 1: Choose Your Streaming Server

Three options dominate self-hosted music. Each has tradeoffs:

| Feature | Plex Amp | Navidrome | Jellyfin |
|---------|----------|-----------|----------|
| **Cost** | Free (core), Plex Pass for offline/lyrics ($120 lifetime) | Completely free | Completely free |
| **Client polish** | Excellent (dedicated music app) | Good (web + Subsonic apps) | Good (Finamp on mobile) |
| **CarPlay/Android Auto** | ✅ Native | ✅ via apps (DSub, Ultrasonic) | ⚠️ Finamp beta |
| **Offline sync** | ✅ Plex Pass | ✅ Most apps support | ✅ Finamp |
| **Resource usage** | Medium | Very low (~50MB RAM) | Medium |
| **Setup complexity** | Low | Very low | Low |
| **Music-only focus** | ✅ Yes | ✅ Yes | ❌ General media |

**My recommendation:** Start with Navidrome if you want dead-simple and free. Upgrade to Plex Amp if you want the most polished experience and don't mind the one-time Plex Pass cost for offline downloads and lyrics. Use Jellyfin if you already run it for movies/TV and want one app for everything.

This guide covers Navidrome (free, lightweight, straightforward) with notes on Plex Amp for those who want the premium experience.

## Step 2: Prepare Your Music Library

Before you stream anything, you need music files. Here are your options:

### Sources

**CD ripping** — The classic approach. Buy used CDs for $2-5, rip to FLAC with Exact Audio Copy (Windows) or XLD (Mac). You own the files forever. Storage cost: ~300-500MB per album in FLAC.

**Bandcamp** — Many artists sell DRM-free downloads directly. Often available in FLAC, MP3 320, or WAV. The artist gets a better cut than streaming.

**Amazon Music purchases** — Buying a physical CD or vinyl on Amazon often includes a free AutoRip digital copy in your Amazon Music library. These are DRM-free MP3s you can download.

**Beatport / JunoDownload** — Electronic music-focused stores with high-quality downloads.

**Qobuz Store** — Lossless downloads from a streaming service that also sells files outright.

### What About My Streaming Playlists?

Services like [TuneMyMusic](https://www.tunemymusic.com) or [Soundiiz](https://soundiiz.com) can export your Spotify/Apple Music playlists to CSV. This gives you a structured list of what to acquire — but not the files themselves. Consider it a migration checklist, not a direct transfer.

### File Organization

Your streaming server expects a clean folder structure. The standard convention:

```
/music
  /Artist Name
    /[Year] Album Name
      01 - Track Title.flac
      02 - Track Title.flac
      cover.jpg
```

Tools like [MusicBrainz Picard](https://picard.musicbrainz.org) or [Beets](https://beets.io) can automatically tag, rename, and organize messy downloads into this structure. Highly recommended if your library is a pile of files with names like `Track_01(1).mp3`.

### Format Notes

| Format | Quality | Size/Album | Best For |
|--------|---------|------------|----------|
| **FLAC** | Lossless | ~300-500MB | Archival, home listening |
| **MP3 320** | Near-transparent | ~80-120MB | Mobile, large libraries |
| **MP3 V0** | Variable, ~245kbps | ~70-100MB | Good compromise |

Rule of thumb: Keep FLAC masters on your server, let your client transcode for mobile if bandwidth matters. Navidrome and Plex both handle transcoding automatically.

## Step 3: Deploy Navidrome with Docker

Navidrome is a lightweight Subsonic-compatible music server written in Go. It scans your library, serves a web UI, and exposes the Subsonic API — meaning any Subsonic client app can connect to it.

### Docker Compose

```yaml
# docker-compose.yml
services:
  navidrome:
    image: deluan/navidrome:latest
    container_name: navidrome
    restart: unless-stopped
    ports:
      - "4533:4533"
    volumes:
      - "./data:/data"
      - "/mnt/music:/music:ro"
    environment:
      ND_SCANSCHEDULE: "1h"
      ND_LOGLEVEL: "info"
      ND_BASEURL: ""
```

Key details:
- `/mnt/music:/music:ro` — Mount your music library read-only. Adjust the host path to wherever your files live.
- `ND_SCANSCHEDULE: 1h` — Automatically scan for new music every hour.
- Port `4533` — Navidrome's default web UI.

Deploy:
```bash
docker compose up -d
```

First run creates an admin user. Check logs for the auto-generated password:
```bash
docker logs navidrome
```

Log in at `http://your-server:4533`, change the password immediately, and let the initial scan complete. For a few thousand tracks, this takes 5-15 minutes.

### Reverse Proxy (Optional but Recommended)

If you want HTTPS and external access, put Navidrome behind your reverse proxy (Nginx Proxy Manager, Traefik, Caddy, etc.).

**Nginx Proxy Manager example:**
- Scheme: `http`
- Forward hostname: `navidrome`
- Forward port: `4533`
- Enable `Block Common Exploits`
- Request a new SSL certificate

For external streaming, you'll want this — it protects your login and lets you stream over HTTPS from anywhere.

## Step 4: Connect Your Clients

Navidrome exposes the Subsonic API, so any Subsonic-compatible app works.

### Mobile

| App | Platform | Cost | Notes |
|-----|----------|------|-------|
| **Ultrasonic** | Android | Free | Lightweight, no nonsense |
| **DSub** | Android | Free | Feature-rich, offline sync |
| **Substreamer** | iOS/Android | Free | Modern UI, CarPlay support |
| **play:Sub** | iOS | $5 | Excellent iOS integration |

Setup is the same across apps:
1. Add server URL: `https://music.yourdomain.com` (or `http://local-ip:4533` for LAN-only)
2. Username: your Navidrome admin (or create users in Settings)
3. Password: your Navidrome password
4. Server type: Subsonic / Generic

### Desktop

- **Web UI**: `https://music.yourdomain.com` — full-featured, no install needed
- **Sublime Music** (Linux): Native Subsonic client
- **Sonixd** (Windows/Mac/Linux): Modern desktop client
- **Feishin** (all platforms): Beautiful, feature-rich

### CarPlay / Android Auto

Substreamer (iOS) and DSub (Android) both support in-car playback. The experience isn't quite as polished as Spotify's native app, but it's functional: browse albums, play playlists, and control playback through the car's interface.

## Step 5: The Plex Amp Alternative

If you want the most polished self-hosted music experience — and don't mind a one-time cost — Plex Amp is the gold standard.

### Why Plex Amp?

- **Native CarPlay/Android Auto** — First-class in-car experience
- **Offline downloads** — Download albums/playlists for plane rides or dead zones
- **Lyrics display** — Real-time synced lyrics
- **Automatic mixes** — "Time Travel Mix," "Artist Mix," "Mood Mix" generated from your library
- **Sonic analysis** — "Behind the Lyrics"-style track info and recommendations
- **Gorgeous UI** — Album art, artist bios, "Popular Tracks" from your library

The catch: offline downloads and lyrics require Plex Pass ($120 lifetime, or ~$5/month). Everything else is free.

### Setup

```yaml
# docker-compose.yml
services:
  plex:
    image: plexinc/pms-docker:latest
    container_name: plex
    restart: unless-stopped
    ports:
      - "32400:32400"
    environment:
      PLEX_CLAIM: "claim-TOKEN_HERE"  # Get from https://plex.tv/claim
      TZ: "America/New_York"
    volumes:
      - "./config:/config"
      - "/mnt/music:/music:ro"
```

Claim your server at [plex.tv/claim](https://www.plex.tv/claim/), paste the token, and deploy. Add a Music library pointed at `/music`, let it scan, then install Plex Amp on your phone.

### Plex Pass Decision Tree

- **Free tier**: Stream your entire library, browse by artist/album/genre, basic playlists
- **Plex Pass adds**: Offline downloads, lyrics, loudness leveling, hardware transcoding, skip intros

If you listen to music mostly at home on Wi-Fi, free is fine. If you commute, travel, or want the full premium experience, the lifetime pass pays for itself in under two years compared to Spotify.

## Step 6: Discovery Without Spotify's Algorithm

The hardest part of leaving streaming isn't hosting — it's finding new music. Spotify's recommendation engine is genuinely good. Here's how to replicate it:

### Curated Sources

- **RateYourMusic charts** — Community-ranked best albums by year, genre, decade
- **Album of the Year** — Aggregated reviews from critics across publications
- **r/letstalkmusic** — Deep-dive discussions, weekly recommendation threads
- **Spotify's "Discover Weekly"** — Use it as a discovery tool, then buy what you like
- **Bandcamp Daily** — Editor-curated features, genre deep-dives, and emerging artists

### Build Your Own Algorithm

Create a system:
1. **Discovery day** (weekly): Spend 30 minutes on RateYourMusic, Bandcamp, or Spotify's free tier. Save interesting albums to a note.
2. **Acquisition**: Buy 1-2 albums per week. Build your library intentionally.
3. **Listen**: Actually listen to full albums. Not playlists. Not shuffled background noise.
4. **Log**: Use [Last.fm](https://last.fm) (still free!) to track scrobbles and find patterns in what you actually enjoy.

After six months, you'll have a library that reflects your taste — not an algorithm's guess.

### Smart Playlists

Both Navidrome and Plex support smart playlists:
- "Recently Added" — Auto-populated with new acquisitions
- "Never Played" — Rotate through your backlog
- "Top Rated" — Surface your 5-star tracks
- "By Decade/Genre" — Organized browsing

These replace Spotify's "Daily Mix" with something more personal.

## Step 7: Backup Your Library

You went through the effort of building this. Don't lose it.

**3-2-1 for music:**
- **3 copies**: Your active library + local backup + cloud backup
- **2 media**: Server/NAS + external drive or cloud
- **1 offsite**: Backblaze B2, Wasabi, or even a hard drive at a friend's house

Tools:
- `rsync` for local sync: `rsync -av /mnt/music /mnt/backup/music`
- [rclone](https://rclone.org) for cloud: `rclone sync /mnt/music remote:bucket`
- [BorgBackup](https://borgbackup.org) for versioned, deduplicated backups

Your music library is likely 100GB-1TB+. Cloud storage costs ~$6/TB/month. Budget for it.

## FAQ

**Is this legal?**
Yes, if you own the files. Rip your own CDs, buy from Bandcamp/Amazon, or download from artist-direct stores. The server itself is just software — what you put on it determines legality.

**How much storage do I need?**
Rule of thumb: ~300-500MB per album in FLAC, ~100MB in MP3 320. A 1,000-album library is roughly 300-500GB in FLAC.

**Can I share with family?**
Yes — Navidrome supports multiple users with their own playlists and play history. Plex does too, and Plex Pass extends sharing to outside your home network.

**What about podcasts/audiobooks?**
Navidrome is music-focused. For podcasts, use [FreshRSS](https://freshrss.org) + a podcast client. For audiobooks, [Audiobookshelf](https://audiobookshelf.org) is purpose-built and excellent.

**Will this work without internet?**
LAN streaming works without internet. For external access, you need your reverse proxy or VPN (WireGuard, Tailscale) to be accessible.

## The Bottom Line

Self-hosted music isn't about nostalgia or being anti-streaming. It's about ownership, quality, and intentionality. You decide what goes in your library. You decide how it's organized. You decide when something stays or goes.

Spotify optimized for convenience. Self-hosting optimizes for control. Both are valid — but after three years of owning my music, I can't imagine going back to renting it.

Start small. Pick one server (Navidrome), add one album, connect one client. Build from there. Your future self — the one listening to an album ten years from now that Spotify delisted in 2028 — will thank you.

---

*Questions? Find me in the [Discord](https://discord.gg/devhandbook) or drop a comment below. And if you found this useful, share it with someone who's complained about Spotify's UI lately.*