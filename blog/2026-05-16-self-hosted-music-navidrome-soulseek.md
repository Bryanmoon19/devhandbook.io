---
layout: post.njk
title: "Own Every Track: Self-Hosted Music with Navidrome, Soulseek \u0026 Slskd"
date: 2026-05-16
description: "Build a complete self-hosted music discovery and streaming pipeline. Download with Soulseek/slskd, manage with Lidarr, stream with Navidrome — all on your own hardware."
tags: ["self-hosted", "music", "navidrome", "soulseek", "slskd", "lidarr", "streaming", "homelab", "docker", "privacy"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/self-hosted-music-navidrome-soulseek-slskd"
---

Spotify raised prices again. That album you had saved? Region-locked last month. Your "Discover Weekly" is half ads for podcasts you never asked for. And the artist payout? $0.003 per stream. The math doesn't work for anyone except the platform.

There's another way. A way where you own the files, control the catalog, and discover music through a community that's been sharing tracks since 2001. Soulseek — the original peer-to-peer music network — still runs today. Pair it with a modern streaming server like Navidrome, and you get a Spotify replacement where every byte lives on hardware you control.

I've been running this stack for two years. My library sits at 15,000 tracks, grows every week, and costs nothing beyond the electricity to keep a few containers running. This guide covers the complete pipeline: discovery with Soulseek, automation with slskd and Lidarr, and streaming with Navidrome to every device you own.

## What You're Building

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Soulseek      │     │   Lidarr        │     │   Navidrome     │
│   Network       │────▶│   (Management)  │────▶│   (Streaming)   │
│   (slskd)       │     │   + slskd       │     │   (Docker)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
   Downloads              Organized Library         Your Phone
   (NAS/Local)            (/music)                 CarPlay/Web
```

Four components:
- **slskd** — Soulseek client running headless in Docker, handles all downloads
- **Lidarr** — Music management: monitors artists, grabs albums, renames and tags files
- **Navidrome** — Streaming server, Subsonic-compatible, serves to any client
- **Clients** — Web UI, DSub (Android), Ultrasonic, or any Subsonic app

Total time to set up: about 45 minutes. Total cost: $0.

## Step 1: slskd — The Soulseek Daemon

Soulseek is a peer-to-peer file sharing network built specifically for music. Unlike BitTorrent, it's designed around conversations, wishlists, and direct user-to-user sharing. slskd is a modern, headless Soulseek client that runs in Docker and exposes a clean web UI.

### Docker Compose

```yaml
services:
  slskd:
    image: slskd/slskd:latest
    container_name: slskd
    ports:
      - "5030:5030"
    volumes:
      - ./slskd:/app/data
      - /mnt/nas/music/downloads:/downloads
    environment:
      - SLSKD_REMOTE_CONFIGURATION=true
    restart: unless-stopped
```

### Key Configuration

After first start, edit `data/slskd.yml`:

```yaml
soulseek:
  username: your_username
  password: your_password
  listen_port: 50300
  description: "Homelab share | slskd"

directories:
  downloads: /downloads
  incomplete: /downloads/.incomplete

shares:
  directories:
    - /mnt/nas/music/library
  filters:
    - \.ini$
    - Thumbs\.db$
    - \.DS_Store$

web:
  port: 5030
  authentication:
    disabled: false
    username: admin
    password: your_secure_password

logging:
  level: Information
```

**Port forwarding:** Soulseek requires an open listening port for searches and downloads to work properly. Forward TCP port 50300 on your router to your slskd host. Without this, you'll only be able to download from users who can connect to you — severely limiting results.

**Account creation:** If you don't have a Soulseek account, register at `https://www.slsknet.org/news/node/682`. Pick a username and use it in the config. The network is small enough that reputation matters — share what you download, and the community reciprocates.

## Step 2: Lidarr — Automated Music Management

Lidarr is the *arr equivalent for music. It monitors artists, tracks album releases, and can automate downloads through slskd. While Lidarr doesn't have native Soulseek support, the slskd integration works through a custom script approach or manual grabbing.

### Docker Compose (Add to Stack)

```yaml
  lidarr:
    image: lscr.io/linuxserver/lidarr:latest
    container_name: lidarr
    ports:
      - "8686:8686"
    volumes:
      - ./lidarr:/config
      - /mnt/nas/music:/music
      - /mnt/nas/music/downloads:/downloads
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    restart: unless-stopped
```

### Folder Structure

Lidarr and Navidrome both expect a standard music folder layout:

```
/music
  /Artist Name
    /[Year] Album Name [Format]
      01 - Track Title.flac
      02 - Track Title.flac
      cover.jpg
```

**Critical:** Set Lidarr's root folder to `/music` and its download client folder to `/downloads`. After Lidarr processes a download, it renames, tags, and moves files to the organized library path.

### slskd + Lidarr Workflow

Since Lidarr doesn't natively support Soulseek, the typical workflow is:

1. **Lidarr monitors** artists and flags wanted albums
2. **Manual or scripted search** in slskd web UI using the wishlist feature
3. **slskd downloads** to `/downloads`
4. **Lidarr import** scans `/downloads`, processes files, moves to `/music`
5. **Navidrome rescans** and the album appears in your library

For a more automated approach, community tools like [soularr](https://github.com/mrusse/soularr) bridge Lidarr and slskd. It reads Lidarr's wanted list and automatically searches Soulseek:

```yaml
  soularr:
    image: mrusse/soularr:latest
    container_name: soularr
    volumes:
      - ./soularr:/data
      - /mnt/nas/music/downloads:/downloads
    environment:
      - LIDARR_URL=http://lidarr:8686
      - LIDARR_API_KEY=your_api_key
      - SLSKD_URL=http://slskd:5030
      - SLSKD_API_KEY=your_slskd_api_key
    restart: unless-stopped
```

## Step 3: Navidrome — Your Streaming Server

Navidrome is a Subsonic-compatible music server that's fast, lightweight, and dead simple. It indexes your library, serves a web player, and works with any Subsonic client.

### Docker Compose (Add to Stack)

```yaml
  navidrome:
    image: deluan/navidrome:latest
    container_name: navidrome
    ports:
      - "4533:4533"
    volumes:
      - ./navidrome:/data
      - /mnt/nas/music:/music:ro
    environment:
      - ND_SCANSCHEDULE=1h
      - ND_LOGLEVEL=info
      - ND_BASEURL=
    restart: unless-stopped
```

**Why read-only (`:ro`):** Navidrome never needs to write to your music folder. Mounting it read-only prevents any accidental file changes. All Navidrome data (database, cache, settings) lives in `./navidrome`.

### Initial Setup

1. Open `http://your-server:4533`
2. Create the first admin account
3. Navidrome will scan `/music` automatically
4. For large libraries (10,000+ tracks), the first scan takes 5-15 minutes

### Transcoding Settings

Navidrome can transcode on the fly for mobile streaming. Default settings work for most, but if you're streaming to mobile over cellular, configure Opus or MP3 transcoding:

In the web UI: **Admin → Players → [Your Player] → Transcoding**

Recommended for mobile:
- **Format:** opus
- **Bitrate:** 128
- **Result:** ~40% smaller than MP3 320, transparent quality

## Step 4: The Complete Docker Compose Stack

Here's everything wired together:

```yaml
version: "3.8"

services:
  slskd:
    image: slskd/slskd:latest
    container_name: slskd
    ports:
      - "5030:5030"
      - "50300:50300"
    volumes:
      - ./slskd:/app/data
      - /mnt/nas/music/downloads:/downloads
    environment:
      - SLSKD_REMOTE_CONFIGURATION=true
    restart: unless-stopped

  lidarr:
    image: lscr.io/linuxserver/lidarr:latest
    container_name: lidarr
    ports:
      - "8686:8686"
    volumes:
      - ./lidarr:/config
      - /mnt/nas/music:/music
      - /mnt/nas/music/downloads:/downloads
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    restart: unless-stopped

  navidrome:
    image: deluan/navidrome:latest
    container_name: navidrome
    ports:
      - "4533:4533"
    volumes:
      - ./navidrome:/data
      - /mnt/nas/music:/music:ro
    environment:
      - ND_SCANSCHEDULE=1h
      - ND_LOGLEVEL=info
      - ND_BASEURL=
    restart: unless-stopped

  # Optional: soularr for automated Soulseek searching
  # soularr:
  #   image: mrusse/soularr:latest
  #   container_name: soularr
  #   volumes:
  #     - ./soularr:/data
  #     - /mnt/nas/music/downloads:/downloads
  #   environment:
  #     - LIDARR_URL=http://lidarr:8686
  #     - LIDARR_API_KEY=your_key
  #     - SLSKD_URL=http://slskd:5030
  #     - SLSKD_API_KEY=your_key
  #   restart: unless-stopped
```

## Step 5: Client Setup — Stream Anywhere

Navidrome speaks the Subsonic API, which means almost any music client works. Here are the best options by platform:

### Web (Any Device)
Navidrome's built-in web player is excellent. It supports playlists, gapless playback, and the full library view. Just open your server URL in a browser.

### Android
- **DSub** — The classic Subsonic client. Stable, full-featured, offline sync. Free on F-Droid, paid on Play Store.
- **Ultrasonic** — Fork of DSub with modern UI. Free, open-source.
- **Subtracks** — Minimal, fast, Material Design. Good for clean library browsing.

**Setup:** Server URL = `http://your-server:4533`, username/password = your Navidrome credentials.

### iOS
- **play:Sub** — The best iOS Subsonic client. Clean UI, CarPlay support, offline sync. One-time purchase (~$5).
- **Substreamer** — Free with ads, subscription to remove. Good for testing before buying play:Sub.

### Desktop
- **Sublime Music** (Linux) — GTK client with album art and playlist support.
- **Sonixd** (Windows/Linux/macOS) — Modern Electron client, very polished.
- **Web player** — Works great in any browser.

### CarPlay / Android Auto
- **play:Sub** (iOS) — Native CarPlay support
- **DSub / Ultrasonic** (Android) — Android Auto compatible

## Step 6: Discovery Workflow

The biggest question people ask: "How do I find new music without Spotify's algorithm?"

### Soulseek Discovery
- **User browsing:** Right-click any user → "Browse shares." See their full library. If someone has 5 albums you love, they probably have 50 more you'll like.
- **Room chat:** Join genre-specific rooms. Ask for recommendations. The community is small but knowledgeable.
- **Wishlist:** Add searches to your wishlist. slskd will notify when someone has what you're looking for.

### Lidarr Monitoring
- Add artists you already love
- Lidarr tracks new releases automatically
- Use the "Monitor" toggle for specific albums or "Future" to catch everything

### External Discovery
- **RateYourMusic** — Comprehensive user-generated ratings and lists. Export lists and search manually in slskd.
- **Last.fm** — Still works for scrobbling from Navidrome. Your listening history builds a taste profile.
- **Bandcamp** — Buy directly from artists, download FLAC, drop into your library. No DRM, ever.

## Step 7: Reverse Proxy \u0026 SSL

Don't expose these services directly. Use a reverse proxy with SSL:

```yaml
  nginx:
    image: nginx:alpine
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    restart: unless-stopped
```

Or use **Nginx Proxy Manager** (if you already run it) with these subdomains:
- `music.yourdomain.com` → Navidrome (4533)
- `slsk.yourdomain.com` → slskd (5030)
- `lidarr.yourdomain.com` → Lidarr (8686)

## File Organization Tips

A clean library is everything. Here's my workflow:

1. **slskd downloads** to `/downloads` with original filenames
2. **Lidarr renames** using the format: `{Artist}/{Album} ({Year})/{track:00} - {Title}`
3. **Beets** (optional but recommended) for extra tagging:
   ```bash
   beet import /downloads
   ```
   Beets uses MusicBrainz to verify tags, fetch album art, and fix metadata.

4. **Navidrome rescans** every hour automatically

## Backups

Your library is irreplaceable. Back it up:

```bash
# Rsync to external drive or secondary NAS
rsync -avP /mnt/nas/music/ /mnt/backup/music/

# Or use rclone to cloud storage
rclone sync /mnt/nas/music remote:backup/music
```

Priority backup order:
1. The music files themselves (largest, most irreplaceable)
2. Lidarr config (`./lidarr` — artist lists, wanted albums)
3. slskd config (`./slskd` — shares, chat history)
4. Navidrome database (`./navidrome/navidrome.db` — playlists, ratings, play counts)

## Troubleshooting

**"No search results in slskd"**
→ Check port forwarding on 50300. Test with a port checker. Without an open port, Soulseek works in limited mode.

**"Lidarr won't import downloads"**
→ Check permissions. Lidarr runs as PUID/PGID. Ensure `/downloads` and `/music` are writable by that user. Check Lidarr's logs for "Import failed" messages.

**"Navidrome shows empty library"**
→ Verify the mount path. If Navidrome sees `/music` but it's empty, the Docker volume mount is wrong. Check with `docker exec navidrome ls /music`.

**"Some files won't play"**
→ Check format support. Navidrome supports FLAC, MP3, Ogg, Opus, AAC, and WMA. Very old or exotic formats (APE, TTA) may need conversion.

## The Bottom Line

This stack replaces every streaming service you pay for. The upfront setup takes an evening. The ongoing cost is the electricity to run three containers — roughly $2-4 per month on a modern server.

What you get:
- **Permanent ownership** of every file
- **No DRM, no region locks, no disappearing albums**
- **Community discovery** through Soulseek's user-driven network
- **Automated management** via Lidarr
- **Stream anywhere** via Navidrome and Subsonic clients
- **No monthly subscription** beyond your hardware

The tradeoff is curation over convenience. You'll spend more time finding music than Spotify's algorithm would spend serving it to you. But you'll find music the algorithm never would have shown you — and you'll own it forever.

Start with Navidrome and a small test library. Add slskd when you're ready to grow. Wire in Lidarr when manual management gets tedious. This is a stack that scales with your commitment.

---

*Got questions? The [self-hosted music thread on r/selfhosted](https://reddit.com/r/selfhosted) and the [Navidrome Discord](https://discord.gg/xh7j7yF) are active communities running similar setups.*
