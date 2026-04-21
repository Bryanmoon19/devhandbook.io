---
layout: post.njk
title: "WireGuard + Pi-hole: The Complete Privacy Stack for Your Homelab"
date: 2026-04-21
description: "Set up a self-hosted WireGuard VPN with network-wide ad blocking via Pi-hole. One Docker Compose file, ten minutes, and your entire network gets privacy and security."
tags: ["wireguard", "pihole", "vpn", "dns", "privacy", "self-hosted", "homelab", "docker", "networking"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/wireguard-pihole-complete-privacy-stack"
---

Every device on your network — phones, laptops, smart TVs, even your fridge — is leaking DNS queries and browsing data to ISPs, advertisers, and whoever else is listening. The solution isn't another browser extension or paid VPN subscription. It's two open-source tools running on hardware you already own.

WireGuard handles the encrypted tunnel. Pi-hole handles the ad blocking and DNS filtering. Together they form the privacy foundation every homelab should have. I've been running this stack for three years across two locations. Total cost: the electricity to run a single LXC container.

This guide gives you the complete setup — one Docker Compose file, proper network configuration, and split tunneling for when you only want certain traffic going through the VPN.

## What You're Building

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Your Device   │────▶│  WireGuard VPN  │────▶│    Internet     │
│  (Phone/Laptop) │     │   (Your Server) │     │   (Encrypted)   │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │    Pi-hole      │
                          │  (DNS Filter)   │
                          └─────────────────┘
```

**What this gets you:**
- **Encrypted traffic** from any network (coffee shop, airport, cellular) back to your home server
- **Network-wide ad blocking** — every device on your home network benefits, not just the ones with browser extensions
- **DNS privacy** — your ISP can't see what domains you're querying
- **Remote access** to homelab services without exposing them to the internet
- **Split tunneling** — route only specific traffic through the tunnel

## Prerequisites

- A server with Docker and Docker Compose (a Proxmox LXC works perfectly)
- A public IP address or dynamic DNS (Cloudflare, DuckDNS, or similar)
- UDP port 51820 forwarded through your router
- 10 minutes

## Step 1: The Complete Docker Compose Stack

This single compose file deploys both services with proper networking:

```yaml
# docker-compose.yml
services:
  wireguard:
    image: linuxserver/wireguard:latest
    container_name: wireguard
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    environment:
      - PUID=1000
      - PGID=1000
      - SERVERURL=your-domain.com
      - SERVERPORT=51820
      - PEERS=phone,laptop,tablet,tv
      - PEERDNS=10.13.13.5
      - INTERNAL_SUBNET=10.13.13.0
      - ALLOWEDIPS=0.0.0.0/0, ::/0
      - PERSISTENTKEEPALIVE_PEERS=all
    volumes:
      - ./wireguard-config:/config
      - /lib/modules:/lib/modules:ro
    ports:
      - "51820:51820/udp"
    sysctls:
      - net.ipv4.conf.all.src_valid_mark=1
    restart: unless-stopped
    networks:
      vpn-net:
        ipv4_address: 10.13.13.2

  pihole:
    image: pihole/pihole:latest
    container_name: pihole
    environment:
      - TZ=America/New_York
      - WEBPASSWORD=your-admin-password
      - SERVERIP=10.13.13.5
      - DNSMASQ_LISTENING=all
    volumes:
      - ./pihole/etc-pihole:/etc/pihole
      - ./pihole/etc-dnsmasq.d:/etc/dnsmasq.d
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "8080:80/tcp"
    cap_add:
      - NET_ADMIN
    restart: unless-stopped
    networks:
      vpn-net:
        ipv4_address: 10.13.13.5
    dns:
      - 127.0.0.1
      - 1.1.1.1

networks:
  vpn-net:
    driver: bridge
    ipam:
      config:
        - subnet: 10.13.13.0/24
```

**Key configuration details:**

- `PEERDNS=10.13.13.5` tells WireGuard clients to use Pi-hole for DNS resolution
- `INTERNAL_SUBNET=10.13.13.0` creates a dedicated network for VPN clients
- Pi-hole gets a static IP (`10.13.13.5`) so WireGuard can always find it
- Port 53 is exposed for DNS — this is what enables network-wide ad blocking

Create the directories:

```bash
mkdir -p wireguard-config pihole/etc-pihole pihole/etc-dnsmasq.d
```

Start the stack:

```bash
docker compose up -d
```

## Step 2: Router Configuration

### Port Forwarding

Forward UDP port 51820 on your router to your server's internal IP. Every router is different, but the pattern is:

1. Log into your router admin panel
2. Find Port Forwarding or Virtual Servers
3. Create a new rule:
   - **External port:** 51820
   - **Internal IP:** Your server's IP (e.g., 192.168.1.100)
   - **Internal port:** 51820
   - **Protocol:** UDP

### Dynamic DNS (if you don't have a static IP)

If your ISP changes your IP address, set up dynamic DNS:

**Cloudflare (recommended):**
```bash
# Using cloudflared or a DDNS client
docker run -d \
  --name ddns \
  -e CF_API_TOKEN=your-token \
  -e ZONE=your-domain.com \
  -e SUBDOMAIN=vpn \
  oznu/cloudflare-ddns
```

**DuckDNS (free alternative):**
```bash
curl -k https://www.duckdns.org/update/yoursubdomain/yourtoken/$(curl -s ifconfig.me)
```

Add to crontab for every 5 minutes:
```bash
*/5 * * * * curl -k -o /dev/null https://www.duckdns.org/update/yoursubdomain/yourtoken/$(curl -s ifconfig.me)
```

## Step 3: Client Configuration

WireGuard client configs are generated automatically in `./wireguard-config/`:

```
wireguard-config/
├── peer_phone/
│   ├── peer_phone.conf      # Import this into the WireGuard app
│   ├── peer_phone.png       # QR code for easy mobile setup
│   └── privatekey-peer_phone
├── peer_laptop/
│   ├── peer_laptop.conf
│   └── ...
└── ...
```

### Mobile Setup (iOS / Android)

1. Install the WireGuard app
2. Tap the **+** button → **Create from QR code**
3. Scan the QR code from `peer_phone.png`
4. Activate the tunnel

### Desktop Setup (macOS / Windows / Linux)

1. Install WireGuard from [wireguard.com/install](https://www.wireguard.com/install/)
2. Click **Import tunnel from file**
3. Select `peer_laptop.conf`
4. Activate the tunnel

### Test Your Connection

With the tunnel active, visit [dnsleaktest.com](https://dnsleaktest.com). You should see:
- Your server's IP address (not your ISP's)
- DNS servers pointing to your Pi-hole or Cloudflare (not your ISP's DNS)

## Step 4: Pi-hole Configuration

Access the Pi-hole admin panel at `http://your-server:8080/admin`.

### Initial Setup

1. Log in with the password from `WEBPASSWORD`
2. Go to **Group Management → Adlists**
3. Add these recommended blocklists:
   - `https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts` (comprehensive)
   - `https://mirror1.malwaredomains.com/files/justdomains` (malware protection)
   - `https://sysctl.org/cameleon/hosts` (tracking protection)

4. Click **Update Gravity** to download the lists

### Custom DNS Upstream

By default, Pi-hole forwards to your router's DNS. Change this for better privacy:

1. **Settings → DNS**
2. Uncheck your router's DNS
3. Check **Cloudflare** (1.1.1.1) or **Quad9** (9.9.9.9)
4. Save

Cloudflare is faster. Quad9 blocks more malware. Both are privacy-focused.

### Local DNS Records

Map your homelab services to friendly names:

1. **Local DNS → DNS Records**
2. Add entries like:
   - `plex.homelab` → `192.168.1.50`
   - `nas.homelab` → `192.168.1.10`
   - `proxmox.homelab` → `192.168.1.100`

Now you can access services by name instead of memorizing IPs.

## Step 5: Network-Wide Ad Blocking (Optional but Recommended)

Want every device on your home network to benefit from Pi-hole, not just VPN clients?

### Option A: Set Pi-hole as Your Router's DNS

1. Log into your router
2. Find DHCP or DNS settings
3. Set the primary DNS server to your Pi-hole's IP (`192.168.1.100` or whatever your server IP is)
4. Set secondary DNS to something else (Cloudflare, Google) as fallback

**Note:** Some routers force their own DNS. If yours does, use Option B.

### Option B: Per-Device DNS Configuration

On devices where you can set DNS manually:
- **iOS:** Settings → Wi-Fi → [Your Network] → Configure DNS → Manual → Add Server → Your Pi-hole IP
- **Android:** Settings → Network → Private DNS → Enter hostname (if using DNS-over-TLS) or set per-WiFi
- **Windows:** Control Panel → Network → Adapter Settings → IPv4 Properties → DNS
- **macOS:** System Settings → Network → [Connection] → DNS

## Step 6: Split Tunneling

Not all traffic needs to go through your VPN. Split tunneling lets you route only specific traffic through the tunnel while everything else uses your normal connection.

### Common Split Tunnel Configurations

**Route only homelab traffic:**
```ini
[Peer]
AllowedIPs = 10.13.13.0/24, 192.168.1.0/24
```
This sends only your VPN subnet and home network through the tunnel. Everything else (Netflix, general browsing) uses your regular connection.

**Route everything except streaming:**
```ini
[Peer]
AllowedIPs = 0.0.0.0/0
# Then exclude streaming IPs (complex, requires routing tables)
```

**Exclude specific apps (mobile):**
On iOS and Android, WireGuard supports per-app tunneling in the app settings.

### Why Split Tunnel?

- **Performance:** Your home upload speed becomes the bottleneck for all traffic
- **Streaming:** Netflix, Hulu, and others block VPN IPs
- **Latency:** Gaming through a VPN adds unnecessary lag
- **Local services:** Some apps need your real IP for location or device discovery

## Advanced: Multi-Location Setup

If you have servers in multiple locations, you can create a mesh:

```
┌─────────────┐         ┌─────────────┐
│  Home Lab   │◄───────►│  VPS /      │
│  (Pi-hole)  │ WireGuard│  Remote Lab  │
└─────────────┘         └─────────────┘
```

Both locations share the same Pi-hole DNS and can reach each other's services by internal IP. Configure this by adding multiple `[Peer]` sections to your WireGuard configs.

## Security Considerations

### Keep WireGuard Updated

```bash
docker compose pull && docker compose up -d
```

Run this monthly or automate it with Watchtower:

```yaml
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 86400 --cleanup
```

### Firewall Rules

On your server, restrict WireGuard to only necessary ports:

```bash
# UFW example
ufw allow 51820/udp
ufw allow 8080/tcp  # Pi-hole web interface (restrict to LAN if possible)
ufw deny 53/tcp     # Don't expose DNS to the internet
ufw deny 53/udp
```

### Pi-hole Admin Password

Change it regularly:
```bash
docker exec pihole pihole -a -p newpassword
```

## Troubleshooting

### "Handshake did not complete"

- Check that UDP 51820 is forwarded correctly
- Verify `SERVERURL` matches your dynamic DNS or static IP
- Check firewall rules on the server
- Test with `wg show` inside the container:
  ```bash
  docker exec wireguard wg show
  ```

### "DNS resolution fails when connected"

- Verify `PEERDNS=10.13.13.5` is set in the WireGuard container
- Check that Pi-hole is running: `docker logs pihole`
- Test DNS directly: `dig @10.13.13.5 google.com`

### "Some sites don't load"

- Check Pi-hole query log for blocked domains
- Whitelist domains that break functionality:
  ```bash
  docker exec pihole pihole -w cdn.example.com
  ```
- Some sites use anti-adblock — you may need to whitelist specific CDNs

### "Slow speeds through VPN"

- Your home upload speed is the cap. Most ISPs offer 10-50 Mbps upload.
- Use split tunneling to route only necessary traffic
- Check CPU usage on the server — WireGuard is efficient but very slow CPUs can bottleneck

## When to Use Something Else

This stack isn't for everyone. Consider alternatives if:

- **You need multi-hop VPNs** for serious anonymity → Use Mullvad or ProtonVPN
- **You're bypassing geo-blocks** for streaming → Commercial VPNs have better IP diversity
- **You need dedicated IPs** → Most residential connections don't offer this
- **Your upload speed is under 10 Mbps** → The VPN will feel slow for all traffic

For privacy-conscious homelab operators who want control over their data, this stack is unbeatable.

## Conclusion

WireGuard + Pi-hole is the foundational privacy stack every homelab should have. For the cost of a single container's worth of electricity, you get:

- Encrypted connections from anywhere
- Network-wide ad and tracker blocking
- DNS privacy from your ISP
- Remote access to all your services
- Complete control over your network traffic

The setup takes 10 minutes. The peace of mind lasts as long as you maintain it.

**Resources:**
- [WireGuard Official Site](https://www.wireguard.com/)
- [Pi-hole Documentation](https://docs.pi-hole.net/)
- [linuxserver/wireguard Docker Hub](https://hub.docker.com/r/linuxserver/wireguard)
- [Pi-hole Docker Guide](https://github.com/pi-hole/docker-pi-hole)

---

*Running a different VPN or DNS setup? Found a clever blocklist or split tunnel config? Share it in the [Discord](https://discord.gg/selfhosted) — always curious how people are securing their networks.*
