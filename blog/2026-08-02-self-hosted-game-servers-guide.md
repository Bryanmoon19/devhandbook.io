---
layout: post.njk
title: "Self-Hosted Game Servers: The Complete 2026 Guide"
date: 2026-08-02
description: "Extend your *arr stack to games. romarr for acquisition, Pterodactyl and friends for management, and the networking know-how to expose it all safely. With Proxmox sizing for Minecraft, Valheim, Palworld, and CS2."
tags: ["homelab", "self-hosting", "gaming", "docker", "proxmox", "game-servers", "ptero", "pvp", "romarr"]
---

You've automated your media. Sonarr grabs shows, Radarr grabs movies, Prowlarr indexes, Bazarr handles subtitles, Jellyfin serves it all to your TV. The whole pipeline runs on a Proxmox box in your closet, and you haven't paid a streaming subscription in three years.

Now automate your games.

The same homelab that streams your library can run a Minecraft realm for 20 friends, a Valheim world that never wipes, a Palworld server that doesn't shut down at 3 AM, and a CS2 match server for your Discord crew. No Nitro server fees. No monthly $30 "premium" hosting tiers. No "your world was archived because no one logged in for 30 days" emails.

This is the next evolution of the *arr lifestyle. Here's how to build it.

---

## The Missing Piece: romarr

The *arr stack is great at movies and TV. It's *terrible* at games. Sonarr doesn't understand ROMs. Radarr has no clue what a CIA file is. Until recently, your options for automating game acquisition were a maze of sketchy torrent sites, hand-curated 1fichier links, and a USB drive you labeled "GameCube ISOs."

Then **romarr** showed up.

