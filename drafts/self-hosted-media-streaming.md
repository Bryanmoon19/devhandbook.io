# Complete Guide to Self-Hosted Media Streaming

**A practical walkthrough of Plex, Jellyfin, and the open-source ecosystem for streaming your own movies, TV, and music.**

---

## Introduction: Why Self-Host Your Media?

Let’s be honest — streaming subscriptions are getting expensive. Netflix, Hulu, Disney+, Spotify, Apple Music… the costs add up fast. But beyond the price tag, self-hosting your media gives you something those services never will: **complete control**.

When you run your own media server, you own your content. No licensing deals expiring and pulling your favorite show overnight. No algorithm deciding what you should watch next. No ads, no data mining, no arbitrary limits on streams or quality. Your media, your rules.

Self-hosted streaming isn’t just for pirates or Linux zealots, either. It’s for anyone who wants a Netflix-like experience for their personal collection of movies, TV shows, music, photos, and even home videos. Whether you’ve got a massive Blu-ray rips collection or just want to centralize family photos, a media server turns your hardware into a private streaming platform accessible from anywhere.

The best part? Modern tools make it surprisingly easy. With Docker, a few configuration files, and a couple of hours, you can have a setup rivaling commercial services — and in some ways surpassing them.

---

## The Landscape: Your Options

Before diving into setup, let’s survey the field. There are several major players, each with different philosophies around open source, cost, and features.

### Plex — The Industry Standard

Plex is the most well-known name in self-hosted media. It’s polished, feature-rich, and has apps on virtually every platform imaginable. The basic server is free, but advanced features (hardware transcoding, live TV/DVR, offline mobile sync, and some music features) require a **Plex Pass** subscription (~$5/month or $120 lifetime).

Plex also pushes its own content (ad-supported movies and shows) and has increasingly integrated streaming services — a trend some users find intrusive. Still, for ease of use and client support, it’s hard to beat.

### Jellyfin — The Open-Source Champion

Jellyfin is a **fully open-source** fork of Emby (after Emby went proprietary). It’s 100% free — no subscriptions, no upsells, no feature paywalls. The community is active, development is rapid, and the feature gap with Plex narrows every year.

If you value open source, privacy, and zero ongoing cost, Jellyfin is the obvious choice. The trade-off? Slightly less polish in some client apps and a smaller ecosystem of third-party tools.

### Emby — The Freemium Middle Ground

Emby sits between Plex and Jellyfin. It offers a free tier but locks hardware transcoding and some advanced features behind **Emby Premiere** (~$5/month). Like Plex, it’s proprietary.

Some users prefer Emby’s interface or find its plugin system more flexible. But with Jellyfin offering a comparable open-source alternative, Emby’s value proposition has weakened for new setups.

### Navidrome — Music-Focused & Lightweight

