---
layout: post.njk
title: "Immich: The Self-Hosted Google Photos Alternative That Actually Works (June 2026)"
date: 2026-06-17
description: "Google Photos is raising prices again and scanning your images for AI training. Here's how to replace it with Immich — a self-hosted photo management platform that runs on a Raspberry Pi or your existing homelab server, with face recognition, automatic backup, and sharing that doesn't sell your data."
tags: ["immich", "photo-management", "self-hosted", "privacy", "google-photos", "homelab", "docker", "proxmox", "backup"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/immich-photo-management-homelab"
---

Google Photos just got more expensive. Again.

If you're on the 2TB plan, you already know the feeling — that notification that your subscription is going up another few dollars a month for the same service you've been using for years. But here's what bothers me more than the price: Google is [explicitly using your photos](https://blog.google/products/photos/google-photos-update-2025/) to train its AI models. Your family pictures, your vacation shots, your screenshots of sensitive documents — all of it feeds into Google's machine learning pipeline.

I moved my photo library off Google Photos in early 2025. It took a weekend to set up, and I've never looked back. If you run a homelab — even something as simple as a Raspberry Pi 4 or an old laptop — you can do the same thing for the cost of a hard drive.

## Why Leave Google Photos?

Let's be honest about what you're actually paying for:

**What Google Photos gives you:**
- Automatic backup from every device
- Decent search ("photos of dogs at the beach")
- Face recognition that groups people reasonably well
- Easy sharing links
- 15GB free, then $2.99/month for 100GB, $9.99/month for 2TB

**What Google Photos takes from you:**
- Your photos train Google's AI (opt-out buried in settings, and even that's questionable)
- No real control over your data — Google can change terms, raise prices, or sunset the service
- Compression on "high quality" backups (not actually original quality)
- Limited export options if you ever want to leave
- Your location data, facial recognition maps, and metadata are stored indefinitely

For most people, the trade-off is fine. But if you're reading a blog called *devhandbook.io*, you're probably not "most people." You already self-host your media server, your password manager, and maybe your AI models. Your photos are the last piece of data you don't control.

## Enter Immich: Self-Hosted Photo Management