[romarr](https://github.com/romarr/romarr) (⭐7, fresh out of the gate) is the *arr for game ROMs. It looks and feels exactly like Sonarr: search, add, download, organize, integrate. The UI is unmistakably *arr — same green accents, same calendar view, same library grid. It plugs into your existing indexers via the Newznab/Torznab protocols you already use for Prowlarr, so the same Usenet providers and torrent trackers that feed your media stack can feed your game library.

What it does well:

- **Multi-platform support** — Switch, 3DS, PS1/PS2/PSP, GameCube, Wii, GBA, GBC, NDS, MAME, and growing
- **IGDB metadata** — proper cover art, release dates, region info, descriptions
- **Same automation patterns** — quality profiles, release preferences, automatic imports
- **Direct integration with game server panels** — this is the key. It can push ROMs straight to a Pterodactyl or Pelican server.

What it doesn't do yet (be honest with yourself):

- **Maturity** — Sonarr has 10+ years of bug fixes. romarr has months. Expect sharp edges.
- **Console firmware/keys** — you're still on your own for that
- **DLC and updates** — patch management is still manual

For retro and emulation use cases, romarr fills a real gap. For modern PC games, you don't need it — SteamCMD and your game server panel handle that. But for building out the full *arr-for-games experience, romarr is the missing first piece.

```
┌──────────────┐    indexers     ┌──────────────┐
│   Prowlarr   │ ───────────────▶│    romarr    │
│  (Prowlarr)  │                 │  (acquire)   │
└──────────────┘                 └──────┬───────┘
                                        │ organizes
                                        ▼
                                 ┌──────────────┐
                                 │  Game Library │
                                 │  (Pterodactyl)│
                                 └──────────────┘
```

---

## Game Server Panels: Picking Your Cockpit

romarr gets the files. The panel runs the servers. This is where you spend your time after the initial setup.

### The Big Three

| Panel | Stack | Active Devs | Game Support | Setup Complexity | Best For |
|-------|-------|-------------|--------------|------------------|----------|
| **Pterodactyl** | PHP + Node | 2-3 | 200+ (community eggs) | Medium | Production, friends' servers, mature ecosystem |
| **Pelican** | Python + TS | Active | 200+ (Pterodactyl egg compatible) | Medium | If you want AGPL and modern codebase |
| **Mc-manage-panel** (⭐67) | Node.js | New | Minecraft-focused | Low | Pure Minecraft households, single-purpose |

### Pterodactyl

The 800-lb gorilla. Pterodactyl has been around since 2017 and has the largest egg library (pre-configured server templates) of any panel. If you run a popular game, there's already an egg. If you run an obscure game, you'll write a custom egg in 20 minutes.

**Pros:** Mature, well-documented, huge community, supports both Docker and Wings (bare-metal) nodes, robust per-server resource limits.

**Cons:** PHP backend is dated, license changed (now a weird "Pterodactyl-Panel and Pterodactyl-Community-Fork" split), and the project governance has been rocky. Most people now use the **community fork** ([pelican-eggs compatible](https://github.com/pelican-eggs/yolks)).

**Setup:**
```bash
# Panel on a Proxmox LXC
apt install -y docker.io docker-compose
mkdir -p /opt/pterodactyl && cd /opt/pterodactyl
curl -L https://github.com/pterodactyl-installer/pterodactyl-installer/releases/latest/download/pterodactyl-installer -o install.sh
bash install.sh --panel
```

### Pelican

Pelican is the spiritual successor to Pterodactyl. Same UI, same egg format, but rewritten in Python (FastAPI) + TypeScript with AGPL licensing. If you're starting fresh today, Pelican is the right call. It imports Pterodactyl eggs, locations, and nodes via migration scripts.

**Pros:** Active development, modern stack, AGPL, same ecosystem as Pterodactyl, no licensing drama.

**Cons:** Younger, fewer tutorials, the migration from Pterodactyl is one-way.

### Mc-manage-panel

[Mc-manage-panel](https://github.com/mc-manage-panel/mc-manage-panel) (⭐67) is purpose-built for Minecraft. If your household runs nothing but Minecraft and you don't want a generic game panel, this is leaner. It's Node.js, has a clean web UI, and the setup is genuinely 10 minutes.

**Pros:** Lightweight, fast, opinionated for Minecraft (modpacks, Forge, Fabric, Paper, Velocity, BungeeCord).

**Cons:** Minecraft only. No Valheim, no Palworld, no CS2.

### Honorable Mentions

- **DockPanel** — Docker-native, very new, no production use yet
- **AMP (Application Management Panel)** by Cubecoders — paid, Windows-first, not homelab-friendly
- **Crafty Controller** — Minecraft-only, very lightweight, good for a single server

**My take:** Run Pterodactyl (or Pelican if you're starting clean) on a Proxmox VM with 4GB RAM. It runs the panel. Then add separate LXC containers or VMs as "Wings" nodes for the actual game servers. Don't try to run the panel and game servers on the same box.

---

## Networking: Exposing Servers Without Getting Owned

This is where most homelabbers either give up or shoot themselves in the foot. Game servers are weird because:

1. The **web panel** needs to be reachable to manage remotely
2. The **game traffic** (UDP) needs to be reachable by clients
3. You **do not** want to expose random ports to the open internet

### The Two-Layer Pattern

```
   ┌──────────────────────────────────────────────┐
   │  Internet                                     │
   └────────┬──────────────────────────┬──────────┘
            │ HTTPS (CF Tunnel)        │ UDP (direct, port-forwarded)
            ▼                          ▼
   ┌──────────────────┐        ┌──────────────────┐
   │ Cloudflare Edge  │        │  Your Router     │
   └────────┬─────────┘        │  (port forward)  │
            │                  └────────┬─────────┘
            ▼                           ▼
   ┌──────────────────┐        ┌──────────────────┐
   │ pterodactyl.     │        │ Game Server      │
   │ yourdomain.com   │        │ (Proxmox LXC)    │
   │  :443 via tunnel │        │ :25565 / :2456 / │
   └──────────────────┘        │ :27015 (UDP)     │
                               └──────────────────┘
```

### Web Panel: Always Cloudflare Tunnel

The Pterodactyl/Pelican web UI goes through a **Cloudflare Tunnel**. Zero exceptions. This is covered in detail in [Cloudflare Tunnels: Expose Your Homelab Without Opening a Single Port](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/), but the short version:

```yaml
# ~/.cloudflared/config.yml on your tunnel host
tunnel: <your-tunnel-id>
credentials-file: /root/.cloudflared/<your-tunnel-id>.json

ingress:
  - hostname: pterodactyl.yourdomain.com
    service: http://192.168.7.50:80
  - service: http_status:404
```

You also get Cloudflare Access for free — add an email OTP or Authentik in front and only your friends get in.

### Game Traffic: Direct UDP Forwarding

Game traffic doesn't go through Cloudflare. It can't — these are real-time UDP streams, often 10-50ms latency-sensitive, and Cloudflare's HTTP-only proxy will tank your ping. For each game, you port forward one or two UDP ports:

| Game | Default Port | Protocol |
|------|--------------|----------|
| Minecraft (Java) | 25565 | TCP |
| Minecraft (Bedrock) | 19132 | UDP |
| Valheim | 2456-2457 | UDP |
| Palworld | 8211 | UDP |
| CS2 | 27015 | UDP |
| Satisfactory | 7777 | UDP |

Port forward from your router to the Proxmox LXC IP. Lock it down to the game traffic only — no wide port ranges, no accidental public exposure of your Plex server.

**Static IP for the LXC:**
```bash
# /etc/network/interfaces on the LXC
auto eth0
iface eth0 inet static
  address 192.168.7.55/24
  gateway 192.168.7.1
  dns-nameservers 1.1.1.1 8.8.8.8
```

**CGNAT check:** If your ISP puts you behind CGNAT (most do now), port forwarding won't work. Verify with `curl ifconfig.me` and compare to your router's WAN IP. If they differ, you need a VPS relay (expensive, laggy) or a friend with real IP space to tunnel through.

### Reverse Proxies: Skip Them

You might be tempted to put Nginx Proxy Manager in front of Pterodactyl. Don't. Cloudflare Tunnel already does TLS termination, DDoS protection, and Access auth. NPM is an extra hop, an extra config surface, and an extra thing to break. The only time you need a reverse proxy is if you're running the panel on a non-standard port and the tunnel can't reach it — just use the tunnel's `service` field with the port number directly.

---

## Hardware: What You Actually Need

The dirty secret of self-hosted game servers: most games are shockingly light. The first time you spin up a Minecraft server and see it happily serving 5 players on 1GB of RAM, you'll wonder why Nitrado charged you $15/month for the same.

### Per-Game Sizing (Real-World)

| Game | Players | RAM | CPU | Disk | Network |
|------|---------|-----|-----|------|---------|
| Minecraft (vanilla) | 5 | 2 GB | 1 vCPU | 5 GB | 5 Mbps |
| Minecraft (modded) | 10 | 6-8 GB | 2 vCPU | 10 GB | 10 Mbps |
| Valheim | 5-10 | 2-3 GB | 2 vCPU | 3 GB | 5 Mbps |
| Palworld | 4-8 | 8-12 GB | 2 vCPU | 5 GB | 10 Mbps |
| CS2 | 10 | 4-6 GB | 2 vCPU | 20 GB | 15 Mbps |
| Satisfactory | 4 | 8 GB | 2 vCPU | 10 GB | 10 Mbps |

**Rules of thumb:**

- **CPU matters more than RAM** for most games. Game servers are single-threaded or weakly multi-threaded. A Ryzen 5 with high single-core boost clock beats a server Xeon with 16 weak cores.
- **Disk is rarely the bottleneck.** SSD helps load times; NVMe is overkill.
- **Upload bandwidth is the silent killer.** Most home connections have asymmetric upload (300/20, 1000/50). 5-6 active game players can saturate 20 Mbps.

### Proxmox Layout

Three approaches, ranked by my preference:

**1. LXC containers (recommended for most games)** — Games like Valheim, CS2, Palworld, and Minecraft run great in privileged LXCs with `nesting=1`. Fast boot, low overhead, easy backups.

```bash
# Create a Valheim LXC
pveam update
pveam available | grep ubuntu
pveam download local ubuntu-24.04-standard_24.04-2_amd64.tar.zst
pct create 200 local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst \
  --hostname valheim \
  --memory 3072 \
  --cores 2 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.7.55/24,gw=192.168.7.1 \
  --features nesting=1 \
  --unprivileged 0
pct start 200
```

**2. VMs (for games that need full kernels)** — Some games (older Source engine stuff, certain anti-cheat) want a real kernel. Or you want ZFS snapshots for easy rollback. VMs are heavier but more isolated.

**3. Bare metal (for a single heavy server)** — If you're running a heavily modded Minecraft realm for 50+ players or a Palworld server with persistent worldgen, dedicating a whole N100 mini-PC or old NUC to it is fine. ~$150-200 for a used NUC beats any cloud offering.

---

## The Full Stack: docker-compose for the Panel

Here's a working `docker-compose.yml` for running Pterodactyl panel alongside your existing media stack. Drop this on a Proxmox LXC with 4GB RAM, and you've got a game server control plane.

```yaml
# /opt/pterodactyl/docker-compose.yml
version: '3.8'

services:
  panel:
    image: ghcr.io/pterodactyl/panel:latest
    container_name: pterodactyl
    restart: unless-stopped
    ports:
      - "80:80"   # Fronted by Cloudflare Tunnel, no direct exposure
      - "443:443"
    environment:
      APP_URL: "https://pterodactyl.yourdomain.com"
      APP_TIMEZONE: "America/New_York"
      APP_ENVIRONMENT_ONLY: "true"
      DB_HOST: "db"
      DB_PORT: "3306"
      DB_DATABASE: "panel"
      DB_USERNAME: "pterodactyl"
      DB_PASSWORD: "${DB_PASSWORD}"
      CACHE_DRIVER: "redis"
      REDIS_HOST: "redis"
      MAIL_DRIVER: "smtp"
      MAIL_HOST: "${MAIL_HOST}"
      MAIL_PORT: "587"
      MAIL_USERNAME: "${MAIL_USER}"
      MAIL_PASSWORD: "${MAIL_PASS}"
      MAIL_ENCRYPTION: "tls"
      MAIL_FROM: "noreply@yourdomain.com"
    volumes:
      - ./data/var:/app/var
      - ./data/nginx:/etc/nginx/http.d
      - ./data/certs:/etc/letsencrypt
      - ./data/logs:/app/storage/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: mariadb:10.11
    container_name: pterodactyl-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: "${DB_ROOT_PASSWORD}"
      MYSQL_DATABASE: "panel"
      MYSQL_USER: "pterodactyl"
      MYSQL_PASSWORD: "${DB_PASSWORD}"
    volumes:
      - ./data/db:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: pterodactyl-redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  wings:
    image: ghcr.io/pterodactyl/yolks:latest
    container_name: pterodactyl-wings
    restart: unless-stopped
    # Don't expose ports here — Pterodactyl assigns per-server ports dynamically
    # and binds them to the host
    ports:
      - "8080:8080"   # Wings daemon API
      - "2022:2022"   # SFTP
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /srv/daemon:/srv/daemon
      - /etc/pterodactyl:/etc/pterodactyl
    environment:
      TZ: "America/New_York"
```

The `wings` container runs on each game server host. Your Proxmox LXC for Valheim runs its own Wings, your Minecraft LXC runs its own, and they all register with the central panel.

The full pipeline now looks like:

```
Prowlarr → romarr → Pterodactyl Panel → Wings (LXC) → Game Server
                ↓           ↓
         Game Library   Cloudflare Tunnel
         (NFS/SMB)      (panel.yourdomain.com)
                              ↓
                       Direct UDP Forward
                              ↓
                          Players
```

---

## The Homelab Is the Ultimate Gaming Platform

Streaming services made us pay monthly for access to media we don't own. Game hosting services do the same — $15-30/month for a Minecraft realm, $20-50/month for a Valheim server, plus per-player fees on some platforms. Add it up for a friend group of 10 playing 3 games and you're at $1,200+/year.

Your homelab runs the same servers for the marginal cost of electricity. The hardware is already there. The Docker patterns are already there. The networking knowledge is already there. You've literally already built the hardest part.

The next time a friend asks "where should I host our Minecraft server," the answer isn't a paid provider. It's your Proxmox box, a Pterodactyl panel, and a Cloudflare Tunnel.

No subscriptions. No limits. No servers archived because nobody logged in for 30 days.

Just games. On your terms. Forever.

---

**Build the full stack:** [Cloudflare Tunnels](/blog/2026-07-26-cloudflare-tunnels-homelab-guide/) for the panel, [Proxmox LXC](/blog/2026-06-03-portainer-alternatives-proxmox-lxc/) for the game hosts, and your existing *arr stack for everything else.
