---
layout: post.njk
title: "Beyond Uptime Kuma: Advanced Monitoring Patterns That Actually Help You Recover"
date: 2026-06-21
description: "Uptime Kuma tells you when things break. But then what? Here's how to build a monitoring stack that doesn't just alert — it helps you fix problems faster, with real patterns from my homelab."
tags: ["self-hosted", "monitoring", "uptime-kuma", "prometheus", "grafana", "homelab", "docker", "proxmox", "devops"]
author: "Bryan Moon"
canonical: "https://devhandbook.io/blog/advanced-monitoring-patterns-homelab-2026"
---

# Beyond Uptime Kuma: Advanced Monitoring Patterns That Actually Help You Recover

Uptime Kuma is great. I run it. You probably run it. It pings your services every 30 seconds and screams at you when Plex goes down at 2 AM.

But here's the thing: **knowing something is broken is only half the battle.** The other half is figuring out *why* it's broken, *how* to fix it*, and ideally, catching it *before* it breaks.

I've been refining my monitoring stack for a couple of years now. I started with Uptime Kuma like everyone else, then slowly layered on more sophisticated tools. Not because I'm a masochist who loves YAML, but because I got tired of SSHing into boxes at midnight to diagnose problems I could have prevented.

This post is about the patterns that actually matter — the ones that go beyond "is it up or down" and help you understand *what's happening* in your homelab.

---

## The Monitoring Pyramid

Before we dive into tools, let's talk about the hierarchy of monitoring. Most homelabbers start at the bottom and never climb:

| Layer | Question | Typical Tool |
|-------|----------|--------------|
| **Availability** | Is it responding? | Uptime Kuma, Ping |
| **Metrics** | How is it performing? | Prometheus + Grafana |
| **Logs** | What happened? | Loki, Graylog, syslog |
| **Traces** | Where did it break? | Jaeger, Zipkin |
| **Synthetic** | Is the user experience good? | Uptime Kuma (advanced), custom scripts |

Most of us live in Layer 1. This post is about climbing to Layers 2 and 3, with a peek at 4. Layer 5 is mostly overkill for a homelab unless you're running services for other people.

---

## Layer 1: Uptime Kuma Done Right

Before you abandon Uptime Kuma, make sure you're using it well. Most people underutilize it.

### Monitor What Actually Matters

Don't just monitor the homepage. Monitor the actual functionality:

- **Plex:** Monitor `/library/sections` (requires auth token) not just the landing page
- **Nextcloud:** Monitor `/status.php` for JSON response, not just HTTP 200
- **Jellyfin:** Monitor `/System/Info/Public` and check for valid JSON
- **Home Assistant:** Monitor `/api/config` with a long-lived token
- **Immich:** Monitor `/api/server-info` for version and features

Uptime Kuma supports keyword monitoring — use it. A 200 OK with a Cloudflare error page is not "up."

### Use the Right Check Interval

| Service Type | Interval | Reason |
|--------------|----------|--------|
| Public-facing (Plex, Nextcloud) | 30-60s | Fast detection matters |
| Internal tools (Pi-hole, AdGuard) | 2-5 min | Not critical for external users |
| Background jobs (arr stack) | 5-15 min | False positive reduction |
| Development/staging | 15-30 min | Don't waste resources |

Checking everything every 30 seconds creates noise. You'll start ignoring alerts.

### Group Your Monitors Logically

Uptime Kuma supports tags and status pages. Use them:

- **Tag by severity:** `critical` (Plex, HA), `important` (Nextcloud), `nice-to-have` (development tools)
- **Tag by host:** `proxmox-lxc-1002`, `mac-mini`, `nas`
- **Status pages per audience:** One for you (everything), one for family (just Plex and HA)

When a Proxmox host reboots, you'll get 10 alerts if every LXC is monitored individually. Group by host and you'll know it's a host issue, not 10 service issues.

---

## Layer 2: Prometheus + Grafana — The Metrics Foundation

Uptime Kuma tells you *that* something broke. Prometheus tells you *what was happening* when it broke.

### What I Monitor

My Prometheus stack (running in Docker on the Mac Mini) collects:

- **Node metrics** — CPU, RAM, disk, network, temperature (via node_exporter)
- **Container metrics** — CPU/RAM per container, restart counts, network I/O (via cadvisor)
- **Docker host metrics** — Engine health, image sizes, volume usage
- **Application metrics** — Database query times, HTTP response codes, queue depths
- **Smart data** — Disk health from the NAS (via smartctl_exporter)

### Key Dashboards I Actually Use

#### 1. The "At a Glance" Dashboard

A single Grafana panel showing:
- All hosts: green/yellow/red status
- Total CPU usage across the homelab
- Memory utilization
- Network throughput (inbound + outbound)
- Top 5 containers by CPU
- Disk space remaining on all volumes

