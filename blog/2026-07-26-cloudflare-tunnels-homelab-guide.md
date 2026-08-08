---
layout: post.njk
title: "Cloudflare Tunnels: Expose Your Homelab Without Opening a Single Port"
date: 2026-07-26
description: "Replace port forwarding, reverse proxies, and dynamic DNS with one Cloudflare Tunnel. Step-by-step guide with Docker, Proxmox, and security hardening."
tags: ["cloudflare", "networking", "security", "self-hosting", "homelab", "docker", "proxmox", "reverse-proxy", "tunnels"]
---

Every homelabber knows the drill: open port 443 on your router, set up Nginx Proxy Manager, configure Let's Encrypt, pray your ISP doesn't block it, and hope you didn't misconfigure something that exposes your Proxmox dashboard to the internet.

There's a better way. **Cloudflare Tunnels** give you a secure, encrypted path from the public internet to your services — without opening a single inbound port. No port forwarding. No dynamic DNS. No reverse proxy config. Just a lightweight daemon (`cloudflared`) running on your server.

I switched my entire homelab to Cloudflare Tunnels six months ago. Here's everything I learned.

---

## Why Cloudflare Tunnels Beat Traditional Port Forwarding

| Approach | Ports Open | Dynamic DNS | TLS Cert | DDoS Protection | ISP Blocking |
|----------|-----------|-------------|----------|-----------------|--------------|
| Port forward + NPM | 80, 443 | Yes | Manual | No | Common |
| Port forward + Caddy | 80, 443 | Yes | Auto | No | Common |
| Tailscale Funnel | 0 | No | Auto | No | No |
| **Cloudflare Tunnel** | **0** | **No** | **Auto** | **Yes (free)** | **No** |

The killer feature isn't just security — it's that Cloudflare's global edge absorbs DDoS attacks, caches your content, and handles TLS termination. Your home IP is never exposed. Your upload bandwidth isn't hammered by bots. And it's completely free.

---

## How It Works (The 30-Second Version)

```
Internet → Cloudflare Edge → cloudflared daemon → Your Service
                ↑ encrypted       ↑ outbound-only
           (TLS termination)   (WebSocket over HTTPS)
```

1. You run `cloudflared` on any machine in your network
2. It makes an **outbound** connection to Cloudflare's edge
3. Cloudflare routes traffic for `your-app.yourdomain.com` through that tunnel
4. Your firewall sees only outbound HTTPS — no inbound ports needed

The `cloudflared` daemon is the only thing that needs to run. It can reach any service on your local network: Docker containers, Proxmox VMs, Raspberry Pis, whatever.

---

## Step 1: Set Up Your Domain on Cloudflare

If you haven't already, point your domain's nameservers to Cloudflare:

1. Sign up at [cloudflare.com](https://cloudflare.com) (free tier is plenty)
2. Add your domain and follow the nameserver change instructions
3. Wait for DNS propagation (usually 5-30 minutes)

Once your domain is active on Cloudflare, you're ready to create tunnels.

---

## Step 2: Install cloudflared

### On Docker (Recommended)

```bash
docker run -d \
  --name cloudflared \
  --restart unless-stopped \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate run \
  --token YOUR_TUNNEL_TOKEN
```

### On Proxmox LXC / Ubuntu

```bash
# Add Cloudflare's package repo
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list

# Install
sudo apt update && sudo apt install cloudflared
```

### On a Mac Mini (Homebrew)

```bash
brew install cloudflare/cloudflare/cloudflared
```

---

## Step 3: Create Your First Tunnel

You can create tunnels two ways: the web dashboard (easier) or the CLI (more control). I recommend the dashboard for most people.

### Via Cloudflare Dashboard (Zero Trust)

1. Go to **Cloudflare Dashboard → Zero Trust → Networks → Tunnels**
2. Click **Create a tunnel**
3. Name it (e.g., `homelab-tunnel`)
4. Choose your environment (Docker, Linux, etc.) — Cloudflare gives you the exact install command with your token
5. Run that command on your server

The tunnel will appear as **HEALTHY** within seconds.

### Via CLI (for automation)

```bash
cloudflared tunnel login          # Opens browser to authorize
cloudflared tunnel create homelab # Creates tunnel, outputs UUID
cloudflared tunnel route dns homelab plex.yourdomain.com
```

---

## Step 4: Route Traffic to Your Services

This is where the magic happens. In the Zero Trust dashboard, go to your tunnel and click **Configure → Public Hostname**.

Add entries like this:

| Subdomain | Domain | Service Type | Service URL |
|-----------|--------|-------------|-------------|
| `plex` | `yourdomain.com` | HTTP | `192.168.1.100:32400` |
| `proxmox` | `yourdomain.com` | HTTPS | `192.168.1.134:8006` |
| `ha` | `yourdomain.com` | HTTP | `192.168.1.46:8123` |
| `portainer` | `yourdomain.com` | HTTP | `192.168.1.202:9443` |

That's it. No Nginx config. No Let's Encrypt cron job. No port forwarding rules. Cloudflare handles TLS automatically with a valid certificate.

**Important:** For services that already use HTTPS (like Proxmox), set "Service Type" to HTTPS and enable "No TLS Verify" in the additional settings. Cloudflare will still terminate TLS at the edge — your internal traffic stays encrypted too.

---

## Step 5: Add Access Control (Optional but Recommended)

Exposing your Proxmox dashboard to the internet without authentication is a bad idea. Cloudflare Zero Trust gives you free access controls:

### Email-Based OTP

1. Go to **Zero Trust → Access → Applications**
2. Click **Add an application** → **Self-hosted**
3. Set the subdomain (e.g., `proxmox.yourdomain.com`)
4. Add a policy: **Allow** → **Emails ending in** → `@yourdomain.com`
5. Save

Now anyone visiting `proxmox.yourdomain.com` must enter their email and receive a one-time code before they see the Proxmox login page. This adds a second layer of authentication before your service even loads.

### GitHub/GitLab/Google SSO

Cloudflare Access supports OAuth with GitHub, Google, Microsoft, and more — all on the free tier. For a personal homelab, email OTP is usually enough.

---

## Advanced: Config File for Multiple Services

If you prefer infrastructure-as-code, use a `config.yml`:

```yaml
tunnel: YOUR_TUNNEL_UUID
credentials-file: /home/user/.cloudflared/YOUR_TUNNEL_UUID.json

ingress:
  # Plex Media Server
  - hostname: plex.yourdomain.com
    service: http://192.168.1.100:32400

  # Home Assistant
  - hostname: ha.yourdomain.com
    service: http://192.168.1.46:8123

  # Proxmox (HTTPS backend)
  - hostname: proxmox.yourdomain.com
    service: https://192.168.1.134:8006
    originRequest:
      noTLSVerify: true

  # Jellyfin
  - hostname: jellyfin.yourdomain.com
    service: http://192.168.1.202:8096

  # Catch-all: deny everything else
  - service: http_status:404
```

Run with:

```bash
cloudflared tunnel --config /etc/cloudflared/config.yml run
```

---

## Docker Compose: The Cleanest Setup

Here's my production `docker-compose.yml` for running cloudflared alongside other services:

```yaml
version: "3.8"

services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared
    restart: unless-stopped
    command: tunnel --no-autoupdate run
    environment:
      - TUNNEL_TOKEN=${CF_TUNNEL_TOKEN}
    networks:
      - proxy
    # No ports exposed — outbound only

  # Example: your other services
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    networks:
      - proxy

networks:
  proxy:
    driver: bridge
```

Store your tunnel token in a `.env` file:

```bash
CF_TUNNEL_TOKEN=eyJhIjoiYWJjZGVm...
```

---

## Real-World Performance

I've been running Cloudflare Tunnels for six months. Here's what I've observed:

**The good:**
- **Zero maintenance.** Once set up, it just works. No cert renewals, no config changes.
- **DDoS protection is real.** Cloudflare's edge absorbs everything. My home connection never sees attack traffic.
- **Faster page loads.** Cloudflare caches static assets at their edge. My blog loads 40% faster through the tunnel than it did through direct port forwarding.
- **ISP changes don't matter.** I switched ISPs last month. New IP address? Didn't touch a single config. The tunnel reconnected automatically.

**The caveats:**
- **Plex streaming bypasses the tunnel.** Cloudflare's Terms of Service prohibit serving video through their proxy (Section 2.8). For Plex, use the tunnel for the web UI but let Plex handle streaming directly. Or use a different domain for media.
- **WebSocket latency.** There's a small (~5-10ms) latency penalty from the extra hop. Not noticeable for web UIs, but real-time applications might feel it.
- **Cloudflare dependency.** If Cloudflare goes down, your services are unreachable. In practice, Cloudflare's uptime is better than my ISP's.

---

## Troubleshooting Common Issues

### "Tunnel shows HEALTHY but I get a 502 Bad Gateway"

The tunnel is connected, but it can't reach your service. Check:
- Is the service actually running? `docker ps` or `systemctl status`
- Is the internal URL correct? Try `curl http://192.168.1.100:32400` from the cloudflared host
- Is there a firewall blocking internal traffic? (Unlikely if cloudflared and the service are on the same Docker network)

### "I get a Cloudflare challenge page (403)"

This means Cloudflare's WAF is blocking the request. Check:
- **Security → Bots** in your Cloudflare dashboard — disable Bot Fight Mode
- **Security → Settings** — set Security Level to "Medium" or "Low"
- **Security → WAF → Custom Rules** — look for any rules blocking your domain

### "My service uses WebSockets and they don't work"

Cloudflare Tunnels support WebSockets natively. No extra config needed. If they're not working, check that your service isn't behind an additional proxy that strips WebSocket headers.

### "I want to expose an SSH server through the tunnel"

Use Cloudflare's browser-based SSH rendering (Zero Trust → Access → Applications → Add → SSH). Or use `cloudflared access ssh` on the client side for a native SSH experience through the tunnel.

---

## When NOT to Use Cloudflare Tunnels

Cloudflare Tunnels are amazing, but they're not for everything:

- **Large file transfers (Plex, Nextcloud).** Cloudflare's ToS prohibits serving non-HTML content disproportionately. Use Tailscale or direct WireGuard for media streaming.
- **Game servers.** The latency penalty and WebSocket overhead make tunnels unsuitable for real-time gaming.
- **You need 100% uptime independent of any third party.** If Cloudflare is unacceptable as a dependency, stick with direct port forwarding + dynamic DNS.

For 90% of homelab services — dashboards, web UIs, blogs, monitoring tools — Cloudflare Tunnels are the best solution available today.

---

## The Bottom Line

Cloudflare Tunnels replaced four things in my homelab:

1. **Port forwarding rules** (gone)
2. **Nginx Proxy Manager** (gone)
3. **Let's Encrypt certbot cron jobs** (gone)
4. **Dynamic DNS updater** (gone)

One `cloudflared` container. Zero inbound ports. Automatic TLS. Free DDoS protection. It's the closest thing to a "set it and forget it" solution I've found in 10 years of homelabbing.

If you're still opening ports on your router, do yourself a favor and switch this weekend. Your firewall will thank you.

---

**Related posts:**
- [Nginx Proxy Manager vs Traefik vs Caddy: Which Reverse Proxy in 2026?](/blog/nginx-proxy-manager-vs-traefik-vs-caddy-2026/)
- [Uptime Kuma vs Nezha: Homelab Monitoring Comparison](/blog/uptime-kuma-vs-nezha-monitoring-comparison/)
- [The Self-Hoster's Guide to DNS: Stop Paying for Dynamic DNS](/blog/self-hosted-dns-guide-2026/)