[Immich](https://immich.app/) is an open-source, self-hosted photo and video management solution that replicates the core Google Photos experience — automatic backup, AI-powered search, face recognition, sharing — while keeping everything on your own hardware.

Here's what matters:

- **Your photos stay on your server.** Full stop. No third-party APIs, no cloud processing, no AI training on your data.
- **Automatic backup from mobile.** The Immich iOS and Android apps upload photos in the background just like Google Photos.
- **AI search that works.** Search by objects, faces, locations, and text in images — all processed locally.
- **Face recognition.** Groups photos by person, just like Google Photos. You can merge, rename, and hide faces.
- **Sharing without sacrifice.** Create shared albums with public links or specific users.
- **Raw format support.** Handles RAW, HEIC, HEIF, and live photos properly.
- **No compression games.** Stores originals unless you explicitly enable transcoding.

The project has 50,000+ GitHub stars and an active development team releasing updates weekly. It's not some abandoned side project — it's become the default recommendation in r/selfhosted and r/homelab for photo management.

## Hardware Requirements: What You Actually Need

Immich is more demanding than a simple file server, but it's not as heavy as you'd think. Here's what works:

| Setup | RAM | Storage | Performance | Notes |
|-------|-----|---------|-------------|-------|
| **Raspberry Pi 4 (8GB)** | 8GB | External USB 3.0 SSD | Usable for <50K photos | Face recognition and AI search are slow but functional |
| **Mini PC (Intel N100/N200)** | 16GB | NVMe SSD + external drive | Good for 100K+ photos | Sweet spot for most users |
| **Old laptop/desktop** | 16GB+ | SATA SSD or NVMe | Excellent | Repurpose hardware you already have |
| **Proxmox LXC/VM** | 4-8GB allocated | ZFS or bind-mounted storage | Excellent | My current setup — see below |
| **Synology/QNAP NAS** | 8GB+ | NAS drives | Good | Run via Docker on the NAS |

**The AI components need the most resources.** Face recognition and CLIP-based search run machine learning models. On a Pi 4, initial face detection for a large library can take hours. On a modern CPU with 16GB RAM, it's minutes.

**My actual setup:** Immich runs in a Proxmox LXC container on my Intel N100 mini PC. I allocated 6GB RAM and 2 cores. The photo library lives on a 4TB external drive mounted via the host. Initial scan of ~35,000 photos took about 45 minutes. Daily background uploads from my phone are instant.

## Installation: Docker Compose on Any System

Immich distributes via Docker Compose. If you've set up any self-hosted service before, this is standard.

### Step 1: Create the Docker Compose file

Create a directory for Immich and save this as `docker-compose.yml`:

```yaml
name: immich

services:
  immich-server:
    container_name: immich_server
    image: ghcr.io/immich-app/immich-server:${IMMICH_VERSION:-release}
    volumes:
      - ${UPLOAD_LOCATION}:/usr/src/app/upload
      - /etc/localtime:/etc/localtime:ro
    environment:
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_USERNAME=postgres
      - DB_DATABASE_NAME=immich
    ports:
      - 2283:3001
    depends_on:
      - redis
      - database
    restart: always
    healthcheck:
      disable: false

  immich-machine-learning:
    container_name: immich_machine_learning
    image: ghcr.io/immich-app/immich-machine-learning:${IMMICH_VERSION:-release}
    volumes:
      - model-cache:/cache
    environment:
      - MACHINE_LEARNING_WORKERS=1
      - MACHINE_LEARNING_WORKER_TIMEOUT=120
    restart: always
    healthcheck:
      disable: false

  redis:
    container_name: immich_redis
    image: docker.io/redis:6.2-alpine
    restart: always
    healthcheck:
      test: redis-cli ping || exit 1

  database:
    container_name: immich_postgres
    image: docker.io/tensorchord/pgvecto-rs:pg14-v0.2.0@sha256:90724186f0a3519f29a0daa8b0a1286ca2c0f9bbd733f266cd7d9999c3d86122
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_USER=postgres
      - POSTGRES_DB=immich
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: always

volumes:
  model-cache:
  pgdata:
```

### Step 2: Create the environment file

Save as `.env` in the same directory:

```bash
# The location where your uploaded files are stored
UPLOAD_LOCATION=./library

# The Immich version to use — 'release' tracks stable releases
IMMICH_VERSION=release

# Database password — change this to something secure
DB_PASSWORD=your-secure-password-here
```

**Important:** Set `UPLOAD_LOCATION` to an absolute path or a path with plenty of space. This is where all your photos and videos will live. On my system, it's `/mnt/photos/immich-library` pointing to the external drive.

### Step 3: Start Immich

```bash
docker compose up -d
```

The first startup downloads images and initializes the database. Give it 2-3 minutes, then access the web UI at `http://your-server-ip:2283`.

### Step 4: Create your admin account

The first user to register becomes the admin. Go to `http://your-server-ip:2283/auth/register`, create your account, and you're in.

### Step 5: Configure backup from your phone

Download the Immich app (iOS or Android), point it at your server URL, and enable background upload. The app will upload new photos automatically — just like Google Photos.

**Pro tip:** Enable "Background Refresh" on iOS and battery optimization exceptions on Android so uploads happen without you thinking about it.

## Reverse Proxy and HTTPS (Required for Mobile Apps)

The mobile apps require HTTPS. You have two options:

**Option A: Cloudflare Tunnel (easiest)**

If you already use Cloudflare for other services, create a tunnel pointing to `localhost:2283` on your server. Zero port forwarding, automatic HTTPS.

**Option B: Nginx Proxy Manager**

If you run [Nginx Proxy Manager](https://nginxproxymanager.com/) (and you probably do if you're reading this), add a proxy host:
- Domain: `photos.yourdomain.com`
- Forward Hostname/IP: `immich_server` (or your server IP)
- Forward Port: `3001`
- Enable "Block Common Exploits" and "Websockets Support"
- Request a new SSL certificate

**Option C: Traefik**

If your homelab uses Traefik, add labels to the `immich-server` service:

```yaml
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.immich.rule=Host(`photos.yourdomain.com`)"
      - "traefik.http.routers.immich.tls.certresolver=letsencrypt"
      - "traefik.http.services.immich.loadbalancer.server.port=3001"
```

## Migrating from Google Photos

This is the part everyone worries about, and honestly, it's easier than you'd think.

### Step 1: Export from Google Photos

1. Go to [Google Takeout](https://takeout.google.com/)
2. Select "Google Photos"
3. Choose export format: **ZIP** (not TGZ — easier to work with)
4. Wait for Google to prepare the export (can take hours to days for large libraries)
5. Download the ZIP files

**Important:** Google Takeout exports preserve timestamps and metadata in JSON sidecar files. Immich reads these automatically during import.

### Step 2: Extract and Import

```bash
# Extract the Takeout ZIP
unzip takeout-*.zip -d ./google-photos-export/

# The structure will be:
# ./google-photos-export/Takeout/Google Photos/
#   ├── 2024/
#   ├── 2023/
#   ├── Photos from 2022/
#   └── ...
```

### Step 3: Upload to Immich

In the Immich web UI:
1. Go to **Administration → Jobs**
2. Or use the upload button in the main interface
3. Drag and drop your extracted folders

Immich will process the photos, read the JSON metadata, organize them by date, and run face recognition in the background. For a 30,000-photo library, expect the initial processing to take 1-3 hours depending on hardware.

**Alternative: CLI bulk import**

For large libraries, use the [Immich CLI](https://immich.app/docs/features/command-line-interface):

```bash
npm install -g @immich/cli
immich login http://your-server-ip:2283/api your-api-key
immich upload --recursive ./google-photos-export/
```

## What About the AI Features?

Here's where Immich gets interesting. The machine learning container runs several models locally:

### Face Recognition
- Detects and groups faces across your entire library
- You can name people, merge duplicates, and hide faces you don't want recognized
- All processing happens on your server — no data leaves your network

### Smart Search (CLIP)
- Search by description: "photos of beach sunsets" or "my dog in the snow"
- Works surprisingly well for natural language queries
- Powered by OpenCLIP models running locally

### Duplicate Detection
- Finds visually similar photos and exact duplicates
- Useful for cleaning up burst shots and accidental double-uploads

### Metadata Extraction
- Reads EXIF data, GPS coordinates, and timestamps
- Builds a timeline view and map view of your photos

**Performance note:** The first time you upload a large library, the ML container will work hard. CPU usage will spike. This is normal. Once the initial scan is complete, daily uploads process in seconds.

## The Honest Downsides

Immich is great, but it's not perfect. Here are the trade-offs:

**1. You're responsible for backups**

Unlike Google Photos, there's no automatic cloud redundancy. If your drive dies, your photos die. Set up a proper backup strategy:
- **Local:** RAID or ZFS with redundancy
- **Offsite:** Sync to a second location (Backblaze B2, another server, or even a friend's house)
- **My setup:** Primary storage on the N100, nightly `rsync` to my NAS, weekly `rclone` to Backblaze B2

**2. No free tier**

Well, it's free software, but you pay for hardware, electricity, and drives. A 4TB external drive costs ~$80. Over 5 years, that's cheaper than Google Photos — but it's upfront cost, not a subscription.

**3. Mobile apps are good, not great**

The iOS and Android apps handle backup and browsing well, but they're not as polished as Google Photos. Occasional quirks, slower search, and fewer editing features. For viewing and sharing, they're fine. For heavy editing, you'll want a separate app.

**4. Sharing requires your server to be accessible**

Public sharing links only work if your server is reachable from the internet. If you run everything behind a VPN, sharing gets more complicated. Solutions: Cloudflare Tunnel, Tailscale funnel, or just accepting that shared links need internet access.

**5. Initial setup takes effort**

This isn't a 5-minute setup. Plan for an afternoon of Docker configuration, reverse proxy setup, and library import. The payoff is worth it, but there's no "just works" button.

## My Actual Workflow

Here's how I use Immich day-to-day:

**Morning:** Photos from yesterday auto-upload from my phone overnight. I check the timeline over coffee.

**Weekly:** I review the "Recently Added" album, delete obvious garbage (duplicate screenshots, accidental pocket shots), and name any unrecognized faces.

**Monthly:** I run duplicate detection and clean up storage. Usually frees up a few GB.

**Sharing:** Family gets shared album links for events. They don't need accounts — just the link.

**Backup anxiety level:** Zero. I know exactly where my photos are, how they're backed up, and that no company is mining them for AI training.

## Cost Comparison: Self-Hosted vs. Google Photos

| Cost | Google Photos (2TB) | Self-Hosted (Immich) |
|------|---------------------|----------------------|
| **Year 1** | $119.88 | ~$200 (4TB drive + existing hardware) |
| **Year 2** | $119.88 | ~$20 (electricity) |
| **Year 3** | $119.88 | ~$20 (electricity) |
| **5-year total** | $599.40 | ~$260 + hardware |
| **10-year total** | $1,198.80 | ~$360 + hardware |

The break-even point is around 18 months if you already have the hardware. If you need to buy a mini PC, it's closer to 3 years. After that, you're saving ~$100/year indefinitely.

But this isn't really about money. It's about control. The $100/year is what you pay to not have your photos scanned by AI, to not worry about price hikes, and to own your data.

## Quick Start for the Impatient

If you want to try Immich without committing, do this:

1. **Install Docker Desktop** on your laptop or any machine with 8GB+ RAM
2. **Save the compose file** and `.env` from above
3. **Run:** `docker compose up -d`
4. **Upload a few hundred photos** and play with search and face recognition
5. **Decide** if the experience is worth migrating your full library

You can evaluate it in an afternoon. If it's not for you, `docker compose down` and delete the folder. No harm done.

## Related Reading

- [Running Local LLMs on Your Mac Mini](/blog/local-llms-mac-mini-practical-guide/) — Same N100 hardware, different use case
- [Self-Hosted This Week: April 2026](/blog/selfhosted-weekly-2026-04-13/) — Broader roundup of self-hosted tools
- [Uptime Kuma vs Nezha Dashboard Comparison](/blog/uptime-kuma-vs-nezha-monitoring-comparison/) — Monitoring your Immich server

---

*Have you migrated off Google Photos? What self-hosted photo management solution are you using? I'd love to hear about your setup — find me on [GitHub](https://github.com/bryanmoon19) or drop a note in the comments.*