If your primary need is music, [Navidrome](https://www.navidrome.org) is worth a look. It’s a lightweight, Subsonic-compatible music server with a clean web UI and excellent mobile app support (via Subsonic clients like DSub and play:Sub). It handles large libraries well and has low resource requirements.

### Stash — Adult Content Management

For those with… specialized media collections, [Stash](https://stashdb.org) is an open-source adult content organizer and player with metadata scraping, scene tagging, and a web interface. Mentioning it here because it fills a niche the mainstream tools ignore.

---

## Feature Comparison

| Feature | Plex | Jellyfin | Emby |
|---------|------|----------|------|
| **License** | Proprietary | Open Source (GPLv2) | Proprietary |
| **Cost** | Free / Plex Pass | 100% Free | Free / Premiere |
| **Hardware Transcoding** | Plex Pass only | Free | Premiere only |
| **Live TV/DVR** | Plex Pass only | Free | Premiere only |
| **Client Apps** | Excellent (all platforms) | Good (improving rapidly) | Good |
| **Web Interface** | Polished | Polished | Polished |
| **Plugin/Add-on Ecosystem** | Large | Growing | Moderate |
| **Music Support** | Good (Plexamp is great) | Good | Good |
| **Photo Support** | Yes | Yes | Yes |
| **Remote Access** | Built-in relay | Manual (Tailscale/VPN/port forwarding) | Built-in |
| **Third-Party Integration** | Extensive | Growing (Sonarr/Radarr/Lidarr via Jellyseerr) | Moderate |

**Bottom line:** For most users, the decision is between **Plex** (ease of use, ecosystem) and **Jellyfin** (open source, free, privacy). This guide covers both.

---

## Hardware Requirements

Before installing anything, make sure your hardware can handle the workload.

### CPU & Transcoding

**Transcoding** — converting video on-the-fly to match a client’s capabilities — is the most CPU-intensive task a media server performs. If all your clients can direct-play your media (same codec, within bitrate limits), CPU requirements are minimal. If you need transcoding, plan accordingly.

| Transcoding Type | CPU Requirement | Notes |
|-----------------|-----------------|-------|
| Direct play / no transcoding | Almost anything | Raspberry Pi 4 works fine |
| 1-2 1080p software transcodes | 4-core Intel/AMD, 2.0 GHz+ | Passable but not ideal |
| 3-5 1080p transcodes | 6-core modern CPU | Intel 10th-gen+, AMD Ryzen 3000+ |
| 4K → 1080p transcodes | Intel Quick Sync or NVIDIA NVENC | Hardware transcoding essential |
| Multiple 4K transcodes | Intel Arc, NVIDIA GTX 1650+, or dedicated | GPU encoding is a game-changer |

**Hardware transcoding** dramatically reduces CPU load. Intel CPUs with Quick Sync (6th-gen and newer) are the sweet spot — integrated, efficient, and well-supported. NVIDIA GPUs work too but use more power. AMD VCE exists but has patchier support across tools.

### RAM

- **Minimum:** 2 GB (for small libraries, no transcoding)
- **Comfortable:** 4 GB
- **Recommended:** 8 GB+ (especially with large libraries or multiple transcodes)

### Storage

Storage needs depend entirely on your collection:

- **1080p movie:** 5–15 GB
- **4K movie:** 20–80 GB
- **TV episode (1080p):** 1–4 GB
- **Music (FLAC):** ~30 MB per album

A modest movie collection (500 films) plus TV shows can easily reach **10–20 TB**. Plan for growth.

**Storage tips:**
- Use a NAS or large hard drives (16–20 TB shucked drives are cost-effective)
- Consider RAID or at least a backup strategy (more on that later)
- SSD for the OS and metadata cache improves library scanning speed

### Network

- **Wired Ethernet** for the server is non-negotiable for 4K streaming
- **Gigabit LAN** minimum; 2.5 GbE or faster if you have multiple 4K streams
- **Upload bandwidth** for remote access: 5–10 Mbps per 1080p stream; 25+ Mbps per 4K stream

---

## Jellyfin Setup with Docker Compose

Jellyfin is my go-to recommendation for new self-hosters. Let’s get it running.

### Directory Structure

Create a clean layout for your media server:

```
/opt/media-server/
├── jellyfin/
│   ├── docker-compose.yml
│   ├── config/
│   └── cache/
├── plex/
│   ├── docker-compose.yml
│   ├── config/
│   └── transcode/
├── media/
│   ├── movies/
│   ├── tv/
│   └── music/
└── nginx/
    └── docker-compose.yml
```

### Jellyfin Docker Compose

Create `/opt/media-server/jellyfin/docker-compose.yml`:

```yaml
version: "3.8"

services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    user: 1000:1000  # Adjust to your user:group IDs (run `id` to check)
    network_mode: host  # Required for DLNA and some client discovery; or use bridge + port mapping
    # Alternative bridge mode:
    # ports:
    #   - "8096:8096"  # HTTP
    #   - "8920:8920"  # HTTPS (optional)
    volumes:
      - ./config:/config
      - ./cache:/cache
      - /path/to/media/movies:/media/movies:ro
      - /path/to/media/tv:/media/tv:ro
      - /path/to/media/music:/media/music:ro
    environment:
      - TZ=America/New_York  # Change to your timezone
      - PUID=1000
      - PGID=1000
    devices:
      # Intel Quick Sync (for hardware transcoding)
      - /dev/dri:/dev/dri
      # NVIDIA (uncomment if using NVENC)
      # - /dev/nvidia0:/dev/nvidia0
      # - /dev/nvidiactl:/dev/nvidiactl
      # - /dev/nvidia-modeset:/dev/nvidia-modeset
      # - /dev/nvidia-uvm:/dev/nvidia-uvm
      # - /dev/nvidia-uvm-tools:/dev/nvidia-uvm-tools
    restart: unless-stopped
```

**Key settings explained:**

- `user: 1000:1000` — Runs the container as your user instead of root. Prevents permission headaches. Find your IDs with the `id` command.
- `network_mode: host` — Simplifies DLNA and some smart TV discovery. If you don’t need those, use bridge mode with explicit port mappings.
- `/dev/dri` passthrough — Required for Intel Quick Sync hardware transcoding.
- `volumes` — The `ro` (read-only) flag on media directories is a safety measure. Jellyfin only needs to read your files.

### Starting Jellyfin

```bash
cd /opt/media-server/jellyfin
docker compose up -d
```

Visit `http://your-server-ip:8096` and complete the initial setup wizard:

1. **Set language and admin account**
2. **Add media libraries** — point to `/media/movies`, `/media/tv`, etc.
3. **Set metadata languages** — English usually works; configure as needed
4. **Configure remote access** — we’ll handle this properly with a reverse proxy later; leave defaults for now

### Hardware Transcoding in Jellyfin

Go to **Dashboard → Playback → Transcoding** and enable:

- **Enable hardware decoding:** Check all formats your CPU/GPU supports (H.264, HEVC/H.265, AV1 if available)
- **Enable hardware encoding**
- **Intel Quick Sync:** Select `QSV` as the encoder
- **NVIDIA:** Select `NVENC`

Save and test by playing a video that needs transcoding. Check the Dashboard’s **Active Devices** section — it’ll show whether hardware transcoding is active.

---

## Plex Setup with Docker Compose

If you prefer Plex, here’s the equivalent setup.

### Plex Docker Compose

Create `/opt/media-server/plex/docker-compose.yml`:

```yaml
version: "3.8"

services:
  plex:
    image: plexinc/pms-docker:latest
    container_name: plex
    network_mode: host  # Plex strongly prefers host networking
    environment:
      - TZ=America/New_York
      - PLEX_CLAIM=claim-XXXXXXXXXXXXXXXX  # Optional: get from https://plex.tv/claim for easy account linking
      - PUID=1000
      - PGID=1000
      - VERSION=docker
    volumes:
      - ./config:/config
      - ./transcode:/transcode
      - /path/to/media/movies:/media/movies:ro
      - /path/to/media/tv:/media/tv:ro
      - /path/to/media/music:/media/music:ro
    devices:
      - /dev/dri:/dev/dri  # Intel Quick Sync
    restart: unless-stopped
```

**Notes:**

- `PLEX_CLAIM` — Get a claim token from [plex.tv/claim](https://plex.tv/claim) and paste it here for automatic server association with your Plex account. The token expires after a few minutes, so grab it right before starting the container.
- `network_mode: host` — Plex really wants host networking for proper remote access and client discovery. It works in bridge mode, but you’ll have more headaches.

### Starting Plex

```bash
cd /opt/media-server/plex
docker compose up -d
```

Visit `http://your-server-ip:32400/web` and complete setup. Plex’s wizard is straightforward — add libraries, let it scan, and you’re streaming.

### Plex Pass & Hardware Transcoding

Hardware transcoding requires a **Plex Pass**. Once you have one:

1. Go to **Settings → Server → Transcoder**
2. Enable **Use hardware acceleration when available**
3. Select your encoder (Intel QSV, NVENC, etc.)
4. Check **Use hardware-accelerated video encoding**

Without Plex Pass, you’re limited to software transcoding — fine for direct play, rough for anything else.

---

## Reverse Proxy Setup

You don’t want to access your media server with `:8096` or `:32400` in the URL. A reverse proxy gives you clean URLs (`jellyfin.yourdomain.com`), automatic HTTPS, and a single point for access control.

### Option A: Nginx Proxy Manager (Recommended)

[Nginx Proxy Manager](https://nginxproxymanager.com/) is a web UI for Nginx that makes reverse proxying and SSL trivial. It’s what I use and recommend.

Create `/opt/media-server/nginx/docker-compose.yml`:

```yaml
version: "3.8"

services:
  npm:
    image: jc21/nginx-proxy-manager:latest
    container_name: npm
    ports:
      - "80:80"
      - "443:443"
      - "81:81"  # Admin UI
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
    restart: unless-stopped
```

```bash
cd /opt/media-server/nginx
docker compose up -d
```

Visit `http://your-server-ip:81` — default login is `admin@example.com` / `changeme`. Change it immediately.

**Add a proxy host:**

1. **Dashboard → Proxy Hosts → Add**
2. **Domain Names:** `jellyfin.yourdomain.com`
3. **Forward Hostname/IP:** Your Jellyfin server IP (or `jellyfin` if on the same Docker network)
4. **Forward Port:** `8096`
5. **Enable SSL:** Request a new certificate (requires port 80 accessible from the internet for Let’s Encrypt validation)
6. **Save**

Repeat for Plex (`plex.yourdomain.com` → port `32400`).

### Option B: Manual Nginx

If you prefer raw Nginx, here’s a sample config for Jellyfin:

```nginx
server {
    listen 443 ssl http2;
    server_name jellyfin.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8096;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Protocol $scheme;
        proxy_set_header X-Forwarded-Host $http_host;

        # WebSocket support (required for Jellyfin)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## SSL/TLS Configuration

HTTPS isn’t optional for remote access. You have two main paths:

### Let’s Encrypt (Free)

Requires:
- A domain name pointing to your server
- Port 80 open to the internet (for HTTP-01 validation)

Nginx Proxy Manager handles this automatically. For manual setups, use [Certbot](https://certbot.eff.org/):

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d jellyfin.yourdomain.com -d plex.yourdomain.com
```

Certificates auto-renew. Reference them in your Nginx config.

### Cloudflare Origin Certificates (Alternative)

If you use Cloudflare DNS, you can generate a 15-year origin certificate and have Cloudflare handle client-facing TLS. This skips the need for public port 80. Just make sure communication between Cloudflare and your origin is encrypted (Full/Strict mode).

---

## Client Apps

Your server is useless without clients. Here’s what’s available:

### Jellyfin Clients

| Platform | App | Notes |
|----------|-----|-------|
| **iOS / iPadOS** | Swiftfin | Native app, improving rapidly. Available on App Store |
| **Android** | Jellyfin Android | Official, excellent |
| **Android TV** | Jellyfin Android TV | Official, good |
| **Apple TV** | Swiftfin | tvOS version exists but is less mature |
| **Roku** | Jellyfin Roku | Official channel |
| **Web** | Browser | Excellent; basically the reference client |
| **Desktop** | Jellyfin Media Player / Jellyfin MPV Shim | Desktop apps with better codec support |

### Plex Clients

Plex’s biggest advantage is client ubiquity. It’s on **everything** — smart TVs, game consoles, streaming sticks, phones, tablets, cars, you name it. The official apps are polished and consistent.

**One caveat:** Some Plex client apps (especially on mobile) require a Plex Pass for full functionality like offline sync.

---

## Remote Access

Once you leave your home network, you need a way to reach your server securely.

### Option 1: Tailscale (Recommended for Most Users)

[Tailscale](https://tailscale.com/) creates a private mesh VPN between your devices. It’s absurdly easy to set up:

1. Install Tailscale on your server: `curl -fsSL https://tailscale.com/install.sh | sh`
2. Install it on your phone/laptop/tablet
3. Log in with the same account
4. Done — your devices can now reach each other as if on the same LAN

**Pros:**
- Zero-config networking
- NAT traversal just works
- End-to-end encryption
- Free for personal use (up to 20 devices)
- No port forwarding needed

**Cons:**
- Each client needs Tailscale installed
- Slightly more latency than direct connections

Access Jellyfin at `http://server-tailscale-ip:8096` from anywhere.

### Option 2: Traditional VPN (WireGuard, OpenVPN)

For more control, run your own VPN server. [WireGuard](https://www.wireguard.com/) is the modern standard — fast, simple, secure.

```bash
# Example: install WireGuard on Ubuntu
sudo apt install wireguard
# Generate keys, configure peers, forward the UDP port
```

This requires port forwarding on your router (see below) and more configuration, but gives you full control.

### Option 3: Port Forwarding (Direct Access)

Forward ports on your router:

- Jellyfin: `8096` → server IP
- Plex: `32400` → server IP

Plex has a built-in relay system that can punch through NAT without manual port forwarding, but it’s slower. For Jellyfin, you need either Tailscale, a VPN, or explicit port forwarding.

**Security warning:** If you expose media servers directly to the internet, use strong passwords, keep software updated, and ideally put it behind a reverse proxy with rate limiting. Media servers are juicy targets.

---

## Integration with the *arr Stack

A media server is only half the equation. The other half is **acquiring and organizing content** — and that’s where the *arr stack shines.

The *arr apps are automation tools for media:

| Tool | Purpose |
|------|---------|
| **Sonarr** | TV show automation |
| **Radarr** | Movie automation |
| **Lidarr** | Music automation |
| **Readarr** | Ebook/audiobook automation |
| **Bazarr** | Subtitle automation |
| **Prowlarr** | Indexer manager (replaces Jackett) |

### How It Works

1. **Prowlarr** manages your indexers (Usenet NZBs and torrent sites)
2. **Sonarr/Radarr/Lidarr** monitor your wanted list and search indexers via Prowlarr
3. When a release is found, it’s sent to your download client (qBittorrent, SABnzbd, etc.)
4. When the download completes, Sonarr/Radarr rename and move it to your media folder
5. Jellyfin/Plex scans the folder and the content appears in your library

### Docker Compose for the *arr Stack

```yaml
version: "3.8"

services:
  sonarr:
    image: lscr.io/linuxserver/sonarr:latest
    container_name: sonarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    volumes:
      - ./sonarr-config:/config
      - /path/to/media/tv:/tv
      - /path/to/downloads:/downloads
    ports:
      - "8989:8989"
    restart: unless-stopped

  radarr:
    image: lscr.io/linuxserver/radarr:latest
    container_name: radarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    volumes:
      - ./radarr-config:/config
      - /path/to/media/movies:/movies
      - /path/to/downloads:/downloads
    ports:
      - "7878:7878"
    restart: unless-stopped

  lidarr:
    image: lscr.io/linuxserver/lidarr:latest
    container_name: lidarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    volumes:
      - ./lidarr-config:/config
      - /path/to/media/music:/music
      - /path/to/downloads:/downloads
    ports:
      - "8686:8686"
    restart: unless-stopped

  prowlarr:
    image: lscr.io/linuxserver/prowlarr:latest
    container_name: prowlarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    volumes:
      - ./prowlarr-config:/config
    ports:
      - "9696:9696"
    restart: unless-stopped
```

**Key point:** All *arr apps and your media server should share the same `PUID/PGID` and mount the same `/downloads` and media directories. This ensures downloaded files are readable by Jellyfin/Plex after processing.

---

## Backup and Maintenance

Your media server is only as good as your backups. Here’s what to protect:

### What to Back Up

| Data | Location | Priority |
|------|----------|----------|
| **Media files** | Your NAS/storage | Critical — this is irreplaceable |
| **Jellyfin config** | `/opt/media-server/jellyfin/config` | High — metadata, watch history, user settings |
| **Plex config** | `/opt/media-server/plex/config` | High — same as above |
| ***arr configs** | `./sonarr-config`, etc. | High — your entire automation setup |
| **Nginx Proxy Manager data** | `./data`, `./letsencrypt` | Medium — easy to recreate but annoying |

### Backup Strategy

1. **Media files:** Use a proper backup tool like [BorgBackup](https://borgbackup.org/), [Restic](https://restic.net/), or a second NAS. RAID is not a backup — it protects against drive failure, not deletion or corruption.

2. **Configuration:** These are small — sync them with Syncthing, rsync to another machine, or include them in your BorgBackup repository.

3. **Offsite backup:** Keep a copy somewhere else. Backblaze B2, Wasabi, or a second location.

### Maintenance Tasks

| Frequency | Task |
|-----------|------|
| **Weekly** | Check for Docker image updates: `docker compose pull && docker compose up -d` |
| **Monthly** | Verify backups are restorable. Test a restore. |
| **Quarterly** | Clean up old/unwanted media. Check disk space trends. |
| **As needed** | Restart services if they get cranky. Logs are in the config directories. |

---

## Which One Should You Choose?

Here’s my honest take:

### Choose Jellyfin If:

- You care about open source and software freedom
- You don’t want ongoing subscription costs
- You value privacy and want zero telemetry
- You’re comfortable with slightly less mature client apps
- You want to tinker and contribute to the ecosystem

### Choose Plex If:

- You want the easiest possible setup with the best client support
- You’re willing to pay for Plex Pass (or don’t need hardware transcoding)
- You value polish and a mature ecosystem over open-source purity
- You want features like live TV/DVR and don’t mind the cost
- You share your library with less technical family members who need plug-and-play apps

### My Recommendation

Start with **Jellyfin**. It’s free, it’s capable, and it improves constantly. If you hit a wall with client support or missing features, you can always migrate to Plex later — your media files don’t change, just the server reading them.

For music-first users, consider **Navidrome** alongside your video server. It’s lighter and purpose-built for audio.

---

## Conclusion

Self-hosting your media isn’t just a cost-saving measure — it’s a reclaiming of ownership. Your movies, your music, your data, your rules. Modern tools like Jellyfin, Plex, and the *arr ecosystem have made it more accessible than ever.

The barrier to entry is lower than most people think. If you can write a Docker Compose file and configure a reverse proxy, you’re already most of the way there. And once it’s running, the experience rivals anything the streaming giants offer — minus the monthly bills, the rotating catalogs, and the data mining.

Your media deserves a home you control. Give it one.

---

**Further Reading:**
- [Jellyfin Documentation](https://jellyfin.org/docs/)
- [Plex Support](https://support.plex.tv/)
- [TRaSH Guides](https://trash-guides.info/) — The bible for *arr automation quality settings
- [r/jellyfin](https://reddit.com/r/jellyfin) & [r/plex](https://reddit.com/r/plex) — Active communities for troubleshooting

---

*Got questions or want to share your setup? Find me on [devhandbook.io](https://devhandbook.io) or reach out on socials.*
