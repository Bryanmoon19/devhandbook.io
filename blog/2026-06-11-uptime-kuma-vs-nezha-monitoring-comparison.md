---
layout: post.njk
title: "Uptime Kuma vs Nezha Dashboard: The Self-Hosted Monitoring Showdown You Actually Need"
date: 2026-06-11
description: "Two titans of self-hosted monitoring go head-to-head. Uptime Kuma has 87K+ stars. Nezha is the rising star from China with 10K+ stars and a web terminal. Here's which one deserves your homelab."
tags: ["uptime-kuma", "nezha", "monitoring", "self-hosted", "homelab", "docker", "proxmox", "comparison", "devops"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/uptime-kuma-vs-nezha-monitoring-comparison"
---

You know the feeling. You wake up, check your phone, and realize Jellyfin has been down since 3 AM. Nobody told you. Your users — which is to say, your family — are sending passive-aggressive texts about "the TV thing not working again."

This is why we monitor things. And in the self-hosted world, two tools have emerged as the dominant choices for "I just need to know when stuff breaks": **Uptime Kuma**, the beloved veteran with 87,000+ GitHub stars, and **Nezha Dashboard**, the rising star from China that's gained 10,000+ stars and a cult following for its sleek interface and built-in web terminal.

I've run both for the past month on my Proxmox homelab. They're both excellent. But they solve slightly different problems, and choosing the wrong one will cost you either flexibility or simplicity. Here's the breakdown.

## What Each Tool Actually Does

Before the comparison, let's clarify what we're comparing. These aren't apples to apples — they're more like apples to really nice pears.

**Uptime Kuma** is a service monitoring tool. It checks if your websites, APIs, containers, and servers are responding. It's focused on *availability* — is this thing up or down? — with beautiful status pages you can share with users.

**Nezha Dashboard** is a server monitoring and operations platform. It tracks system resources (CPU, memory, disk, network) across your fleet, with a real-time dashboard, alerts, and a built-in web terminal for remote management. It's focused on *performance* and *operations*.

The overlap: both can notify you when things break. The difference: Uptime Kuma checks from the outside ("can I reach this service?"), while Nezha reports from the inside ("how hard is this server working?").

## Head-to-Head Comparison

| Feature | Uptime Kuma | Nezha Dashboard |
|---------|-------------|-----------------|
| **Primary Focus** | Service uptime / availability | Server resources / performance |
| **Monitoring Types** | HTTP, TCP, Ping, Docker, Steam, DNS, Push | System metrics, HTTP, TCP, Ping, SSL |
| **Star Count** | 87,855 (June 2026) | 10,115 (June 2026) |
| **Resource Usage** | ~150MB RAM | ~80MB RAM (agent + dashboard) |
| **Status Pages** | Built-in, multiple, custom domains | Via community themes |
| **Notifications** | 90+ services (Telegram, Discord, Email, etc.) | Telegram, Discord, Slack, Pushover, webhook |
| **Web Terminal** | ❌ No | ✅ Built-in SSH via browser |
| **Auto Discovery** | Docker containers | Docker containers |
| **Alerting Complexity** | Simple thresholds | Simple thresholds |
| **Multi-Language** | 20+ languages | Chinese + English + community |
| **SSL Monitoring** | Certificate expiry | Certificate expiry + change detection |
| **Mobile Experience** | Responsive web UI | Responsive web UI |
| **API** | REST API | gRPC + REST |

## Uptime Kuma: The Status Page Champion

Uptime Kuma has earned its 87,000+ stars honestly. Louis Lam built something that just *works*, and the community has kept it polished.

### What Makes It Special

**Status pages are first-class citizens.** You can create multiple status pages, map them to custom domains, add logos, and customize the layout. This matters if you're running services that other people depend on — family media servers, community tools, or client projects.

**The notification ecosystem is unmatched.** Ninety-plus notification services means whatever you're already using — Telegram, Discord, Pushover, Matrix, even Minecraft server webhooks — Uptime Kuma talks to it natively. No Zapier required.

**Push monitoring** is a clever feature. Instead of Uptime Kuma polling a service, the service sends a heartbeat. Perfect for cron jobs, backup scripts, or anything that runs on a schedule. Miss a heartbeat, get an alert. Simple.

**Steam Game Server monitoring** exists because Louis is clearly a gamer who got annoyed his friends couldn't tell when the Valheim server was up. This specificity — solving real problems for real people — is why Uptime Kuma thrives.

### Quick Uptime Kuma Setup

```yaml
# docker-compose.yml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:2
    container_name: uptime-kuma
    ports:
      - "3001:3001"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Deploy, visit `http://your-server:3001`, create your account, and start adding monitors. The UI guides you through everything.

### Where Uptime Kuma Falls Short

It doesn't monitor *system resources*. You can see if Plex is responding, but not whether your server's CPU is pegged at 100% or if the disk is filling up. For that, you need something else — or Uptime Kuma + a resource monitor.

The status pages, while beautiful, are also a commitment. If you publish one and your monitoring goes down, people notice. Running Uptime Kuma for public status pages means you now need to monitor your monitoring.

## Nezha Dashboard: The Operator's Dream

Nezha (哪吒) is named after a Chinese mythological figure, and like its namesake, it's surprisingly powerful for something so lightweight. Built by naiba and a growing community, it brings a different philosophy to monitoring.

### What Makes It Special

**The built-in web terminal is a killer feature.** Click into any monitored server from your browser and get a working SSH session. No VPN, no port forwarding, no remembering which key goes where. For homelab operators managing 5-10 servers across different networks, this alone justifies the setup.

**Real-time resource tracking** shows CPU, memory, disk, and network for every agent-connected server, updated every few seconds. The default dashboard is gorgeous — dark mode, smooth graphs, system temperatures if sensors are available.

**SSL certificate monitoring goes beyond expiry.** Nezha detects certificate *changes*, which is how you'll catch a misconfigured reverse proxy or a Let's Encrypt renewal that went sideways before users start seeing browser warnings.

**Scheduled tasks** let you run commands across your fleet from the dashboard. Update all agents, clean Docker volumes, restart services — without logging into each box.

### Quick Nezha Setup

Nezha uses a hub-and-spoke model like Beszel. The dashboard is the hub; agents run on each monitored host.

**Step 1: Deploy the Dashboard**

```yaml
# docker-compose.yml
services:
  nezha-dashboard:
    image: nezhahq/nezha:v2
    container_name: nezha-dashboard
    ports:
      - "8008:8008"
    volumes:
      - ./data:/data
    restart: unless-stopped
```

**Step 2: Deploy the Agent**

```yaml
# docker-compose.yml on monitored host
services:
  nezha-agent:
    image: nezhahq/agent:v2
    container_name: nezha-agent
    environment:
      - NZ_SERVER=your-dashboard-ip:8008
      - NZ_SECRET=your-secret-key-from-dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /proc:/proc:ro
      - /sys:/sys:ro
    restart: unless-stopped
```

Grab the secret from the Nezha dashboard under **System → Agents → Add Agent**.

### Where Nezha Falls Short

The English documentation is functional but not comprehensive. You'll occasionally find yourself translating Chinese README sections or checking the Telegram community for answers.

Status pages require community themes. The default installation gives you an admin dashboard and a user-facing dashboard, but creating public status pages means installing a separate frontend theme like [nezha-dash](https://github.com/hamster1963/nezha-dash). It's not hard, but it's an extra step Uptime Kuma handles natively.

Notification channels are more limited. You get Telegram, Discord, Slack, Pushover, and webhooks — enough for most people, but not the 90+ services Uptime Kuma supports.

## The Real Question: What Are You Actually Monitoring?

This is the decision framework that matters.

**Choose Uptime Kuma if:**
- You need public or private status pages
- You're monitoring websites, APIs, and services from the outside
- You want the broadest notification support
- You're checking "is this thing up?" more than "how hard is this server working?"
- You want something that works perfectly in 20 minutes

**Choose Nezha if:**
- You're managing multiple servers and need resource visibility
- You want a web terminal for remote access
- You're tracking system performance, not just service availability
- You need SSL certificate change detection
- You want scheduled task execution across your fleet
- You're comfortable with slightly rougher English docs

**Choose Both if:**
- You have a real homelab (not a Raspberry Pi with two containers)
- You want status pages for users AND resource monitoring for yourself
- You can spare ~230MB RAM total (150MB for Kuma + 80MB for Nezha)

This is what I run. Uptime Kuma handles the public-facing "is Plex up?" questions. Nezha tells me which Proxmox LXC is about to run out of disk space. They complement each other like coffee and spite.

## My Current Stack: How They Play Together

On my Proxmox host (192.168.7.134), I have:

- **Uptime Kuma** in LXC 1003 (media tools container) — monitors Jellyfin, Navidrome, *arr apps, and the blog
- **Nezha Dashboard** in LXC 1002 (TeslaMate container, since it has resources to spare) — monitors all LXCs plus the Proxmox host itself
- **Beszel** on a dedicated 512MB LXC — tracks long-term trends and sends alerts when baselines drift

Yes, that's three monitoring tools. No, I'm not sorry. Each does something the others don't, and together they give me complete visibility without the resource drain of Prometheus + Grafana.

## Resource Comparison on Proxmox LXC

I tested both on identical 512MB LXC containers:

| Metric | Uptime Kuma | Nezha Dashboard |
|--------|-------------|-----------------|
| **RAM (idle)** | 145MB | 72MB |
| **RAM (under load)** | 180MB | 95MB |
| **CPU (idle)** | 1-2% | 0.5-1% |
| **Disk** | 200MB | 120MB |
| **Startup Time** | 8s | 5s |
| **Agent RAM (per host)** | N/A (self-contained) | 25MB |

Both run comfortably in 512MB LXCs. Nezha is lighter, especially if you're already running the dashboard elsewhere and just adding agents.

## Advanced: Running Behind a Reverse Proxy

**Nginx Proxy Manager:**

For Uptime Kuma:
- Forward `status.yourdomain.com` to `http://uptime-kuma:3001`
- Enable WebSocket support (required for real-time status updates)

For Nezha:
- Forward `nezha.yourdomain.com` to `http://nezha-dashboard:8008`
- Enable WebSocket support (required for the real-time dashboard)
- The web terminal uses WebSocket as well — don't forget this

**Caddy:**
```
status.yourdomain.com {
    reverse_proxy localhost:3001
}

nezha.yourdomain.com {
    reverse_proxy localhost:8008
}
```

**Cloudflare Tunnel** (if you want zero-config public access without opening ports):
```bash
cloudflared tunnel --no-autoupdate run --token YOUR_TOKEN
# Map status.yourdomain.com → localhost:3001
# Map nezha.yourdomain.com → localhost:8008
```

## Migration Path: Switching From One to the Other

If you're currently running one and wondering about the other:

**Uptime Kuma → Nezha:** You'll lose status pages unless you set up a community theme. You'll gain resource monitoring and web terminals. Export your monitor list from Kuma and recreate in Nezha — there's no automatic migration.

**Nezha → Uptime Kuma:** You'll lose resource monitoring and web terminals. You'll gain native status pages and broader notifications. The agent model is completely different, so you'll uninstall Nezha agents and set up Uptime Kuma monitors from scratch.

**The smart move:** Run both for a month, see which one you actually check, then decide if the other provides enough unique value to keep.

## Final Verdict

Uptime Kuma and Nezha aren't competitors. They're colleagues who happen to work in the same building.

Uptime Kuma is for the "is my stuff online?" question. It's polished, mature, and has the best status pages in the self-hosted world. If you have users who need to know when your services are down, Kuma is the answer.

Nezha is for the "what's happening inside my servers?" question. The web terminal alone saves me 10 minutes a day of SSH context-switching. The real-time resource tracking catches problems before they become outages.

If you're running a single Raspberry Pi with AdGuard and Plex, Uptime Kuma is probably enough. If you're managing a multi-LXC Proxmox fleet with separate networks for media, automation, and IoT, Nezha adds real operational value.

And if you're like me — running enough services that "monitoring the monitoring" is a genuine concern — you'll appreciate having both.

**Resources:**
- [Uptime Kuma GitHub](https://github.com/louislam/uptime-kuma)
- [Uptime Kuma Demo](https://demo.kuma.pet/start-demo)
- [Nezha Dashboard GitHub](https://github.com/nezhahq/nezha)
- [Nezha English Documentation](https://nezhahq.github.io/en_US/index.html)
- [Nezha Community Themes](https://github.com/hamster1963/nezha-dash)

---

*Running Uptime Kuma, Nezha, or both in your homelab? Found a clever integration I missed? Let me know in the [Discord](https://discord.gg/selfhosted) — I'm always curious how people are keeping tabs on their setups.*