---
title: "Self-Hosted Audiobookshelf: The Complete 2026 Guide to Owning Your Audiobooks"
description: "A comprehensive guide to setting up Audiobookshelf — the open-source audiobook and podcast server that replaces Audible. Docker Compose, Proxmox LXC, mobile apps, reverse proxy, and VPN setup."
date: 2026-04-23
author: Bryan Moon
draft: true
tags:
  - self-hosting
  - audiobooks
  - audiobookshelf
  - docker
  - proxmox
  - audible-alternative
  - homelab
---

# Self-Hosted Audiobookshelf: The Complete 2026 Guide to Owning Your Audiobooks

## 1. Introduction: Why I Left Audible

I remember the exact moment I decided to build my own audiobook server. My wife tapped the Audible app on her phone, and instead of her library, she got a spinning loading icon that never stopped. Reinstall the app? Still spinning. Log out and back in? Still spinning. Search Google for answers? Pages of other people with the same problem, and nothing but silence from Amazon.

This was the moment that pushed me over the edge. It wasn't just about one broken app — it was about the realization that I didn't actually own anything in that library. Thousands of dollars spent on audiobooks, and Amazon could make them disappear (or at least inaccessible) with a single broken update.

This story isn't unique to me. Ars Technica's Lee Hutchinson [published a piece in March 2025](https://arstechnica.com/gadgets/2025/03/i-threw-away-audibles-app-and-now-i-self-host-my-audiobooks/) that went viral in the self-hosting community for exactly this reason. His wife's Audible app stopped working, and after the usual troubleshooting rituals failed, he "changed tacks and fixed the problem, permanently, with Audiobookshelf." That resonated with me because it was the same path I was already walking.

The bigger problem here is platform lock-in and DRM. When you "buy" an audiobook from Audible, you're really buying a license to access it through their app, under their terms, as long as they feel like keeping the service running. The files are wrapped in DRM that prevents you from moving them elsewhere. If the app breaks, your library breaks with it.

The solution is to take ownership back. Enter **Audiobookshelf** — an open-source, self-hosted audiobook and podcast server that puts you in control of your media. You own the files. You run the server. You decide how to access it.

This guide covers everything I've learned from setting up and running Audiobookshelf in my own homelab: Docker Compose setup, library organization, Proxmox LXC deployment, mobile app configuration, reverse proxy setup, VPN access, and the honest DRM conversation that nobody wants to have but everybody needs to hear.

Let's build something you actually own.

---

## 2. What Is Audiobookshelf?

[Audiobookshelf](https://github.com/advplyr/audiobookshelf) is an open-source audiobook and podcast server with over 12,000 GitHub stars and an active community. Think of it as **Plex for audiobooks**, except it's actually designed for audiobooks instead of being a video platform awkwardly repurposed for audio.

### Key Features

- **Multi-user support**: Create separate accounts for family members with their own libraries, progress, and bookmarks.
- **Progress sync**: Your listening position syncs across devices. Start a book on your phone during your commute, pick up exactly where you left off on your desktop at home.
- **Metadata fetching**: Automatically pulls in cover art, author info, series data, and descriptions from sources like Audnexus (Audible metadata), Google Books, and OpenLibrary.
- **Podcast support**: Subscribe to RSS feeds, auto-download new episodes, and even generate open RSS feeds for sharing your own content.
- **Offline mobile apps**: Download books to your phone for plane rides, road trips through dead zones, or anywhere without reliable internet.
- **Web player**: A clean, functional web interface that works on any device with a browser.
- **Library statistics**: Track listening time, books completed, and other nerdy metrics that homelab people love.

### Hardware Requirements

Here's the beautiful thing about Audiobookshelf: it runs on almost anything.

- **RAM**: ~150MB at idle (I run mine in a Proxmox LXC with 512MB allocated and never hit the limit)
- **CPU**: Nearly anything modern will handle it. The server is lightweight. The only time you'll see CPU spikes is during bulk library scanning or metadata matching.
- **Storage**: Depends entirely on your library. A single audiobook ranges from 200MB to 2GB+. Plan accordingly. I store mine on a NAS and mount it into the container.
- **Network**: Wired Ethernet is ideal, but Wi-Fi works fine for home use. If you're streaming remotely, your upload bandwidth becomes the bottleneck.

I run mine on a Proxmox LXC container with 1 CPU core, 512MB RAM, and 20GB disk space (for the application and metadata). The actual audiobook files live on a Synology NAS mounted via NFS. This is a perfect example of how lightweight the server really is.

---

## 3. Prerequisites

Before we dive into the setup, make sure you have:

1. **Docker and Docker Compose installed** on your target machine (or a willingness to run bare metal, though Docker is strongly recommended for ease of updates and isolation).
2. **A directory for your audiobooks** — this could be local storage, a NAS share (SMB/CIFS or NFS), or even an external drive. Just make sure it's accessible from the machine running Audiobookshelf.
3. **A reverse proxy** (optional but highly recommended) — we'll cover Nginx Proxy Manager and Traefik setups later.
4. **A VPN solution** for remote access — WireGuard is my recommendation, but Tailscale and ZeroTier are excellent zero-config alternatives.
5. **DRM-free audiobook files** — we'll discuss sourcing these in Section 12.

---

## 4. Docker Compose Setup

Docker is the easiest and most maintainable way to run Audiobookshelf. Updates are a single `docker compose pull && up -d` away, and you get clean isolation from your host system.

### Basic Docker Compose File

Create a `docker-compose.yml` file in your preferred directory (I use `~/docker/audiobookshelf/`):

```yaml
services:
  audiobookshelf:
    image: ghcr.io/advplyr/audiobookshelf:latest
    container_name: audiobookshelf
    ports:
      - "13378:80"
    volumes:
      # Main audiobook library
      - /path/to/audiobooks:/audiobooks
      # Podcast library (optional)
      - /path/to/podcasts:/podcasts
      # Configuration and database
      - /path/to/config:/config
      # Metadata cache (covers, etc.)
      - /path/to/metadata:/metadata
    environment:
      - TZ=America/New_York
      # Optional: Set a default user for auto-login (not recommended for multi-user)
      # - AUDIOBOOKSHELF_UID=1000
      # - AUDIOBOOKSHELF_GID=1000
    restart: unless-stopped
    # Optional: Resource limits for shared hosts
    # deploy:
    #   resources:
    #     limits:
    #       memory: 1G
```

### Directory Structure Explained

| Volume | Container Path | Purpose |
|--------|---------------|---------|
| Audiobooks | `/audiobooks` | Your main book library |
| Podcasts | `/podcasts` | Podcast episodes and RSS feeds |
| Config | `/config` | Server config, user data, database |
| Metadata | `/metadata` | Downloaded cover art, cached search results |

**Important**: The config and metadata directories are critical. Back these up regularly. Your actual audiobook files can be re-scanned if lost, but your listening progress, bookmarks, and library settings live in `/config`.

### Starting the Container

```bash
cd ~/docker/audiobookshelf
docker compose up -d
```

The server will be available at `http://your-server-ip:13378` within seconds.

### Proxmox LXC Deployment Tips

Since I run mine in a Proxmox LXC container, here are the practical details I've learned:

**1. Enable nesting for Docker**

If you're running Docker inside an LXC (which I recommend for isolation), you must enable the `nesting=1` feature. Without this, Docker will fail with confusing errors about cgroups and namespaces.

```bash
# On the Proxmox host, edit the container config
nano /etc/pve/lxc/<VMID>.conf

# Add this line
features: nesting=1
```

Or via the Proxmox web UI: Container > Options > Features > Check "Nesting".

**2. Bind mount your NAS storage**

Don't store audiobooks inside the LXC's local disk — they'll fill up your container fast and make backups painful. Instead, bind mount from your NAS or host storage:

```bash
# In /etc/pve/lxc/<VMID>.conf
mp0: /mnt/nas/audiobooks,mp=/audiobooks
mp1: /mnt/nas/podcasts,mp=/podcasts
```

**3. Allow unprivileged container access to mounts**

If your LXC is unprivileged (the default and recommended setting), you'll need to map the host's user/group IDs so the container can read the mounted files:

```bash
# On the Proxmox host
# Add to /etc/subuid and /etc/subgid
root:100000:65536

# Then in /etc/pve/lxc/<VMID>.conf
lxc.idmap: u 0 100000 65536
lxc.idmap: g 0 100000 65536
```

Make sure the mounted files on your NAS are readable by the mapped UID. I use `uid=1000,gid=1000` in my NFS mount options to keep things simple.

**4. Container specs that work**

My current LXC for Audiobookshelf:
- **OS**: Ubuntu 24.04 LXC template
- **CPU**: 1 core (burstable to 2 during scans)
- **RAM**: 512MB (never exceeds 300MB in practice)
- **Disk**: 20GB (for OS + Docker + config/metadata)
- **Storage**: Audiobooks live on the NAS, mounted via bind mount

---

## 5. First Run & Library Setup

Once your container is running, open `http://your-server-ip:13378` in a browser.

### Initial Setup Wizard

1. **Create the root user**: The first account you create is the admin account. Save these credentials somewhere secure (I use my password manager).

2. **Create your first library**: You'll be prompted to create a library immediately. Choose between:
   - **Book** library: For audiobooks
   - **Podcast** library: For RSS-fed podcasts

3. **Set the library path**: Point it to `/audiobooks` (or whatever you named your volume in Docker Compose).

4. **Language and metadata settings**: Choose your preferred language. I leave metadata providers at their defaults (Audnexus + Google Books + OpenLibrary).

### Scanning Your Library

Once the library is created, Audiobookshelf will offer to scan for books. This is where your directory structure matters — which brings us to the next section.

---

## 6. Directory Structure Best Practices

Audiobookshelf is remarkably flexible about organization, but following consistent conventions will save you hours of manual metadata correction later.

### Recommended Structure

```
/audiobooks/
├── Author Name/
│   ├── Book Title/
│   │   ├── Book Title.mp3          (or .m4b, .ogg, etc.)
│   │   ├── Book Title - 01.mp3     (if split into parts)
│   │   ├── Book Title - 02.mp3
│   │   ├── cover.jpg               (optional, ABS will fetch if missing)
│   │   ├── desc.txt                (optional description)
│   │   └── reader.txt              (optional narrator info)
│   └── Another Book/
│       └── ...
├── Another Author/
│   ├── Series Name/
│   │   ├── 01 - Book One/
│   │   │   └── ...
│   │   └── 02 - Book Two/
│   │       └── ...
│   └── Standalone Book/
│       └── ...
└── ...
```

### File Naming Conventions

Audiobookshelf recognizes a few naming patterns:

- `Book Title.mp3` — Single-file book
- `Book Title - 01.mp3`, `Book Title - 02.mp3` — Multi-part books
- `01 - Chapter Name.mp3` — Chapter-based files

The server will automatically merge multi-part books into a single logical book in the library.

### Metadata Tags That Matter

If your files have embedded metadata tags, Audiobookshelf will use them:

| Tag | Purpose |
|-----|---------|
| `title` | Book title |
| `artist` | Author name |
| `album` | Series name (optional) |
| `albumartist` | Series author (if different) |
| `date` | Publication year |
| `description` | Book synopsis |
| `narrator` | Reader/narrator name |
| `genre` | Genre/category |

**Pro tip**: If your audiobooks came from Audible, they likely have good metadata tags already. If they came from CDs or other sources, you may need to tag them. I use [MusicBrainz Picard](https://picard.musicbrainz.org/) for bulk tagging, though it's designed for music — for audiobooks, I sometimes fall back to a simple Python script using `mutagen`.

### Optional Text Files

For books without embedded tags, you can add:

- `desc.txt` — A plain text description of the book
- `reader.txt` — The narrator's name

Place these in the same folder as the audio files, and Audiobookshelf will pick them up during scanning.

### Cover Art

Audiobookshelf will automatically fetch cover art from its metadata providers, but you can also provide your own:

- `cover.jpg` or `cover.png` in the book folder
- Embedded cover art in the audio files themselves

I prefer letting it fetch automatically — the Audnexus integration is excellent and usually finds the right cover on the first try.

---

## 7. Mobile Apps & Offline Listening

This is where Audiobookshelf really shines compared to a simple file server. The mobile apps are polished, support offline downloads, and sync progress across devices.

### Android: Official App

The official Audiobookshelf app is available on the [Google Play Store](https://play.google.com/store/apps/details?id=com.audiobookshelf.app). It's full-featured, actively maintained, and works exactly as you'd expect:

- Connect to your server by entering the URL
- Browse libraries and search
- Stream or download for offline listening
- Sleep timer, playback speed control, chapter navigation
- Progress syncs back to the server in real-time

### iOS: TestFlight Beta

The iOS official app is currently in beta and distributed via [TestFlight](https://testflight.apple.com/join/wiic7QI7). The link is publicly available and Apple-approved for testing. In my experience, it's stable enough for daily use — I've been running it for months without crashes.

Features match the Android app: streaming, downloads, sync, sleep timer, speed controls, the works.

**Note**: TestFlight apps have a 90-day renewal cycle. If you see a "Beta Has Expired" message, check the Audiobookshelf Discord or GitHub for an updated TestFlight link. This has happened to me once, and it was resolved within 24 hours.

### Third-Party Alternative: Plappa (iOS)

If the TestFlight process isn't your thing, or you want an alternative interface, [Plappa](https://apps.apple.com/us/app/plappa/id6474096622) is an excellent third-party client for Audiobookshelf on iOS.

Lee Hutchinson from Ars Technica uses Plappa as his daily driver and reports it as "more responsive and less prone to crashing than Apple's own Books app." I've tried it myself and can confirm — it's fast, the UI is clean, and it has one killer feature: **no in-app store page constantly trying to sell you something**. Just your books, your server, nothing else.

Plappa supports all the core features: streaming, downloads, progress sync, sleep timer, variable playback speed. If you're an iOS user and the TestFlight process feels like too much friction, Plappa is absolutely worth the (small) purchase price.

### Offline Sync Strategy

My personal workflow:

1. **At home on Wi-Fi**: Download the next 2-3 books I plan to read. This avoids any cellular data concerns.
2. **During commutes**: Stream directly. My daily commute is short enough that I don't worry about data usage.
3. **Travel**: Pre-download everything I might want. A 10-hour flight needs at least 2-3 books queued up.
4. **After finishing**: Delete the downloaded copy to free space. My listening progress is safely stored on the server.

Data usage perspective: even my largest audiobook (a full-cast Dune recording at 2.4GB) is well within most modern data plans. If you're on a tight data budget, pre-downloading on Wi-Fi is the obvious answer.

---

## 8. Reverse Proxy & SSL

If you're accessing Audiobookshelf from outside your home network — and with mobile apps, you probably will be — you need a reverse proxy with SSL. This gives you a clean URL like `https://audiobooks.yourdomain.com` instead of remembering an IP address and port.

### Option A: Nginx Proxy Manager (Recommended for Beginners)

Nginx Proxy Manager is a web UI for Nginx that makes reverse proxy setup point-and-click easy.

**Docker Compose for NPM** (run on a separate machine or the same host):

```yaml
services:
  nginx-proxy-manager:
    image: jc21/nginx-proxy-manager:latest
    container_name: nginx-proxy-manager
    ports:
      - "80:80"
      - "81:81"
      - "443:443"
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
    restart: unless-stopped
```

**Setup steps**:

1. Access NPM at `http://your-server-ip:81`
2. Default login: `admin@example.com` / `changeme`
3. Add a proxy host:
   - Domain Names: `audiobooks.yourdomain.com`
   - Forward Hostname/IP: `your-audiobookshelf-ip`
   - Forward Port: `13378`
   - Enable "Block Common Exploits"
   - SSL tab: Request a new SSL certificate (requires port 80 accessible for Let's Encrypt validation)
   - Enable "Force SSL" and "HTTP/2 Support"

### Option B: Traefik (For Docker-Native Setups)

If you're already running Traefik for other containers, adding Audiobookshelf is trivial. Add labels to your Audiobookshelf container:

```yaml
services:
  audiobookshelf:
    image: ghcr.io/advplyr/audiobookshelf:latest
    # ... existing config ...
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.audiobookshelf.rule=Host(`audiobooks.yourdomain.com`)"
      - "traefik.http.routers.audiobookshelf.entrypoints=websecure"
      - "traefik.http.routers.audiobookshelf.tls.certresolver=letsencrypt"
      - "traefik.http.services.audiobookshelf.loadbalancer.server.port=80"
    networks:
      - traefik

networks:
  traefik:
    external: true
```

### Subdomain Recommendation

I use `audiobooks.mydomain.com` — it's clean, descriptive, and easy to remember. Some people prefer `abs.mydomain.com` or `listen.mydomain.com`. Whatever you choose, make sure it's a subdomain you don't mind typing into your phone's app settings.

---

## 9. Remote Access: VPN vs. Exposed Server

Here's the critical security decision: how do you access your audiobooks when you're not home?

### My Recommendation: WireGuard VPN

I run a WireGuard server on my LAN (actually on the same Proxmox host, in its own LXC). My phone has a WireGuard profile with a home screen shortcut. Tap it, I'm on my LAN, Plappa sees the server, everything works.

**Why WireGuard over exposing the server directly?**

- **Security**: No open ports on your audiobook server to the public internet. No certificate management on the ABS container itself. No worrying about zero-day exploits in ABS being reachable from the internet.
- **Simplicity**: One VPN connection covers all your self-hosted services — Audiobookshelf, Home Assistant, Plex, file server, everything.
- **Performance**: WireGuard is fast. On a modern CPU, you'll barely notice the encryption overhead.
- **Data control**: Your traffic never transits through a third-party service.

**Basic WireGuard setup** (on a Debian/Ubuntu host):

```bash
# Install WireGuard
apt update && apt install -y wireguard

# Generate keys
wg genkey | tee privatekey | wg pubkey > publickey

# Create config /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <server-private-key>
Address = 10.200.200.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Phone
PublicKey = <phone-public-key>
AllowedIPs = 10.200.200.2/32

# Start WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
```

On your phone, install the WireGuard app, scan a QR code generated from your server config, and you're done.

### Alternative: Tailscale or ZeroTier

If rolling your own WireGuard feels like too much work, [Tailscale](https://tailscale.com) and [ZeroTier](https://www.zerotier.com) are excellent "zero-config" mesh VPN solutions. Install the app on your server and your phone, log in with the same account, and they handle the networking magic.

- **Tailscale**: Free for personal use (up to 20 devices). Uses WireGuard under the hood but handles key exchange and NAT traversal automatically. Has an iOS widget for one-tap connection.
- **ZeroTier**: Similar concept, slightly more configurable. Also free for personal use.

I've used both. Tailscale is simpler; ZeroTier is more flexible. For Audiobookshelf access, either is overkill in a good way.

### Why NOT Expose Directly?

You *could* expose Audiobookshelf directly to the internet via your reverse proxy. It has authentication, after all. But:

- Every exposed service is an attack surface
- Audiobookshelf's auth is functional but not battle-tested against dedicated attacks
- Your listening habits, library content, and user data become reachable by anyone who finds the URL
- Automated scanners constantly probe the internet for web services — obscurity is not security

The VPN approach adds one step (tap to connect) and dramatically improves your security posture. For a media server that contains potentially years of purchased content, that's a tradeoff I'm happy to make.

---

## 10. Podcast Support

I mentioned earlier that I'm more of an audiobook person than a podcast person, but Audiobookshelf's podcast support is genuinely impressive and worth covering.

### Adding Podcasts

1. In the web UI, switch to your podcast library (or create one if you haven't).
2. Click "Add" > "Search" or "Add RSS Feed".
3. For search, type the podcast name — Audiobookshelf queries multiple directories.
4. For RSS, paste the feed URL directly.

### Auto-Download Settings

Once a podcast is added, configure auto-download:

- **Schedule**: Check for new episodes every hour, every 6 hours, or daily
- **Max episodes to keep**: Auto-delete old episodes to manage storage (e.g., keep only the last 10)
- **Download automatically**: Queue new episodes for immediate download

This is perfect for news podcasts, daily shows, or any series you want to stay current on without manual intervention.

### Open RSS Feeds

Here's a feature most people don't know about: Audiobookshelf can generate RSS feeds for your libraries. This means you can:

- Share a curated podcast collection with friends
- Subscribe to your own audiobook library via a traditional podcast app (useful for weird edge cases)
- Create public-facing feeds for content you have rights to distribute

Enable it in Settings > RSS Feeds. Each library gets its own feed URL.

---

## 11. Backups & Maintenance

Self-hosting means you are your own sysadmin. The good news: Audiobookshelf makes backups easy.

### Automated Backups

Audiobookshelf has built-in automated backups that run on a schedule you define:

1. Go to Settings > Backups in the web UI
2. Set your backup schedule (I run daily at 3 AM)
3. Choose how many backups to keep (I keep 7 — one week's worth)
4. The backup includes: config, database, users, libraries, metadata, and settings

Backups are stored in your `/config/backups` directory. I have my backup location mounted to my NAS, so backups are automatically off the server.

### What to Back Up

| Priority | Path | Contents |
|----------|------|----------|
| Critical | `/config` | All server config, user accounts, listening progress, bookmarks, library settings |
| High | `/metadata` | Downloaded cover art, cached search results |
| Medium | `/audiobooks` | Your actual book files (can be re-ripped or re-downloaded, but that's work) |

My backup strategy:

- **Daily**: ABS built-in backup of `/config` to NAS
- **Weekly**: Full NAS snapshot to offsite backup (I use a second NAS at a family member's house, synced via Synology's Cloud Station)
- **Monthly**: Manual verification that I can restore from backup (this has saved me twice)

### Updates

Updating Audiobookshelf is a single command:

```bash
cd ~/docker/audiobookshelf
docker compose pull
docker compose up -d
```

I run this weekly via a cron job, but you could also use Watchtower for fully automatic updates. I prefer manual control so I can check the release notes first — Audiobookshelf updates are generally safe, but major version bumps sometimes have breaking changes.

---

## 12. The DRM Conversation (Brief, Honest)

I need to address the elephant in the room: DRM. This is the part of the guide where I can't give you a step-by-step, and there's a good reason for that.

### The Reality

Files downloaded from Audible (`.aax` format) and many other commercial sources are wrapped in DRM. Audiobookshelf **cannot** play DRM-protected files. This means that if your entire library is in Audible's ecosystem, you can't simply drop those files into Audiobookshelf and have them work.

### What the EFF Says

When Ars Technica's Lee Hutchinson researched this for his article, he reached out to the Electronic Frontier Foundation. Here's what EFF's Competition and IP Litigation Director Mitch Stoltz told him:

> "In the US, the law against 'circumventing' effective DRM has no personal-use exemption. In Europe, it varies by country... That's as silly as it sounds — stripping DRM from one's own copy of an audiobook in order to listen to it privately through different software doesn't threaten the author or publisher, except that it makes it harder for them to charge you twice for the same audiobook."

### What This Means for You

- **In the US**: Removing DRM from audiobooks you purchased, even for personal use, is legally problematic under the DMCA's anti-circumvention provisions.
- **In Europe**: Laws vary by country. Some have personal-use exemptions; others don't.
- **The practical reality**: Nobody is getting sued for stripping DRM from their own audiobook library to listen on their own server. But the legal framework exists, and you should be informed.

### My Recommendation

**Buy DRM-free whenever possible.**

Sources I use:

- **[Libro.fm](https://libro.fm)**: DRM-free audiobooks that support independent bookstores. Every purchase splits revenue with a local bookstore of your choice. Files are plain MP3s or M4Bs with no encryption. This is my primary source now.
- **Direct from publishers**: Many publishers sell DRM-free files directly from their websites.
- **Humble Bundle**: Occasional audiobook bundles, usually DRM-free.
- **[LibriVox](https://librivox.org)**: Public domain audiobooks, completely free, read by volunteers. Quality varies wildly, but you can't beat the price.
- **CD rips**: Physical audiobooks on CD have no DRM. Rip them with any standard CD ripping tool (I use Exact Audio Copy on Windows, XLD on Mac).

The transition to DRM-free isn't instant — I still have Audible books I purchased years ago that I'm slowly replacing as Libro.fm runs sales. But every new purchase is DRM-free, and my Audiobookshelf library grows week by week without legal ambiguity.

---

## 13. Conclusion: Own Your Media

Setting up Audiobookshelf was one of the most satisfying self-hosting projects I've done. Not because it was technically challenging — it wasn't. But because it solved a real problem in my daily life and gave me back something I'd unknowingly given away: ownership of media I paid for.

When my wife's Audible app stopped working that day, it was a wake-up call. We had spent thousands of dollars on audiobooks over the years, and in that moment, all of it was inaccessible because one company decided to push a broken update. That's not ownership. That's rental with extra steps.

Audiobookshelf changes that equation. My books live on my server. My progress is stored in my database. My access depends on my infrastructure, which I control and maintain. If something breaks, I fix it — and I don't have to wait for Amazon's support team to acknowledge the problem exists.

The setup is straightforward: Docker Compose for the server, consistent directory structure for the library, a mobile app for listening, and a VPN for secure remote access. The whole thing runs on hardware you probably already have, sipping 150MB of RAM at idle.

**My challenge to you**: Start with one book. Just one. Set up Audiobookshelf, add a single DRM-free audiobook, and try the mobile app. See how it feels to actually own the playback experience. From there, the library grows naturally — one purchase at a time, one rip at a time, one LibriVox download at a time.

Before you know it, you'll have your own personal audiobook server that works exactly the way you want it to. No spinning loading icons. No app stores. No platform lock-in. Just books, your way.

That's the promise of self-hosting, and Audiobookshelf delivers on it beautifully.

---

## Related Posts

- [Self-Hosted Music Streaming: Navidrome Setup Guide](/blog/self-hosted-music-navidrome) — Apply the same principles to your music library
- [Proxmox LXC Container Setup: From Zero to Docker](/blog/proxmox-lxc-docker) — The foundation this Audiobookshelf deployment runs on
- [Docker Compose for Homelab Beginners](/blog/docker-compose-homelab) — If the YAML in this guide looked like hieroglyphics, start here
- [WireGuard VPN Setup for Remote Homelab Access](/blog/wireguard-homelab-vpn) — Secure access to all your self-hosted services

## Resources & Links

- [Audiobookshelf GitHub](https://github.com/advplyr/audiobookshelf)
- [Official Audiobookshelf Documentation](https://www.audiobookshelf.org/docs)
- [Ars Technica: "I threw away Audible's app, and now I self-host my audiobooks"](https://arstechnica.com/gadgets/2025/03/i-threw-away-audibles-app-and-now-i-self-host-my-audiobooks/) — The article that inspired this guide
- [How-To Geek: "How I Replaced Audible with Audiobookshelf"](https://www.howtogeek.com/how-i-replaced-audible-with-audiobookshelf/)
- [Plappa (iOS App Store)](https://apps.apple.com/us/app/plappa/id6474096622) — Third-party iOS client
- [Libro.fm](https://libro.fm) — DRM-free audiobooks supporting independent bookstores
- [LibriVox](https://librivox.org) — Free public domain audiobooks
- [Audiobookshelf TestFlight (iOS)](https://testflight.apple.com/join/wiic7QI7) — Official iOS beta
- [Audiobookshelf Discord](https://discord.gg/audiobookshelf) — Community support and announcements

---

*Did you find this guide helpful? Have questions about your setup? I'm always happy to chat about homelab projects. The best part of self-hosting is the community — pass it forward when you can.*
