---
layout: post.njk
title: "Route qBittorrent Through a VPN With Gluetun (Kill Switch Included)"
date: 2026-04-11
description: "Self-host qBittorrent inside a Docker VPN tunnel using Gluetun. Complete setup with docker-compose, kill switch configuration, port forwarding, and leak verification."
tags: ["gluetun", "qbittorrent", "docker", "vpn", "self-hosted", "homelab", "privacy", "torrent"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/gluetun-qbittorrent-docker-vpn"
---

Running a torrent client on your home network without a VPN is a privacy risk. Your IP address is visible to every peer in the swarm, and some ISPs actively throttle BitTorrent traffic. The usual fix — a VPN client on your host or router — is awkward for homelab setups. It either routes *everything* through the VPN, or you end up with complex split-tunnel rules that break every time you add a new service.

**Gluetun solves this by putting the VPN inside a Docker container, then routing other containers through it.** qBittorrent gets a dedicated, kill-switched tunnel. The rest of your stack uses your normal connection. If the VPN drops, qBittorrent loses network access instantly — no leaks, no accidental exposure.

This guide covers the full setup: Gluetun configuration, qBittorrent attachment, port forwarding, and how to verify your real IP never appears in the swarm.

## What Gluetun Actually Does

Gluetun is a lightweight Go-based VPN client that runs inside a Docker container. It supports OpenVPN and WireGuard for dozens of providers — NordVPN, Mullvad, ProtonVPN, PIA, AirVPN, and many more. It also includes a built-in HTTP proxy, SOCKS5 proxy, and Shadowsocks server.

**The key feature for this setup is `network_mode: service:gluetun`.** By attaching qBittorrent to Gluetun's network stack, all of qBittorrent's traffic — inbound and outbound — travels through the VPN tunnel. Gluetun becomes the network layer. qBittorrent doesn't even know the VPN exists; it just sees a normal eth0 interface.

## The Complete Docker Compose Stack

Here's a production-ready `docker-compose.yml` for Gluetun + qBittorrent. This example uses **Mullvad** with WireGuard, but the structure is the same for any supported provider.

```yaml
services:
  gluetun:
    image: qmcgaw/gluetun:latest
    container_name: gluetun
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun:/dev/net/tun
    ports:
      - 8080:8080   # qBittorrent WebUI
      - 6881:6881   # qBittorrent torrenting port
      - 6881:6881/udp
    volumes:
      - ./gluetun:/gluetun:ro
    environment:
      - VPN_SERVICE_PROVIDER=mullvad
      - VPN_TYPE=wireguard
      - SERVER_COUNTRIES=Netherlands
      - WIREGUARD_PRIVATE_KEY=${WIREGUARD_PRIVATE_KEY}
      - FIREWALL_OUTBOUND_SUBNETS=192.168.1.0/24  # allow LAN access
    restart: unless-stopped

  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    network_mode: service:gluetun
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
      - WEBUI_PORT=8080
      - TORRENTING_PORT=6881
    volumes:
      - ./qbittorrent/config:/config
      - /mnt/downloads:/downloads
    restart: unless-stopped
    depends_on:
      gluetun:
        condition: service_healthy
```

### Why This Works

- **Gluetun** creates the VPN tunnel and exposes ports `8080` and `6881` on the host.
- **qBittorrent** uses `network_mode: service:gluetun`, so it shares Gluetun's network namespace. It has no independent network access.
- **Port mappings on Gluetun** forward those ports through the tunnel. The VPN server's public IP becomes your "listening" IP for torrents.
- **`depends_on` with `condition: service_healthy`** ensures qBittorrent doesn't start until the VPN is active.

## Provider Configuration Examples

Gluetun supports a long list of providers. Here are quick configs for the most common ones.

### Mullvad (WireGuard)

```yaml
environment:
  - VPN_SERVICE_PROVIDER=mullvad
  - VPN_TYPE=wireguard
  - SERVER_COUNTRIES=Netherlands
  - WIREGUARD_PRIVATE_KEY=${WIREGUARD_PRIVATE_KEY}
```

Get your private key from Mullvad's website: **Settings → WireGuard key**. Paste it into a `.env` file:

```bash
WIREGUARD_PRIVATE_KEY=YOUR_KEY_HERE
```

### ProtonVPN (WireGuard)

```yaml
environment:
  - VPN_SERVICE_PROVIDER=protonvpn
  - VPN_TYPE=wireguard
  - SERVER_COUNTRIES=Netherlands
  - WIREGUARD_PRIVATE_KEY=${WIREGUARD_PRIVATE_KEY}
```

ProtonVPN WireGuard keys are available in your account dashboard under **Downloads → WireGuard configuration**.

### Private Internet Access (OpenVPN)

```yaml
environment:
  - VPN_SERVICE_PROVIDER=private internet access
  - VPN_TYPE=openvpn
  - OPENVPN_USER=${PIA_USER}
  - OPENVPN_PASSWORD=${PIA_PASS}
  - SERVER_REGIONS=Netherlands
```

### NordVPN (OpenVPN)

```yaml
environment:
  - VPN_SERVICE_PROVIDER=nordvpn
  - VPN_TYPE=openvpn
  - OPENVPN_USER=${NORD_USER}
  - OPENVPN_PASSWORD=${NORD_PASS}
  - SERVER_REGIONS=Netherlands
```

For the full provider list and environment variable reference, see the [Gluetun Wiki](https://github.com/qdm12/gluetun-wiki).

## The Kill Switch

Gluetun's kill switch is **automatic and aggressive** — the exact behavior you want. If the VPN connection drops, Gluetun cuts all outbound traffic. Because qBittorrent is inside Gluetun's network namespace, it loses connectivity too.

You don't need to configure the kill switch. It's on by default. But there are a few adjustments worth knowing about:

### Allow Local Network Access

By default, Gluetun blocks all non-VPN traffic. If you want to reach qBittorrent's WebUI from your LAN without routing that traffic through the VPN, add:

```yaml
- FIREWALL_OUTBOUND_SUBNETS=192.168.1.0/24
```

Replace `192.168.1.0/24` with your actual LAN subnet.

### Test the Kill Switch

1. Start the stack: `docker compose up -d`
2. Open qBittorrent's WebUI at `http://your-server-ip:8080`
3. Add a legal torrent (e.g., a Linux ISO) and confirm it downloads
4. Stop the Gluetun container: `docker stop gluetun`
5. Watch qBittorrent's transfer rate drop to zero within seconds
6. Restart Gluetun: `docker start gluetun`
7. Confirm downloads resume once the VPN reconnects

## Port Forwarding and the Listening Port

For healthy torrent speeds, peers need to connect to you. That requires an open listening port. Most VPN providers don't support port forwarding anymore, but a few still do — **Mullvad, PIA, AirVPN, and ProtonVPN (on some plans)**.

### If Your Provider Supports Port Forwarding

1. Request a forwarded port from your VPN provider's dashboard.
2. Set `TORRENTING_PORT=6881` in the qBittorrent environment variables.
3. In qBittorrent's settings (WebUI → Tools → Options → Connection), set the **listening port** to `6881`.
4. Gluetun maps port `6881` through the tunnel. If the VPN provider forwards it, the port test in qBittorrent should show green.

### If Your Provider Doesn't Support Port Forwarding

Torrents will still work, but you'll rely on outbound connections rather than inbound ones. Speeds are usually fine for well-seeded content. Set qBittorrent to **UPnP / NAT-PMP off** and **listening port to a random high port** to reduce noise.

## Verifying Your IP Doesn't Leak

Trust, but verify. Here's how to confirm qBittorrent is actually using the VPN.

### Method 1: Check qBittorrent's Connection IP

Install the **Trackers** tab in qBittorrent and look at the **"IP"** column when downloading. It should show your VPN's exit IP, not your home ISP IP.

### Method 2: Use a Magnet Link Test

Add this magnet link to qBittorrent:

```
magnet:?xt=urn:btih:4E69DC6738EBC4D10B8A79F4A58F18D87E2F9B3B&dn=ipleak.net+test
```

This connects to [ipleak.net](https://ipleak.net)'s torrent leak test. After a few minutes, visit the site and scroll to the **Torrent Address detection** section. The IP shown should match your VPN, not your home connection.

### Method 3: Check Gluetun Logs

```bash
docker logs gluetun -f
```

Look for lines like:

```
INFO [wireguard] Connected
INFO [dns] ready
INFO [healthcheck] healthy
```

If the healthcheck fails, qBittorrent won't start (thanks to `depends_on`). If the VPN drops mid-session, you'll see:

```
WARN [vpn] connection lost
INFO [firewall] blocking all outbound traffic
```

## File Organization and Permissions

qBittorrent downloads to `/mnt/downloads` in the compose example above. Make sure the folder exists and PUID `1000` has write access:

```bash
mkdir -p /mnt/downloads
sudo chown -R 1000:1000 /mnt/downloads
```

Gluetun's config folder only needs to store optional provider files (like OpenVPN `.ovpn` certs for custom providers). For standard providers, it's empty and read-only is fine.

## Restart Behavior and Updates

Set both containers to `restart: unless-stopped`. If your host reboots, Gluetun starts first, establishes the VPN, and then qBittorrent starts. If the VPN connection is unstable, Gluetun will retry automatically.

For updates, run:

```bash
docker compose pull
docker compose up -d
```

qBittorrent will preserve its config and torrent list because `./qbittorrent/config` is bind-mounted.

## Common Issues

### qBittorrent WebUI Is Inaccessible

Make sure `FIREWALL_OUTBOUND_SUBNETS` includes your LAN, or access the WebUI from a device on the same Docker host.

### Torrents Show "Stalled"

Check the VPN connection first: `docker logs gluetun`. Then verify the listening port in qBittorrent matches the Gluetun port mapping (`6881`).

### qBittorrent Starts Before Gluetun Is Ready

The `depends_on` with `condition: service_healthy` requires Docker Compose v3+ and a compatible healthcheck in the Gluetun image (which is included in recent tags). If it still races, add a short delay script or use a reverse proxy that handles container startup gracefully.

### Slow Speeds

Try a different VPN server region. Gluetun's `SERVER_COUNTRIES` and `SERVER_CITIES` variables make this easy. Some providers also support `SERVER_HOSTNAMES` to pick exact endpoints.

## Why This Setup Beats a VPN on the Host

| Approach | Routing Control | Kill Switch | Container Restart Behavior |
|---|---|---|---|
| Host VPN client | All or nothing | Often manual | Disconnects everything on restart |
| Gluetun + container | Per-container | Automatic | qBittorrent waits for VPN, then starts |
| Router VPN | Entire LAN | Varies by router | Doesn't help individual container routing |

Gluetun decouples the VPN from your host. You can run one container through NordVPN, another through Mullvad, and leave the rest of your stack on your normal connection. It's the cleanest way to add privacy to a self-hosted torrent workflow.

## Related Reading

- [What Is Real-Debrid?](/blog/what-is-real-debrid/) — A developer-friendly guide to premium streaming and cached torrents
- [TeslaMate on Proxmox LXC](/blog/teslamate-proxmox-lxc/) — Another Docker-in-LXC stack for your homelab
- [Self-Hosted Weekly](/blog/selfhosted-weekly-2026-03-30/) — Curated tools and updates

---

*Questions or improvements? The source for this post is on [GitHub](https://github.com/bryanmoon19/devhandbook.io). PRs welcome.*