I check this maybe once a day. It's not for alerting — it's for understanding trends.

#### 2. The "What Just Broke" Dashboard

Triggered by Uptime Kuma alerts. Shows:
- Last 1 hour of CPU/memory for the affected host
- Container restart events
- Disk I/O spikes
- Network errors
- Recent log entries (via Loki integration)

This is for diagnosis, not casual browsing.

#### 3. The "Capacity Planning" Dashboard

Updated weekly. Shows:
- Disk usage trends (with linear regression for "when will this fill up?")
- Memory growth over 30 days
- Network bandwidth trends
- Container image sizes (to find bloat)

This prevents the "oh crap, the NAS is 95% full" surprise.

### Prometheus Config That Works

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: 
        - '192.168.1.134:9100'  # Proxmox host
        - '192.168.1.201:9100'  # TeslaMate LXC
        - '192.168.1.202:9100'  # Media tools LXC
        - '192.168.1.165:9100'  # Mac Mini

  - job_name: 'cadvisor'
    static_configs:
      - targets:
        - '192.168.1.201:8080'
        - '192.168.1.202:8080'

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - /etc/prometheus/rules/*.yml
```

The key insight: **scrape from inside the network.** Don't expose Prometheus to the internet. Use WireGuard or Tailscale if you need external access to Grafana.

### Alert Rules That Don't Cry Wolf

```yaml
groups:
  - name: homelab
    rules:
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          
      - alert: DiskWillFillIn72Hours
        expr: predict_linear(node_filesystem_avail_bytes[6h], 72*3600) < 10737418240
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Disk {{ $labels.device }} on {{ $labels.instance }} filling fast"
          
      - alert: ContainerRestartLoop
        expr: rate(container_start_count_total[15m]) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container {{ $labels.name }} restarting frequently"
```

Notice: `predict_linear` for disk filling up. This is the difference between "reacting" and "preventing." I get alerted when a disk will fill in 72 hours, not when it's already full.

---

## Layer 3: Logs with Loki — The "Why"

Metrics tell you *that* CPU spiked. Logs tell you *which process* caused it.

### Loki Setup (Docker Compose)

```yaml
version: '3.8'
services:
  loki:
    image: grafana/loki:3.0
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki-data:/loki
    ports:
      - "3100:3100"

  promtail:
    image: grafana/promtail:3.0
    volumes:
      - ./promtail-config.yml:/etc/promtail/config.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/config.yml

volumes:
  loki-data:
```

### Promtail Config

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker
          __path__: /var/lib/docker/containers/*/*.log

  - job_name: syslog
    static_configs:
      - targets:
          - localhost
        labels:
          job: syslog
          __path__: /var/log/syslog

  - job_name: journal
    journal:
      max_age: 12h
      labels:
        job: systemd-journal
    relabel_configs:
      - source_labels: ['__journal__systemd_unit']
        target_label: 'unit'
```

### Log Queries That Save Time

In Grafana, connected to Loki:

**Find all errors from a specific container:**
```
{job="docker", container="jellyfin"} |= "error" | json
```

**Find slow database queries:**
```
{job="docker", container="postgres"} |= "duration:" |~ "duration: [0-9]{3,}"
```

**Find authentication failures (potential attack):**
```
{job="syslog"} |= "Failed password" | json
```

**Find container restart reasons:**
```
{job="docker"} |= "level=error" | json | line_format "{% raw %}{{.container_name}}{% endraw %}: {% raw %}{{.error}}{% endraw %}"
```

The power of Loki is **label-based filtering.** Instead of grep-ing through files on 5 different hosts, you query one endpoint with structured filters.

---

## Layer 4: Distributed Tracing (Optional but Cool)

If you're running microservices or complex app stacks, tracing shows you the path a request takes through your system.

For a homelab, this is mostly useful if you:
- Run multiple interconnected services (e.g., a media pipeline: Sonarr → qBittorrent → Plex)
- Debug performance issues across service boundaries
- Want to understand where latency actually comes from

I run Jaeger in a "just in case" mode. It's lightweight when not actively sampling, and invaluable when I need it.

```yaml
services:
  jaeger:
    image: jaegertracing/all-in-one:1.50
    ports:
      - "16686:16686"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

Most homelab apps don't support OpenTelemetry natively, so I use a reverse proxy with trace injection or manual instrumentation for custom scripts.

---

## Pattern: The Incident Response Workflow

Here's what actually happens when something breaks in my homelab now:

### Step 1: Uptime Kuma Detects

Uptime Kuma notices Plex is down. Sends me a Telegram message: "Plex DOWN — HTTP 502."

### Step 2: Prometheus Context

