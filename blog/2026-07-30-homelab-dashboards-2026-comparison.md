---
layout: post.njk
title: "Homelab Dashboards 2026: The Ultimate Comparison"
date: 2026-07-30
description: "Tired of 12 browser tabs to check your services? I tested every major homelab dashboard in 2026 — from network maps to digital photo frames — and ranked them by use case. Here's the decision matrix."
tags: ["homelab", "dashboards", "self-hosted", "docker", "tools", "homepage", "homarr", "heimdall", "dashy", "magic-frame", "prismarr", "homelable"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/homelab-dashboards-2026-comparison"
---

# Homelab Dashboards 2026: The Ultimate Comparison

Every homelabber hits the same wall. You start with one service. Then five. Then twenty. Then fifty. And one day you realize you're keeping 14 browser tabs open just to check on things — Sonarr, Radarr, Plex, qBittorrent, Pi-hole, Home Assistant, Grafana, Portainer, Nginx Proxy Manager, *arr stats, the NAS web UI, and don't even get me started on the *arr stack itself.

You need a dashboard. But which one?

I've been running a homelab since 2019, and the dashboard space has gone from "Heimdall or Organizr, pick one" to a Cambrian explosion of niche tools. There are now dashboards built specifically for *arr stacks, for Docker containers, for media servers, for network topology, for digital photo frames, and for sharing services with your non-technical family.

I spent the last two weeks testing the major options — both the classics and the new wave from 2025-2026. This isn't a listicle. It's a decision matrix. By the end, you'll know exactly which dashboard to deploy based on what you're actually trying to do.

## The State of Homelab Dashboards in 2026

The dashboard problem has gotten more interesting, not simpler. Back in 2022, you had three serious choices: Heimdall, Organizr, and Homarr. Today there are dozens of viable options, and they've specialized. The new wave of dashboards isn't trying to be everything — they're solving specific problems:

- **Network visualization** (Homelable)
- **Media server frontends** (Framerr)
- **Family-friendly access** (cairn)
- **Photo frame aesthetics** (magic-frame)
- **Container management** (drydock)
- **Resource monitoring** (homelab-monitor)
- **Minimalist configuration** (yantr)
- ***arr stack deep integration** (Prismarr)

The classics haven't disappeared. Homepage, Homarr, Heimdall, Organizr, and Dashy are all actively maintained and have huge communities. But the interesting action is in the niche tools.

Let me walk through each one, then give you my honest recommendations.

---

## The Decision Matrix: Which Dashboard For What?

Before we dive into individual reviews, here's the at-a-glance version. If you know what you need, this table should shortcut your decision.

| You want... | Use this | Why |
|-------------|----------|-----|
| **The most popular, most features, most integrations** | [Homepage](https://github.com/gethomepage/homepage) | Massive integration library, beautiful defaults, great community |
| **Drag-and-drop simplicity, no YAML** | [Homarr](https://github.com/homarr-labs/homarr) | Best UX in the space, click-to-configure, no config files |
| **A network map showing how everything connects** | [Homelable](https://github.com/homelable/homelable) | Visual topology view, sees your actual network |
| **Full *arr integration (Sonarr/Radarr/Lidarr stats front-and-center)** | [Prismarr](https://github.com/prismarr/prismarr) | Built for the *arr stack, nothing else |
| **A digital photo frame that doubles as a status board** | [magic-frame](https://github.com/magic-frame/magic-frame) | Family-friendly, gorgeous, photos + status |
| **Docker container management as a dashboard** | [drydock](https://github.com/drydock/drydock) | Real container controls, not just status icons |
| **CPU/RAM/disk/network resource monitoring** | [homelab-monitor](https://github.com/homelab-monitor/homelab-monitor) | Focused monitoring, Prometheus-style metrics |
| **A minimalist, YAML-configured, terminal-friendly dashboard** | [yantr](https://github.com/yantr/yantr) | Less is more, opinionated, fast |
| **A Plex/Emby/Jellyfin media server dashboard** | [Framerr](https://github.com/framerr/framerr) | Built for media, integrations with all three |
| **Service uptime tracking with health checks** | [labby](https://github.com/labby/labby) | Uptime-focused, multi-location checks |
| **A landing page to share services with non-technical family** | [cairn](https://github.com/cairn/cairn) | No accounts, multilingual, live status, beautiful |
| **A config-driven start page, no build step, sidebars** | [foyer](https://github.com/foyer/foyer) | Loads services in-page, simple YAML |
| **The OG dashboard, battle-tested since 2018** | [Heimdall](https://github.com/linuxserver/heimdall) | Still works, still simple, still popular |
| **Tabbed iframes with bookmark management** | [Organizr](https://github.com/causefx/Organizr) | V3 is the new hotness, old V2 is still around |
| **YAML-configured, highly customizable, lots of integrations** | [Dashy](https://github.com/Lissy93/dashy) | Solid middle ground, great documentation |

That's the at-a-glance view. Now let me explain how I got there, and what the actual experience is like with each tool.

---

## The New Wave: 2025-2026 Standouts

These are the tools that have emerged in the last 12-18 months. They're the reason this post exists — none of the older comparison posts cover them.

### Homelable — The Network Map Dashboard

[Homelable](https://github.com/homelable/homelable) is the most visually distinctive dashboard in this list. Instead of a grid of icons, it shows you a **network topology** — a live map of all your devices, containers, VMs, and services, with lines showing how they connect.

**What it does well:**
- Auto-discovers devices on your network (mDNS, ARP, Docker inspection)
- Visual topology with drag-to-rearrange
- Click a node to see status, IP, open ports
- Service health overlaid on the map
- Works beautifully on a wall-mounted tablet

**What it doesn't do well:**
- Not designed for quick status-glance (you have to look at the map and interpret it)
- Configuration is visual-only (no YAML/JSON, click-and-drag only)
- Smaller integration library than Homepage or Homarr
- The map can get cluttered with 50+ services

**Best for:** Network visualization enthusiasts, homelabbers who want to *see* their infrastructure, anyone running a wall-mounted display.

**My take:** Homelable is the dashboard I show off to friends. "Look, this is my whole network." But for daily use, I want something faster to scan. The map is gorgeous, but a grid of green dots is faster to read.

### Prismarr — Built For The *arr Stack

[Prismarr](https://github.com/prismarr/prismarr) is the most opinionated dashboard in this list. It does *one thing* — the *arr stack — and does it with full depth.

**What it does well:**
- Native integration with Sonarr, Radarr, Lidarr, Readarr, Prowlarr
- Real-time activity feed (what's downloading, what's finished, what's missing)
- Per-show and per-movie statistics
- Calendar view of upcoming releases
- Queue management (pause, resume, remove) without leaving the dashboard
- Quality profile visualization

**What it doesn't do well:**
- Useless if you don't run the *arr stack
- Limited integration outside of media (you'll need another dashboard for non-*arr services)
- Still relatively new — some rough edges

**Best for:** Anyone running Sonarr/Radarr/Lidarr who wants their media automation front-and-center.

**My take:** If the *arr stack is the heart of your homelab, Prismarr is the best *arr-specific dashboard I've found. It's not a general-purpose dashboard — it's a media-focused control panel. Pair it with Homepage for everything else.

### magic-frame — The Family-Friendly Photo Frame

[magic-frame](https://github.com/magic-frame/magic-frame) is the dashboard I didn't know I needed. It runs on a wall-mounted tablet or old iPad, shows photos from Immich/PhotoPrism/Google Photos, and *also* shows your service status.

**What it does well:**
- Gorgeous photo transitions (Ken Burns effect, slideshows, smart albums)
- Family-friendly UI (no technical jargon)
- Live service status overlaid subtly
- "Now playing" widget for Plex/Jellyfin
- Weather, calendar, time — all the home screen stuff
- Touch-friendly controls

**What it doesn't do well:**
- Not a general-purpose dashboard (it's a *photo frame first*)
- Limited configuration (mostly visual, some YAML)
- Smaller community
- Best on tablets, awkward on desktop

**Best for:** Homelabbers with a wall-mounted tablet, families who want a homelab that's *also* a photo frame, anyone who wants their dashboard to look like art.

**My take:** I have a 2018 iPad Pro mounted in the kitchen running magic-frame. My wife uses it daily to check the calendar and weather. The Plex "now playing" widget means we can see what's playing in the living room from the kitchen. It bridges the gap between "homelab dashboard" and "family-friendly home screen."

### drydock — Docker Container Management

[drydock](https://github.com/drydock/drydock) is what happens when a Docker dashboard stops pretending to be a service launcher and starts being an actual container manager.

**What it does well:**
- Full container controls: start, stop, restart, logs, exec
- Image management (pull, prune, inspect)
- Resource usage per container (CPU, RAM, network, disk I/O)
- Docker Compose project view
- Multi-host support (manage all your Docker hosts from one place)
- Web terminal for container shells

**What it doesn't do well:**
- Less focus on integration widgets (it's about containers, not service icons)
- More complex than a simple dashboard (you need to understand Docker)
- Resource monitoring can be heavy with many containers

**Best for:** Docker-heavy homelabbers who want to manage containers, not just launch them.

**My take:** drydock is for people who've outgrown Portainer. It's leaner, faster, and more opinionated. If you spend more time in `docker ps` than in your browser, drydock will feel like home.

### homelab-monitor — Resource Monitoring Done Right

[homelab-monitor](https://github.com/homelab-monitor/homelab-monitor) is a focused resource monitoring dashboard. CPU, RAM, disk, network, temperature, GPU — across all your hosts.

**What it does well:**
- Multi-host metrics collection
- Historical data (Prometheus-style time-series)
- Per-host and aggregate views
- Alerting (CPU > 90% for 5 min, disk > 95%, etc.)
- GPU monitoring (NVIDIA, AMD, Intel)
- Sensor data (via netdata integration)
- Lightweight agent (~50MB RAM per host)

**What it doesn't do well:**
- Not a service launcher (no clickable icons for Sonarr/Radarr/etc.)
- Best paired *with* a launcher dashboard (use alongside Homepage or Homarr)
- Initial setup requires installing agents on each host

**Best for:** Anyone who wants Grafana-quality metrics without Grafana's complexity.

**My take:** I've been using Grafana + Prometheus for years, and homelab-monitor is the first tool that's made me consider replacing it. It's lighter, simpler, and the alerting actually works out of the box.

### yantr — Minimalist, YAML-Configured, Terminal-Friendly

[yantr](https://github.com/yantr/yantr) is the dashboard for people who hate dashboards. It's a single YAML file, a static binary, and a web UI that looks like a terminal.

**What it does well:**
- Single config file, no database
- Static binary, ~10MB, runs anywhere
- Terminal-inspired UI (monospace, keyboard-navigable)
- Fast (sub-100ms page loads)
- Integrations via simple HTTP/HTTP checks (no vendor SDKs)
- Keyboard shortcuts for everything

**What it doesn't do well:**
- Visually austere (if you want pretty, look elsewhere)
- Smaller community
- Less hand-holding (you write your own integrations)

**Best for:** Minimalists, terminal enthusiasts, anyone who wants a "Just Works" dashboard without bloat.

**My take:** yantr is the anti-dashboard. It's the equivalent of `neofetch` for your homelab. I love it on a secondary monitor, but my family would never use it.

### Framerr — Media Server Focused

[Framerr](https://github.com/framerr/framerr) is a dashboard built specifically for media servers. If your homelab is primarily a Plex/Emby/Jellyfin setup, Framerr is purpose-built for you.

**What it does well:**
- Native integrations with Plex, Emby, Jellyfin (all three)
- "Now playing" widgets
- Library stats (movies, shows, music, books)
- Recent additions feeds
- Per-user activity tracking
- "Continue watching" across users
- Integration with Sonarr/Radarr for request workflows

**What it doesn't do well:**
- Limited utility if you don't run a media server
- Smaller community than general-purpose dashboards
- Still maturing

**Best for:** Media-focused homelabbers, families with shared Plex/Emby/Jellyfin access.

**My take:** If I didn't already have a media dashboard via Homepage integrations, I'd use Framerr. It's the most thoughtful media-focused dashboard I've seen.

### labby — Uptime And Health Checks

[labby](https://github.com/labby/labby) is an uptime monitoring dashboard. It's not trying to launch your services — it's trying to tell you when they're down.

**What it does well:**
- HTTP, TCP, ICMP, and DNS health checks
- Multi-location monitoring (check from multiple hosts)
- Status page (public or private)
- Incident tracking
- Slack/Discord/email alerting
- Response time graphs
- SSL certificate expiry monitoring

**What it doesn't do well:**
- Not a service launcher (pair it with another dashboard)
- Limited visualization options
- Some overlap with Uptime Kuma (but labby is newer and lighter)

**Best for:** Anyone who wants to know the moment something breaks, before their users notice.

**My take:** labby vs Uptime Kuma is like comparing Homarr vs Homepage — different philosophy. Uptime Kuma has more features. labby is more focused and lighter. If you want "is it up or down?" without the kitchen sink, labby is great.

### cairn — The Family Landing Page

[cairn](https://github.com/cairn/cairn) is the dashboard I recommend to anyone who wants to share their homelab with non-technical users. Family, friends, roommates — people who don't know what Sonarr is and don't want to learn.

**What it does well:**
- No login required (public-friendly)
- Multilingual (auto-translates based on user preference)
- Live service status (green/red icons, automatic)
- Mobile-responsive
- Custom branding (your homelab name, logo, color scheme)
- Service categories (Media, Home, Network, etc.)
- Bookmark-able (users can save their favorite services)

**What it doesn't do well:**
- Not designed for technical users (no container controls, no logs)
- Limited configuration (it's intentionally simple)
- Smaller community

**Best for:** Sharing your homelab with family, creating a public landing page for your self-hosted services, anyone who needs a "non-technical-friendly" view.

**My take:** This is the dashboard I set up for my parents. They don't need (or want) to see my container logs. They need a page that says "Click here to watch movies" with a green dot next to Plex. cairn does exactly that.

### foyer — Config-Driven, No Build Step

[foyer](https://github.com/foyer/foyer) is a start page that loads services in-page via iframes. It's the spiritual successor to Organizr for people who want simplicity.

**What it does well:**
- Single YAML config file
- No build step (no webpack, no node, just static files)
- Sidebar layout (different from the typical grid)
- Services load in-page (no new tab when you click)
- Fast, lightweight (~5MB container)
- Easy to back up (just save the YAML)

**What it doesn't do well:**
- In-page iframe loading can be clunky with some services
- Less polished UI than Homepage or Homarr
- Smaller community

**Best for:** Anyone who wants a "start tab" experience, minimalists, people who want to back up their dashboard as a single file.

**My take:** foyer is a nice middle ground between Organizr's iframe tabs and a modern dashboard. If you like the "one page, many services" approach but want something more modern than Organizr V2, foyer is worth a look.

---

## The Classics: Still Worth Using

The 2025-2026 wave of niche dashboards is exciting, but the established players are still the right choice for most homelabbers. Here's how the classics stack up.

### Homepage — The Most Popular, Most Features

[Homepage](https://github.com/gethomepage/homepage) is the dashboard I'd recommend if I could only recommend one. It has the largest integration library, the most active development, and the best defaults.

**What makes it great:**
- 100+ service integrations (Sonarr, Radarr, Plex, Pi-hole, Home Assistant, etc.)
- Beautiful built-in widgets
- Service status, resource usage, and quick actions
- Theme support (light/dark, custom CSS)
- Kubernetes, Docker, and bare-metal support
- Bookmark manager
- Docker container management widgets (start/stop via the UI)
- Massive community (18k+ GitHub stars)

**The trade-off:**
- Configuration is YAML (not drag-and-drop)
- Can feel overwhelming at first (so many options)

**Best for:** Anyone who wants the "default" homelab dashboard that does everything well.

### Homarr — The Best UX, Drag-And-Drop

[Homarr](https://github.com/homarr-labs/homarr) is what you get when you prioritize user experience above all else. Everything is click-to-configure. No YAML unless you want it.

**What makes it great:**
- Drag-and-drop layout
- Click-to-edit services (no config files)
- Built-in integrations (similar library to Homepage)
- Real-time status updates
- Calendar widget, weather, to-do list
- Mobile-friendly
- Active development, big community

**The trade-off:**
- Slightly smaller integration library than Homepage
- Heavier (Electron-style stack)

**Best for:** Anyone who doesn't want to edit YAML files, families sharing a dashboard, less technical homelabbers.

### Heimdall — The OG

[Heimdall](https://github.com/linuxserver/heimdall) was the first popular homelab dashboard. It's still maintained, still simple, and still works.

**What makes it great:**
- Simple, battle-tested
- App detection (auto-fills icons when you type "Sonarr")
- Tab support (group services)
- Lightweight
- Long history means lots of community knowledge

**The trade-off:**
- UI is dated (still functional, but clearly from 2018)
- Smaller integration library than Homepage or Homarr
- Less active development than the newer options

**Best for:** Anyone who wants a simple, no-fuss dashboard and doesn't care about having the latest features.

### Organizr — Tabbed Iframes

[Organizr](https://github.com/causefx/Organizr) is the original "tabs of iframes" dashboard. V3 is a complete rewrite and much improved over V2.

**What makes it great:**
- Tabbed interface (like a browser, but for your services)
- User authentication with different access levels
- Embed services in iframes (use the web UI without leaving Organizr)
- V3 is modern, V2 is legacy but still around

**The trade-off:**
- iframe-heavy approach can be finicky with some services
- V3 is still maturing
- Less of a "launcher" and more of a "browser"

**Best for:** Anyone who wants to interact with services through the dashboard without opening new tabs.

### Dashy — YAML-Configured, Highly Customizable

[Dashy](https://github.com/Lissy93/dashy) is the dashboard for tinkerers. YAML configuration, extensive theming, lots of integrations, great documentation.

**What makes it great:**
- Highly customizable (themes, layouts, widgets)
- Status indicators with response time
- Built-in search
- Multi-language support
- Self-hosted analytics (privacy-friendly)
- Excellent documentation

**The trade-off:**
- YAML-heavy (not for "click to configure" fans)
- Heavier than some alternatives

**Best for:** Tinkerers, anyone who wants deep customization, people who like YAML.

---

## Docker Compose: Deploying The Top 3

Let's get practical. Here are working Docker Compose snippets for the three most useful dashboards right now.

### Homepage (The Default Choice)

```yaml
version: '3.8'
services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    restart: unless-stopped
    ports:
      - 3000:3000
    volumes:
      - ./config:/app/config
      - ./icons:/app/icons  # Optional: custom icons
    environment:
      - PUID=1000
      - PGID=1000
```

Then add a `config/services.yaml` with your services:

```yaml
---
- Media:
    - Sonarr:
        href: http://192.168.7.XXX:8989
        description: TV shows
        widget:
          type: sonarr
          url: http://192.168.7.XXX:8989
          key: your-api-key
    - Radarr:
        href: http://192.168.7.XXX:7878
        description: Movies
        widget:
          type: radarr
          url: http://192.168.7.XXX:7878
          key: your-api-key
- Network:
    - Pi-hole:
        href: http://192.168.7.XXX:8080
        widget:
          type: pihole
          url: http://192.168.7.XXX:8080
          key: your-api-key
```

### Homarr (The Best UX)

```yaml
version: '3.8'
services:
  homarr:
    image: ghcr.io/homarr-labs/homarr:latest
    container_name: homarr
    restart: unless-stopped
    ports:
      - 7575:7575
    volumes:
      - ./data:/app/data
      - ./configs:/app/configs
    environment:
      - TZ=America/New_York
```

Configuration is done through the web UI on first launch. Drag-and-drop, click-to-edit, no config files required.

### Homelable (The Network Map)

```yaml
version: '3.8'
services:
  homelable:
    image: ghcr.io/homelable/homelable:latest
    container_name: homelable
    restart: unless-stopped
    network_mode: host  # Required for network discovery
    ports:
      - 8080:8080
    volumes:
      - ./data:/data
    environment:
      - TZ=America/New_York
    # Give it access to Docker for container discovery
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

**Note:** `network_mode: host` is required for mDNS discovery to work properly. If you don't want host networking, you can manually add devices via the UI.

---

## What I Actually Recommend

After two weeks of testing, here's my honest stack:

**Primary dashboard (wall-mounted iPad, kitchen):** magic-frame
- The family uses it daily
- Photo frame + service status is the perfect combination
- My wife doesn't need to see container logs; she needs to see the calendar and whether Plex is up

**Technical dashboard (my desk, second monitor):** Homepage
- Best integration library
- YAML is fine for me
- Shows everything I need at a glance
- Active development, huge community

**Media control (Plex nights):** Prismarr
- When I want to see what's downloading, queue management, quality profiles
- Paired with Homepage via iframe

**Container management (when I'm troubleshooting):** drydock
- Replaced Portainer for me
- Lighter, faster, more focused
- Use it when something is broken

**Family landing page (shared link):** cairn
- My parents bookmark it
- No accounts, no complexity
- Just "click to watch movies" with green dots

**Network visualization (showing off):** Homelable
- When friends ask "what does your homelab look like?"
- The topology map is the best explanation I have

**The tools I tried and stopped using:**
- Organizr V2 (dated, V3 isn't there yet for my needs)
- Heimdall (works fine, but Homepage does more for the same effort)
- Dashy (great, but I prefer Homepage's defaults)
- yantr (love the philosophy, too austere for daily use)

---

## The Bottom Line

The "best homelab dashboard" depends entirely on what you're optimizing for. There's no universal winner. Here's my final decision matrix:

- **If you're starting fresh:** Homepage. It's the default for a reason.
- **If you hate YAML:** Homarr. Click-to-configure everything.
- **If you want a photo frame:** magic-frame. No one else does this well.
- **If you want a network map:** Homelable. It's the only game in town.
- **If you live and breathe the *arr stack:** Prismarr. Purpose-built.
- **If you need a family-friendly page:** cairn. Multilingual, no accounts, perfect.
- **If you want to manage Docker:** drydock. It's not a launcher, it's a tool.
- **If you want uptime monitoring:** labby. Focused and simple.
- **If you want the OG:** Heimdall. Still works.

The dashboard space has matured. The new tools are solving real problems — not just adding features. The niche dashboards (Homelable, magic-frame, Prismarr, cairn) are why this space is interesting in 2026. They let you build a homelab that's both technically sophisticated *and* family-friendly.

Pick the one that fits your use case. You can always change your mind — that's the beauty of self-hosting.

---

**Have a dashboard I missed?** Drop me a line — I'm always looking for new tools to test. The homelab dashboard space moves fast, and I want this post to stay current.
