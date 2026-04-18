---
layout: post.njk
title: "Beszel: The Lightweight Monitoring Stack Your Homelab Actually Needs"
date: 2026-04-18
description: "Why I migrated from Prometheus + Grafana to Beszel for homelab monitoring. A simpler, faster, and more resource-efficient approach to keeping tabs on your servers."
tags: ["beszel", "monitoring", "grafana", "prometheus", "homelab", "self-hosted", "docker", "proxmox"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/beszel-lightweight-monitoring"
---

I used to run Prometheus, Grafana, and a half-dozen exporters just to see if my containers were healthy. It worked. But it also consumed 2GB of RAM, required constant query tuning, and felt like using a sledgehammer to check a pulse.

Then I found Beszel.

Beszel is a lightweight, modern monitoring stack built specifically for the "I just want to know if things are working" crowd. After running it alongside my Prometheus setup for a month, I made the switch permanent. Here's why it might be the monitoring tool your homelab has been waiting for.

## What Is Beszel?

Beszel is an open-source monitoring solution that combines a lightweight agent with a clean web dashboard. It's designed for small-to-medium deployments — think homelabs, small VPS fleets, or a few Docker hosts — where full observability platforms feel like overkill.

**The pitch:**
- **Single binary** for the agent (or one Docker container)
- **Pre-built dashboard** — no query writing required
- **Automatic service discovery** for Docker containers
- **Alerts via Discord, Slack, Telegram, or webhook**
- **Minimal resource usage** (~50MB RAM vs Prometheus's 1GB+)

## The Problem with Prometheus in Homelabs

Don't get me wrong — Prometheus and Grafana are powerful. They're also powerful enough to be frustrating:

| Aspect | Prometheus Stack | Beszel |
|--------|-----------------|--------|
| **Memory** | 1-2GB+ for basic setup | ~50MB |
| **Configuration** | YAML, scrape configs, recording rules | Environment variables |
| **Query language** | PromQL (steep learning curve) | None needed |
| **Dashboard setup** | Build from scratch or import | Works out of the box |
| **Alerting** | Alertmanager + routing trees | Built-in, simple |

For a homelab with 5-10 services, Prometheus often creates more work than it saves. You're maintaining a monitoring system *and* the things it's supposed to monitor.

## Setting Up Beszel

Beszel runs as a hub-and-spoke model. The **hub** is the web dashboard and data store. The **agents** run on each host you want to monitor.

### Step 1: Deploy the Hub

The hub stores metrics and serves the web UI. SQLite is the default database — no external dependencies needed.

```yaml
# docker-compose.yml
services:
  beszel-hub:
    image: henrygd/beszel-hub:latest
    container_name: beszel-hub
    ports:
      - "8090:8090"
    volumes:
      - ./beszel-data:/data
    environment:
      - BESZEL_PORT=8090
      - BESZEL_DB=/data/beszel.db
    restart: unless-stopped
```

Deploy and visit `http://your-server:8090`. Create your admin account on first launch.

### Step 2: Add Agents

On each host you want to monitor, run the Beszel agent:

```yaml
# docker-compose.yml on monitored host
services:
  beszel-agent:
    image: henrygd/beszel-agent:latest
    container_name: beszel-agent
    environment:
      - BESZEL_KEY=your-public-key-from-hub
      - BESZEL_HUB=http://your-hub-ip:8090
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /proc:/proc:ro
      - /sys:/sys:ro
    restart: unless-stopped
```

The `BESZEL_KEY` comes from the hub dashboard — click "Add System" and copy the key.

**Note:** The Docker socket mount enables automatic container discovery. Remove it if you only want host-level metrics.

### Step 3: Proxmox LXC Setup

For Proxmox LXCs, you have two options:

**Option A: Privileged LXC with nesting**
```bash
# On Proxmox host
pct set <vmid> -features nesting=1
```

Then deploy the Docker agent normally.

**Option B: Binary install (no Docker)**
```bash
# Inside the LXC
wget https://github.com/henrygd/beszel/releases/latest/download/beszel-agent-linux-amd64.tar.gz
tar -xzf beszel-agent-linux-amd64.tar.gz
sudo mv beszel-agent /usr/local/bin/

# Create systemd service
sudo nano /etc/systemd/system/beszel-agent.service
```

```ini
[Unit]
Description=Beszel Agent
After=network.target

[Service]
ExecStart=/usr/local/bin/beszel-agent -key your-key -hub http://your-hub:8090
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now beszel-agent
```

## What You Get Out of the Box

Once agents connect, the dashboard shows:

- **CPU usage** (per-core and aggregate)
- **Memory utilization** with breakdown (used, cached, buffers)
- **Disk usage** per mount point
- **Network I/O** with bandwidth graphs
- **Docker containers** — status, CPU, memory per container
- **System temperature** (if sensors available)

All with 1-minute resolution and 30-day retention by default.

## Configuring Alerts

Beszel's alerting is refreshingly simple. In the dashboard:

1. Go to **Settings → Notifications**
2. Add your Discord webhook, Slack URL, or Telegram bot token
3. Set thresholds per system:
   - CPU > 80% for 5 minutes
   - Memory > 90%
   - Disk > 85%
   - Container down

No routing trees. No silence configurations. Just "tell me when something breaks."

Example Discord notification:
```
🚨 Alert: plex-server
CPU usage: 94% (threshold: 80%)
Duration: 6 minutes
```

## Real-World Migration: My Setup

I migrated a 5-host homelab from Prometheus to Beszel over a weekend:

**Before:**
- Prometheus + Alertmanager + Grafana: 3 containers, ~1.5GB RAM
- Node exporter on 5 hosts
- cAdvisor for Docker metrics
- Custom dashboards I never quite finished

**After:**
- Beszel hub: 1 container, ~80MB RAM
- Beszel agent: 1 container per host, ~30MB each
- Working dashboards immediately
- Alerts that actually made sense

**Time to full migration:** 3 hours including testing.

## When to Stick with Prometheus

Beszel isn't a wholesale replacement for every use case. Keep Prometheus if:

- You need **long-term metric retention** (years, not weeks)
- You're doing **complex aggregations** across hundreds of hosts
- You need **custom business metrics** (application-level, not just infrastructure)
- Your team already **knows PromQL** and has built dashboards

For everyone else — especially homelab operators with 2-20 hosts — Beszel removes complexity you probably don't need.

## Advanced: Running Beszel Behind a Reverse Proxy

If you want HTTPS and a custom domain:

**Nginx Proxy Manager:**
- Forward `beszel.yourdomain.com` to `http://beszel-hub:8090`
- Enable Websocket support (required for live updates)

**Traefik:**
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.beszel.rule=Host(`beszel.yourdomain.com`)"
  - "traefik.http.routers.beszel.tls.certresolver=letsencrypt"
  - "traefik.http.services.beszel.loadbalancer.server.port=8090"
  - "traefik.http.routers.beszel.middlewares=auth@file"  # optional basic auth
```

**Caddy:**
```
beszel.yourdomain.com {
    reverse_proxy localhost:8090
}
```

## Conclusion

Monitoring shouldn't be a second job. Beszel proves you can have visibility into your homelab without running a full observability platform.

If you're currently maintaining a Prometheus stack just to check if Plex is up, give Beszel a try. The 30 minutes you spend setting it up will save you hours of dashboard tuning and query debugging.

**Resources:**
- [Beszel GitHub](https://github.com/henrygd/beszel)
- [Official Documentation](https://beszel.dev)
- [Docker Hub](https://hub.docker.com/r/henrygd/beszel-hub)

---

*Running Beszel in your homelab? Found a clever integration? Drop a note in the [Discord](https://discord.gg/selfhosted) — always curious how people are monitoring their setups.*