I open the Grafana "What Just Broke" dashboard. I see:
- CPU on the Plex LXC spiked to 100% 5 minutes ago
- Memory climbed steadily for 30 minutes before the spike
- Container hasn't restarted — it's still running but unresponsive

Hypothesis: Out of memory, possibly due to a large library scan.

### Step 3: Loki Confirmation

I query Loki for the Plex container logs in the last hour:
```
{job="docker", container="plex"} |= "error" | json
```

Results show: `OutOfMemoryError: Java heap space` — Plex's Java-based scanner ran out of memory during a scheduled scan.

### Step 4: Fix

- SSH into the LXC
- Restart Plex container: `docker restart plex`
- Increase container memory limit in compose file
- Re-run scan to verify
- Done in 3 minutes

### Before This Stack

- Uptime Kuma says Plex is down
- SSH into LXC
- Check `docker ps` — Plex is running
- Check `docker logs plex` — last 500 lines, no obvious error
- Check `htop` — CPU is fine, memory is fine
- Check `df -h` — disk is fine
- Restart Plex anyway
- It works, but I don't know why it broke
- Repeat tomorrow because I didn't fix the root cause

**Time saved per incident: 15-30 minutes. Root cause found: almost always.**

---

## Pattern: Proactive Monitoring

The best incident is the one you prevent. Here are the patterns I use:

### 1. Capacity Forecasting

Prometheus `predict_linear()` tells me when resources will run out:

```promql
# Disk will fill in 72 hours at current rate
predict_linear(node_filesystem_avail_bytes{mountpoint="/"}[6h], 72*3600) < 10737418240

# Memory trend over 7 days
avg_over_time(node_memory_MemAvailable_bytes[7d])
```

I review these weekly. If a trend shows the NAS filling in 3 weeks, I clean up before it becomes urgent.

### 2. Update Monitoring

I run a weekly script that checks for available updates:

```bash
#!/bin/bash
# check-updates.sh

# Docker images with updates available
docker images --format "{% raw %}{{.Repository}}{% endraw %}:{% raw %}{{.Tag}}{% endraw %}" | while read image; do
    LATEST=$(skopeo inspect docker://$image 2>/dev/null | jq -r '.Labels."org.opencontainers.image.version" // .Labels.version // "unknown"')
    CURRENT=$(docker inspect $image --format='{% raw %}{{index .Config.Labels "org.opencontainers.image.version"}}{% endraw %}' 2>/dev/null)
    if [ "$LATEST" != "$CURRENT" ] && [ "$LATEST" != "unknown" ]; then
        echo "UPDATE: $image ($CURRENT → $LATEST)"
    fi
done

# Proxmox packages
ssh root@192.168.1.134 "apt list --upgradable 2>/dev/null | wc -l" | xargs echo "Proxmox packages to update:"
```

This runs Sunday mornings and posts a summary to Telegram. I batch-update when convenient instead of reacting to security announcements.

### 3. Configuration Drift Detection

I version-control all my Docker Compose files and config. A nightly script checks for drift:

```bash
#!/bin/bash
# check-drift.sh

cd /opt/docker-stacks

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "WARNING: Uncommitted changes in docker-stacks"
    git status --short
fi

# Check running containers vs compose files
docker compose ls --quiet | while read project; do
    cd /opt/docker-stacks/$project
    if ! docker compose config -q 2>/dev/null; then
        echo "WARNING: $project compose file is invalid"
    fi
done
```

This catches "I edited a config file and forgot to commit" before it becomes "why is this different from the backup?"

---

## The Full Stack Architecture

Here's how everything connects in my homelab:

```
┌─────────────────────────────────────────────────────────┐
│                    Uptime Kuma                           │
│              (Availability + Alerts)                    │
└──────────────────┬──────────────────────────────────────┘
                   │ Telegram
                   ▼
┌─────────────────────────────────────────────────────────┐
│   Prometheus → Grafana → (Metrics + Dashboards)           │
│        ↑                                                  │
│   node_exporter, cadvisor, custom exporters               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│   Loki → Grafana → (Logs + Search)                      │
│     ↑                                                     │
│   Promtail (on each host)                                 │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│   Alertmanager → Telegram/SMS                             │
│   (Smart alerting with grouping + silencing)            │
└─────────────────────────────────────────────────────────┘
```

**Resource usage:**
- Prometheus: ~500MB RAM, light CPU
- Grafana: ~200MB RAM
- Loki: ~300MB RAM (with 7-day retention)
- Alertmanager: ~50MB RAM
- **Total: ~1GB RAM, minimal CPU**

This fits comfortably on a Raspberry Pi 4 or any LXC with 2GB RAM.

---

## What I Don't Monitor (And Why)

Not everything needs monitoring. Here's what I skip:

| Thing | Why I Skip It |
|-------|---------------|
| Individual Docker container CPU in normal state | Too noisy, cadvisor aggregate is enough |
| Network traffic per device | My router (UniFi) handles this |
| Temperature on SSDs | Smart data covers this, and modern SSDs throttle safely |
| Exact HTTP response times for every endpoint | Sample 1% with tracing instead |
| My own desktop machine | If it's down, I know — I'm sitting in front of it |
| Cloud services (Google, GitHub) | They have their own status pages; my alerts won't help |

The goal of monitoring isn't to measure everything. It's to measure the *right* things so you can act.

---

## Getting Started: The Minimal Viable Stack

If you're currently on Uptime Kuma alone and want to level up without drowning in complexity:

### Week 1: Add Prometheus + Grafana

1. Deploy Prometheus + Grafana in Docker
2. Add node_exporter to your main hosts
3. Import the "Node Exporter Full" Grafana dashboard (ID: 1860)
4. Set up ONE alert: disk space < 10%

### Week 2: Add Loki for Logs

1. Deploy Loki + Promtail
2. Add Promtail to your main Docker host
3. In Grafana, create a panel that shows logs for a specific container
4. Try querying logs when something next breaks

### Week 3: Smart Alerting

1. Add Alertmanager
2. Configure Telegram notifications
3. Set up alert grouping (so 10 container restarts = 1 message, not 10)
4. Add silence periods (e.g., don't alert for non-critical issues between 11 PM and 7 AM)

### Month 2: Custom Dashboards

1. Build the "At a Glance" dashboard described above
2. Add capacity forecasting panels
3. Create per-service dashboards (Plex, Nextcloud, etc.)

You don't need to do it all at once. Each layer adds value independently.

---

## Tools Comparison: What to Use When

| Need | Tool | Why |
|------|------|-----|
| Is it up? | Uptime Kuma | Simple, effective, good notifications |
| What's the trend? | Prometheus + Grafana | Time-series, great for pattern recognition |
| What happened? | Loki | Label-based log search, Grafana integration |
| Complex multi-service debug | Jaeger | Distributed tracing (advanced) |
| Network monitoring | UniFi / ntopng | Router-level visibility |
| Security monitoring | Wazuh / CrowdSec | IDS/IPS, not just performance |
| Everything in one place | Datadog / New Relic | Too expensive for homelab, but reference architecture |

For a homelab, the "Prometheus + Grafana + Loki" stack is the sweet spot. It's what the cloud-native world standardized on, it runs on minimal hardware, and it's all open-source.

---

## Common Mistakes to Avoid

1. **Monitoring too many things** — You'll ignore alerts. Start with 5 critical metrics.
2. **Alerting on thresholds without duration** — CPU spikes for 10 seconds don't matter. Use `for: 5m`.
3. **No alert grouping** — One host reboot = 50 alerts = alert fatigue.
4. **No runbook** — When you get an alert, you shouldn't have to think. Document: "If X, do Y."
5. **Forgetting to monitor the monitors** — If Prometheus goes down, you're blind. Uptime Kuma should monitor Prometheus.
6. **Keeping logs forever** — Set retention. Loki with 7 days is usually enough for a homelab.
7. **Not testing alerts** — Use `amtool` to send test alerts. Make sure Telegram/SMS actually works.

---

## The "Runbook" Pattern

For every alert I have, I keep a one-page runbook in a Git repo:

```markdown
# Alert: Plex Down

## Check
1. Is the LXC responding? `ping 192.168.1.203`
2. Is Docker running? `docker ps`
3. Check logs: `docker logs plex --tail 100`

## Common Causes
- Out of memory → increase limit in compose, restart
- Database locked → restart container, check Nextcloud DB
- Library scan running → wait or throttle scan

## Fix
```bash
ssh root@192.168.1.203
docker restart plex
```

## Escalation
If restart doesn't fix: check LXC resources, check NFS mounts
```

This seems obvious, but at 2 AM when you're half-asleep, having a checklist is invaluable.

---

## Conclusion

Uptime Kuma is the gateway drug of homelab monitoring. It gets you in the door. But the real value comes from the layers above: metrics that show trends, logs that explain failures, and workflows that turn alerts into fixes.

Start small. Add Prometheus this weekend. Add Loki next month. Build one dashboard at a time. The goal isn't to have the most comprehensive monitoring stack — it's to **never again spend an hour diagnosing a problem that should have taken five minutes.**

The best compliment your monitoring stack can receive is silence: alerts that are rare, actionable, and always lead to a fix. Everything else is just noise.

---

*Last updated: June 21, 2026. My monitoring stack runs on a Mac Mini M4 with 16GB RAM, alongside Plex, Home Assistant, and a dozen other services. Total monitoring overhead: <5% CPU, ~1GB RAM.*